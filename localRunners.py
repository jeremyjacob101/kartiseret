from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
from rich.progress import Progress, ProgressColumn, SpinnerColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.console import Console, Group
from rich.live import Live
from rich.theme import Theme
from rich.table import Column
import time, os
from supabase import create_client
from dataclasses import dataclass
from typing import Callable, Any, Optional

from localRegistry import REGISTRY, DATAFLOW_REGISTRY
from utils.logger import artifactPrinting

runningGithubActions = os.getenv("GITHUB_ACTIONS") == "true"


@dataclass
class RunResult:
    name: str
    secs: float
    ok: bool


@dataclass(frozen=True)
class KindSpec:
    registry: dict[str, list[type]]
    make_instance: Callable[[type, str], Any]  # (cls, key) -> instance
    run_instance: Callable[[Any], None]  # instance -> None
    cleanup: Callable[[Any], None]  # instance -> None
    count_label: str
    mode: str  # "parallel" | "sequential"
    total_strategy: str  # "max" | "sum"
    overall_task_name: str
    fetch_avg: Callable[[list[type]], dict[str, float]]
    get_item_name: Callable[[type], str]


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


def _calc_total_estimated(items, get_item_est, strategy: str) -> float:
    ests = [float(get_item_est(item)) for item in items] if items else []
    if not ests:
        return 0.0
    if strategy == "max":
        return float(max(ests))
    if strategy == "sum":
        return float(sum(ests))
    raise ValueError(f"Unknown total strategy: {strategy}")


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


KIND_SPECS: dict[str, KindSpec] = {
    "cinema": KindSpec(registry=REGISTRY, make_instance=lambda cls, key: cls(cinema_type=key, supabase_table_name=key), run_instance=lambda inst: inst.scrape(), cleanup=lambda instance: (instance.driver.quit() if instance and getattr(instance, "driver", None) else None), count_label="Threads", mode="parallel", total_strategy="max", overall_task_name="overall", fetch_avg=_fetch_avg_times_for_classes, get_item_name=lambda cls: getattr(cls, "CINEMA_NAME", cls.__name__)),
    "dataflow": KindSpec(registry=DATAFLOW_REGISTRY, make_instance=lambda cls, key: cls(), run_instance=lambda inst: inst.dataRun(), cleanup=lambda instance: None, count_label="Dataflows", mode="sequential", total_strategy="sum", overall_task_name="dataflows", fetch_avg=_fetch_avg_times_for_dataflows, get_item_name=lambda cls: cls.__name__),
}


def _finalize_overall_bar(overall, overall_task_id: int, ok: bool, completed: float, elapsed_secs: float, done: int):
    overall_color = "green" if ok else "red"

    task = overall.tasks[overall_task_id]
    task.finished_style = overall_color
    task.complete_style = overall_color
    task.pulse_style = overall_color

    overall.update(overall_task_id, completed=completed, elapsed=_hms(elapsed_secs), eta=_hms(0), done=done, bar_color=overall_color, elapsed_color=overall_color, eta_color=overall_color)


def _update_task_status(status, tid: int, name: str, est: float, r: RunResult):
    color = "green" if r.ok else "red"
    status.update(tid, description=f"[{color}]{name}[/{color}]", time=f"[{color}]{_hms(r.secs)}[/{color}]", completed=est, bar_color=color, **({} if r.ok else {"failed": True}))


def _update_overall(overall, task_id: int, now: float, started_at: float, completed: float, done: int):
    total = float(overall.tasks[task_id].total or 0.0)
    completed = min(float(completed), total)
    eta_secs = max(0.0, total - completed)
    elapsed_secs = now - started_at

    overall.update(task_id, completed=completed, elapsed=_hms(elapsed_secs), eta=_hms(eta_secs), done=done)
    return total, completed, elapsed_secs, eta_secs


def _run_rich(overall, status, overall_task_id: int, items, get_item_name, get_item_est, run_one, mode: str, overall_started_at: float, refresh_sleep: float = 0.2):
    results, status_task_id_by_item, est_by_item = [], {}, {}

    for item in items:
        name = get_item_name(item)
        est = float(get_item_est(item))
        tid = status.add_task(f"[yellow]{name}[/yellow]", total=est, completed=0.0, time=f"[yellow]       [/yellow]", bar_color="#f266e0")
        status_task_id_by_item[item] = tid
        est_by_item[item] = est

    if mode == "parallel":
        start_by_item = {item: time.time() for item in items}

        with ThreadPoolExecutor(max_workers=max(1, len(items))) as ex:
            future_to_item = {ex.submit(run_one, item): item for item in items}
            pending = set(future_to_item.keys())
            done_set = set()
            done_count = 0
            max_elapsed_seen = 0.0

            while True:
                now = time.time()

                # overall progress = max elapsed of any still-running task (capped at total)
                max_elapsed = 0.0
                for item in items:
                    if item in done_set:
                        continue
                    elapsed = now - start_by_item[item]
                    if elapsed > max_elapsed:
                        max_elapsed = elapsed

                max_elapsed_seen = max(max_elapsed_seen, max_elapsed)
                overall_total, overall_completed, overall_elapsed, eta_secs = _update_overall(overall, overall_task_id, now, overall_started_at, max_elapsed_seen, done_count)

                # Update each per-task bar by elapsed time
                for item in items:
                    if item in done_set:
                        continue
                    tid = status_task_id_by_item[item]
                    est = est_by_item[item]
                    elapsed = now - start_by_item[item]
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

                    tid = status_task_id_by_item[item]
                    est = est_by_item[item]
                    name = get_item_name(item)

                    _update_task_status(status, tid, name, est, r)

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
                tid = status_task_id_by_item[item]
                est = est_by_item[item]
                name = get_item_name(item)

                start = time.time()
                fut = ex.submit(run_one, item)

                while True:
                    now = time.time()
                    elapsed = now - start

                    status.update(tid, completed=min(elapsed, est))
                    overall_total, overall_completed, overall_elapsed, eta_secs = _update_overall(overall, overall_task_id, now, overall_started_at, sum_est_done + min(elapsed, est), done_count)

                    if fut.done():
                        break

                    time.sleep(refresh_sleep)

                r = fut.result()
                results.append(r)

                done_count += 1
                sum_est_done += est
                all_ok = all_ok and r.ok
                now = time.time()

                _update_task_status(status, tid, name, est, r)
                _update_overall(overall, overall_task_id, now, overall_started_at, sum_est_done, done_count)

        final_elapsed = time.time() - overall_started_at
        _finalize_overall_bar(overall, overall_task_id, all_ok, float(overall.tasks[overall_task_id].total or 0.0), final_elapsed, done_count)
        return results


def runGroup(kind: str, key: str) -> Optional[list[RunResult]]:
    spec = KIND_SPECS.get(kind)
    if spec is None:
        raise ValueError(f"Unknown kind: {kind}")

    classes = spec.registry.get(key, [])
    if not classes:
        return None

    def run_one(cls: type) -> RunResult:
        t0, instance, ok = time.time(), None, True
        try:
            instance = spec.make_instance(cls, key)
            spec.run_instance(instance)
        except Exception:
            ok = False
            artifactPrinting(instance)
        finally:
            spec.cleanup(instance)

        return RunResult(name=cls.__name__, secs=time.time() - t0, ok=ok)

    if runningGithubActions:
        results: list[RunResult] = []
        if spec.mode == "parallel":
            with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
                futures = [ex.submit(run_one, cls) for cls in classes]
                for fut in as_completed(futures):
                    results.append(fut.result())  # RunResult
        else:
            for cls in classes:
                results.append(run_one(cls))  # RunResult

        print("\n--------------------\n", flush=True)
        for result in results:
            minutes, seconds = divmod(int(result.secs), 60)
            print(f"{result.name}: {minutes:02d}m{seconds:02d}s", flush=True)
        print("\n--------------------\n", flush=True)

    if not runningGithubActions:
        avg_by_name = spec.fetch_avg(classes)
        get_item_est = lambda item: float(avg_by_name.get(item.__name__, 60.0))

        console = Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))
        overall = Progress(TextColumn("[bold {task.fields[elapsed_color]}]{task.fields[elapsed]}[/bold {task.fields[elapsed_color]}]"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("[bold {task.fields[eta_color]}]{task.fields[eta]}[/bold {task.fields[eta_color]}]"), TextColumn("[bold green]{task.fields[done]}/{task.fields[total_count]} " + spec.count_label + "[/bold green] " + "[bold #66d6f2]{task.fields[group_label]}[/bold #66d6f2]"), SpinnerColumn(style="bold #f266e0"), console=console, refresh_per_second=6)
        status = Progress(TextColumn("{task.fields[time]}"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("{task.description}"), console=console, refresh_per_second=6)
        with Live(Group(overall, status), console=console, refresh_per_second=6):
            total_estimated = _calc_total_estimated(classes, get_item_est, spec.total_strategy)
            overall_task_id = overall.add_task(spec.overall_task_name, total=total_estimated, elapsed=_hms(0), eta=_hms(total_estimated), done=0, total_count=len(classes), group_label=key, bar_color="#f266e0", elapsed_color="#9c27f5", eta_color="orange1")
            overall_started_at = time.time()
            _run_rich(overall, status, overall_task_id, classes, spec.get_item_name, get_item_est, run_one, spec.mode, overall_started_at)
