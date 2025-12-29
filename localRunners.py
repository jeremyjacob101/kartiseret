from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from rich.progress import Progress, ProgressColumn, SpinnerColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.console import Console, Group
from rich.live import Live
from rich.theme import Theme
from rich.table import Column
import time, os

from localRegistry import REGISTRY, DATAFLOW_REGISTRY
from utils.logger import artifactPrinting

from supabase import create_client

runningGithubActions = os.getenv("GITHUB_ACTIONS") == "true"

from dataclasses import dataclass


@dataclass
class RunResult:
    name: str
    secs: float
    ok: bool


class PerTaskBarColumn(ProgressColumn):
    def __init__(self, bar_width=20, default_bar="#f266e0", default_back="grey23"):
        super().__init__(Column())
        self.bar_width = bar_width
        self.default_bar = default_bar
        self.default_back = default_back

    def render(self, task):
        bar_color = task.fields.get("bar_color", self.default_bar)
        back_color = task.fields.get("bar_back", self.default_back)
        failed = task.fields.get("failed", False)

        if failed:
            return ProgressBar(total=max(0, task.total) if task.total is not None else None, completed=min(task.completed, task.total or 0), width=self.bar_width, pulse=False, style=back_color, complete_style="red", finished_style="red", pulse_style="red")
        return ProgressBar(total=max(0, task.total) if task.total is not None else None, completed=max(0, task.completed), width=self.bar_width, pulse=not task.started, animation_time=task.get_time(), style=back_color, complete_style=bar_color, finished_style=bar_color, pulse_style=bar_color)


def _hms(secs: float) -> str:
    secs = int(secs)
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def _print_timings(results):
    print("\n--------------------\n", flush=True)
    for result in results:
        minutes, seconds = divmod(int(result.secs), 60)
        print(f"{result.name}: {minutes:02d}m{seconds:02d}s", flush=True)
    print("\n--------------------\n", flush=True)


def _fetch_avg_times_for_dataflows(classes) -> dict[str, float]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    sb = create_client(url, key)

    class_names = [cls.__name__ for cls in classes]
    FALLBACK = 60.0

    by_name: dict[str, float] = {}

    try:
        resp = sb.table("utilAvgDataTime").select("data_type,avg_time").in_("data_type", class_names).execute()
        rows = resp.data or []
        for r in rows:
            k = r.get("data_type")
            if not k:
                continue
            try:
                v = float(r.get("avg_time") or 0.0)
            except (TypeError, ValueError):
                v = 0.0
            if v > 0:
                by_name[k] = v
    except Exception:
        by_name = {}

    return {cls.__name__: (by_name.get(cls.__name__) or FALLBACK) for cls in classes}


def _fetch_avg_times_for_classes(classes) -> dict[str, float]:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    sb = create_client(url, key)
    class_names = [cls.__name__ for cls in classes]
    resp = sb.table("utilAvgScrapeTime").select("cinema_name,avg_time").in_("cinema_name", class_names).execute()
    rows = resp.data or []
    by_name = {r["cinema_name"]: float(r.get("avg_time") or 0.0) for r in rows}

    FALLBACK, out = 60.0, {}
    for cls in classes:
        v = by_name.get(cls.__name__, 0.0)
        out[cls.__name__] = v if v and v > 0 else FALLBACK
    return out


def _finalize_overall_bar(overall, overall_task_id: int, ok: bool, completed: float, elapsed_secs: float, done: int):
    overall_color = "green" if ok else "red"

    task = overall.tasks[overall_task_id]
    task.finished_style = overall_color
    task.complete_style = overall_color
    task.pulse_style = overall_color

    overall.update(overall_task_id, completed=completed, elapsed=_hms(elapsed_secs), eta=_hms(0), done=done, bar_color=overall_color, elapsed_color=overall_color, eta_color=overall_color)


def _run_in_threadpool(classes, run_one):
    results = []
    with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
        futures = [ex.submit(run_one, cls) for cls in classes]
        for fut in as_completed(futures):
            results.append(fut.result())  # RunResult
    return results


def _run_sequential(classes, run_one):
    results = []
    for cls in classes:
        results.append(run_one(cls))  # RunResult
    return results


def _make_rich_ui(count_label: str, key_field: str):
    console = Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))
    summary = "[bold green]{task.fields[done]}/{task.fields[total_count]} " + count_label + "[/bold green] " + "[bold #66d6f2]{task.fields[" + key_field + "]}[/bold #66d6f2]"
    overall = Progress(TextColumn("[bold {task.fields[elapsed_color]}]{task.fields[elapsed]}[/bold {task.fields[elapsed_color]}]"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("[bold {task.fields[eta_color]}]{task.fields[eta]}[/bold {task.fields[eta_color]}]"), TextColumn(summary), SpinnerColumn(style="bold #f266e0"), console=console, refresh_per_second=6)
    status = Progress(TextColumn("{task.fields[time]}"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("{task.description}"), console=console, refresh_per_second=6)
    return console, overall, status


def _run_rich(overall, status, overall_task_id: int, items, get_item_name, get_item_est, run_one, mode: str, overall_started_at: float, refresh_sleep: float = 0.2):
    results = []
    status_task_id_by_key = {}
    est_by_key = {}

    for item in items:
        key = item
        name = get_item_name(item)
        est = float(get_item_est(item))
        tid = status.add_task(f"[yellow]{name}[/yellow]", total=est, completed=0.0, time=f"[yellow]       [/yellow]", bar_color="#f266e0")
        status_task_id_by_key[key] = tid
        est_by_key[key] = est

    if mode == "parallel":
        start_by_key = {item: time.time() for item in items}

        with ThreadPoolExecutor(max_workers=max(1, len(items))) as ex:
            future_to_item = {ex.submit(run_one, item): item for item in items}
            pending = set(future_to_item.keys())
            done_set = set()
            done_count = 0

            while True:
                now = time.time()

                # overall progress = max elapsed of any still-running task (capped at total)
                max_elapsed = 0.0
                for item in items:
                    if item in done_set:
                        continue
                    elapsed = now - start_by_key[item]
                    if elapsed > max_elapsed:
                        max_elapsed = elapsed

                overall_total = float(overall.tasks[overall_task_id].total or 0.0)
                overall_completed = min(max_elapsed, overall_total)
                eta_secs = max(0.0, overall_total - overall_completed)
                overall_elapsed = now - overall_started_at

                # Update each per-task bar by elapsed time
                for item in items:
                    if item in done_set:
                        continue
                    tid = status_task_id_by_key[item]
                    est = est_by_key[item]
                    elapsed = now - start_by_key[item]
                    status.update(tid, completed=min(elapsed, est))

                # Collect finished (only touch futures that are done)
                done_futs, _ = wait(pending, timeout=0, return_when=FIRST_COMPLETED)
                for fut in done_futs:
                    item = future_to_item[fut]
                    if item in done_set:
                        pending.discard(fut)
                        continue

                    r = fut.result()  # RunResult
                    results.append(r)

                    done_set.add(item)
                    done_count += 1
                    pending.discard(fut)

                    tid = status_task_id_by_key[item]
                    est = est_by_key[item]
                    name = get_item_name(item)

                    status.update(tid, description=f"[{'green' if r.ok else 'red'}]{name}[/{'green' if r.ok else 'red'}]", time=f"[{'green' if r.ok else 'red'}]{_hms(r.secs)}[/{'green' if r.ok else 'red'}]", completed=est, bar_color=("green" if r.ok else "red"), **({} if r.ok else {"failed": True}))

                overall.update(overall_task_id, completed=overall_completed, elapsed=_hms(overall_elapsed), eta=_hms(eta_secs), done=done_count)

                if not pending:
                    all_ok = all(r.ok for r in results)
                    _finalize_overall_bar(overall, overall_task_id, all_ok, float(overall.tasks[overall_task_id].total or 0.0), overall_elapsed, done_count)
                    return results

                time.sleep(refresh_sleep)

    else:  # sequential
        done_count = 0
        sum_est_done = 0.0
        all_ok = True

        with ThreadPoolExecutor(max_workers=1) as ex:
            for item in items:
                tid = status_task_id_by_key[item]
                est = est_by_key[item]
                name = get_item_name(item)

                start = time.time()
                fut = ex.submit(run_one, item)

                while True:
                    now = time.time()
                    elapsed = now - start

                    status.update(tid, completed=min(elapsed, est))

                    overall_total = float(overall.tasks[overall_task_id].total or 0.0)
                    overall_completed = min(sum_est_done + min(elapsed, est), overall_total)
                    eta_secs = max(0.0, overall_total - overall_completed)
                    overall_elapsed = now - overall_started_at

                    overall.update(overall_task_id, completed=overall_completed, elapsed=_hms(overall_elapsed), eta=_hms(eta_secs), done=done_count)

                    if fut.done():
                        break

                    time.sleep(refresh_sleep)

                r = fut.result()
                results.append(r)

                done_count += 1
                sum_est_done += est
                all_ok = all_ok and r.ok

                status.update(tid, description=f"[{'green' if r.ok else 'red'}]{name}[/{'green' if r.ok else 'red'}]", time=f"[{'green' if r.ok else 'red'}]{_hms(r.secs)}[/{'green' if r.ok else 'red'}]", completed=est, bar_color=("green" if r.ok else "red"), **({} if r.ok else {"failed": True}))

                now = time.time()
                overall_elapsed = now - overall_started_at
                overall_completed = min(sum_est_done, float(overall.tasks[overall_task_id].total or 0.0))
                eta_secs = max(0.0, float(overall.tasks[overall_task_id].total or 0.0) - overall_completed)

                overall.update(overall_task_id, completed=overall_completed, elapsed=_hms(overall_elapsed), eta=_hms(eta_secs), done=done_count)

        final_elapsed = time.time() - overall_started_at
        _finalize_overall_bar(overall, overall_task_id, all_ok, float(overall.tasks[overall_task_id].total or 0.0), final_elapsed, done_count)
        return results


def _runCinemaType_rich(type: str, classes, run_one):
    avg_by_classname = _fetch_avg_times_for_classes(classes)
    console, overall, status = _make_rich_ui("Threads", "cinema_type")

    with Live(Group(overall, status), console=console, refresh_per_second=6):
        total_estimated = max(avg_by_classname.values()) if avg_by_classname else 0.0
        overall_task = overall.add_task("overall", total=total_estimated, elapsed=_hms(0), eta=_hms(total_estimated), done=0, total_count=len(classes), cinema_type=type, bar_color="#f266e0", elapsed_color="#9c27f5", eta_color="orange1")
        overall_started_at = time.time()
        _run_rich(overall, status, overall_task, classes, lambda cls: getattr(cls, "CINEMA_NAME", cls.__name__), lambda cls: float(avg_by_classname.get(cls.__name__, 60.0)), run_one, "parallel", overall_started_at)


def _runDataflows_rich(flow_key, classes, run_one_dataflow):
    avg_by_classname = _fetch_avg_times_for_dataflows(classes)
    console, overall, status = _make_rich_ui("Dataflows", "flow_key")

    with Live(Group(overall, status), console=console, refresh_per_second=6):
        total_estimated = float(sum(avg_by_classname.get(cls.__name__, 60.0) for cls in classes))
        overall_task = overall.add_task("dataflows", total=total_estimated, completed=0.0, elapsed=_hms(0), eta=_hms(total_estimated), done=0, total_count=len(classes), flow_key=flow_key, bar_color="#f266e0", elapsed_color="#9c27f5", eta_color="orange1")
        overall_started_at = time.time()
        _run_rich(overall, status, overall_task, classes, lambda cls: cls.__name__, lambda cls: float(avg_by_classname.get(cls.__name__, 60.0)), run_one_dataflow, "sequential", overall_started_at)


def runCinemaType(type: str):
    classes = REGISTRY.get(type, [])
    if not classes:
        return

    def run_one(cls):
        t0, instance, ok = time.time(), None, True
        try:
            instance = cls(cinema_type=type, supabase_table_name=type)
            instance.scrape()
        except Exception as e:
            ok = False
            artifactPrinting(instance)
        finally:
            if instance and getattr(instance, "driver", None):
                instance.driver.quit()
        return RunResult(name=cls.__name__, secs=time.time() - t0, ok=ok)

    if runningGithubActions:
        results = _run_in_threadpool(classes, run_one)
        _print_timings(results)
    else:
        _runCinemaType_rich(type, classes, run_one)


def runDataflows(flow_key: str):
    classes = DATAFLOW_REGISTRY.get(flow_key, [])
    if not classes:
        return

    def run_one_dataflow(cls):
        t0, instance, ok = time.time(), None, True
        try:
            instance = cls()
            instance.dataRun()
        except Exception:
            ok = False
            artifactPrinting(instance)
        return RunResult(name=cls.__name__, secs=time.time() - t0, ok=ok)

    if runningGithubActions:
        results = _run_sequential(classes, run_one_dataflow)
        _print_timings(results)
    else:
        _runDataflows_rich(flow_key, classes, run_one_dataflow)
