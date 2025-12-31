from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from rich.progress import Progress, ProgressColumn, SpinnerColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.console import Console, Group
from rich.table import Column
from rich.theme import Theme
from rich.live import Live

from dataclasses import dataclass
import time


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
    hours, remainder = divmod(secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def _finalize_overall_bar(overall, overall_task_id: int, ok: bool, completed: float, elapsed_secs: float, done: int):
    overall_color = "green" if ok else "red"
    task = overall.tasks[overall_task_id]
    task.finished_style = overall_color
    task.complete_style = overall_color
    task.pulse_style = overall_color
    overall.update(overall_task_id, completed=completed, elapsed=_hms(elapsed_secs), eta=_hms(0), done=done, bar_color=overall_color, elapsed_color=overall_color, eta_color=overall_color)


def _update_task_status(status, task_id: int, name: str, estimated_secs: float, result: RunResult):
    color = "green" if result.ok else "red"
    status.update(task_id, description=f"[{color}]{name}[/{color}]", time=f"[{color}]{_hms(result.secs)}[/{color}]", completed=estimated_secs, bar_color=color, **({} if result.ok else {"failed": True}))


def _update_overall(overall, task_id: int, now: float, started_at: float, completed: float, done: int):
    total = float(overall.tasks[task_id].total or 0.0)
    completed = min(float(completed), total)
    eta_secs = max(0.0, total - completed)
    elapsed_secs = now - started_at
    overall.update(task_id, completed=completed, elapsed=_hms(elapsed_secs), eta=_hms(eta_secs), done=done)


def run_rich_ui(spec, key: str, classes, get_item_est, run_one):
    console = Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))
    overall = Progress(TextColumn("[bold {task.fields[elapsed_color]}]{task.fields[elapsed]}[/bold {task.fields[elapsed_color]}]"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("[bold {task.fields[eta_color]}]{task.fields[eta]}[/bold {task.fields[eta_color]}]"), TextColumn("[bold green]{task.fields[done]}/{task.fields[total_count]} " + spec.count_label + "[/bold green] " + "[bold #66d6f2]{task.fields[group_label]}[/bold #66d6f2]"), SpinnerColumn(style="bold #f266e0"), console=console, refresh_per_second=6)
    status = Progress(TextColumn("{task.fields[time]}"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("{task.description}"), console=console, refresh_per_second=6)

    with Live(Group(overall, status), console=console, refresh_per_second=6):
        results, status_task_id_by_item, est_by_item = [], {}, {}

        all_estimated_times = [float(get_item_est(item)) for item in classes] if classes else []
        if not all_estimated_times:
            total_estimated = 0.0
        elif spec.total_strategy == "max":
            total_estimated = float(max(all_estimated_times))
        else:  # "sum"
            total_estimated = float(sum(all_estimated_times))

        overall_task_id = overall.add_task(spec.overall_task_name, total=total_estimated, elapsed=_hms(0), eta=_hms(total_estimated), done=0, total_count=len(classes), group_label=key, bar_color="#f266e0", elapsed_color="#9c27f5", eta_color="orange1")
        overall_started_at = time.time()

        for item in classes:
            name = spec.get_item_name(item)
            est = float(get_item_est(item))
            task_id = status.add_task(f"[yellow]{name}[/yellow]", total=est, completed=0.0, time=f"[yellow]       [/yellow]", bar_color="#f266e0")
            status_task_id_by_item[item] = task_id
            est_by_item[item] = est

        if spec.mode == "parallel":
            if not classes:
                _finalize_overall_bar(overall, overall_task_id, True, float(overall.tasks[overall_task_id].total or 0.0), time.time() - overall_started_at, 0)
                return

            start_by_item = {item: time.time() for item in classes}

            with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
                future_to_item = {ex.submit(run_one, item): item for item in classes}
                pending = set(future_to_item.keys())
                done_set = set()
                done_count = 0
                max_elapsed_seen = 0.0

                while pending:
                    now = time.time()

                    # overall progress = max elapsed of any still-running task (capped at total)
                    max_elapsed = 0.0
                    for item in classes:
                        if item in done_set:
                            continue
                        elapsed = now - start_by_item[item]
                        if elapsed > max_elapsed:
                            max_elapsed = elapsed

                    max_elapsed_seen = max(max_elapsed_seen, max_elapsed)
                    _update_overall(overall, overall_task_id, now, overall_started_at, max_elapsed_seen, done_count)

                    # Update each per-task bar by elapsed time
                    for item in classes:
                        if item in done_set:
                            continue
                        task_id = status_task_id_by_item[item]
                        est = est_by_item[item]
                        elapsed = now - start_by_item[item]
                        status.update(task_id, completed=min(elapsed, est))

                    # Collect finished (only touch futures that are done)
                    done_futures, _ = wait(pending, timeout=0, return_when=FIRST_COMPLETED)
                    for future in done_futures:
                        item = future_to_item[future]
                        if item in done_set:
                            pending.discard(future)
                            continue

                        result = future.result()  # RunResult
                        results.append(result)

                        done_set.add(item)
                        done_count += 1
                        pending.discard(future)

                        task_id = status_task_id_by_item[item]
                        est = est_by_item[item]
                        name = spec.get_item_name(item)

                        _update_task_status(status, task_id, name, est, result)

                    time.sleep(0.2)

                all_ok = all(result.ok for result in results)
                final_elapsed = time.time() - overall_started_at
                _finalize_overall_bar(overall, overall_task_id, all_ok, float(overall.tasks[overall_task_id].total or 0.0), final_elapsed, done_count)

        else:  # sequential
            done_count, sum_est_done, all_ok = 0, 0.0, True

            with ThreadPoolExecutor(max_workers=1) as ex:
                for item in classes:
                    task_id = status_task_id_by_item[item]
                    eta_of_item = est_by_item[item]
                    name = spec.get_item_name(item)

                    start = time.time()
                    future = ex.submit(run_one, item)

                    while True:
                        now = time.time()
                        elapsed = now - start

                        status.update(task_id, completed=min(elapsed, eta_of_item))
                        _update_overall(overall, overall_task_id, now, overall_started_at, sum_est_done + min(elapsed, eta_of_item), done_count)

                        if future.done():
                            break

                        time.sleep(0.2)

                    result = future.result()
                    results.append(result)

                    done_count += 1
                    sum_est_done += eta_of_item
                    all_ok = all_ok and result.ok
                    now = time.time()

                    _update_task_status(status, task_id, name, eta_of_item, result)
                    _update_overall(overall, overall_task_id, now, overall_started_at, sum_est_done, done_count)

            final_elapsed = time.time() - overall_started_at
            _finalize_overall_bar(overall, overall_task_id, all_ok, float(overall.tasks[overall_task_id].total or 0.0), final_elapsed, done_count)
