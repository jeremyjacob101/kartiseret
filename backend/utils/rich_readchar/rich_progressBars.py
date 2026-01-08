from __future__ import annotations
from typing import Any, Callable, Dict, Iterable, List, Optional, Set
from rich.progress import Progress, ProgressColumn, SpinnerColumn, TextColumn
from rich.progress_bar import ProgressBar
from rich.console import Console, Group, RenderableType
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
    attempts: int = 1


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

        total = max(0, task.total) if task.total is not None else None
        completed = max(0, task.completed)

        if failed:
            return ProgressBar(total=total, completed=min(completed, task.total or 0) if task.total is not None else completed, width=self.bar_width, pulse=False, style=back_color, complete_style="red", finished_style="red", pulse_style="red")
        return ProgressBar(total=total, completed=completed, width=self.bar_width, pulse=False, style=back_color, complete_style=bar_color, finished_style=bar_color)


def _label(attempt: int, name: str) -> str:
    return f"({attempt}) {name}"


def _hms(secs: float) -> str:
    secs = int(secs)
    hours, remainder = divmod(secs, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"


def _finalize_overall_bar(overall: Progress, overall_task_id: int, ok: bool, completed: float, elapsed_secs: float, done: int):
    overall_color = "green" if ok else "red"
    task = overall.tasks[overall_task_id]
    task.finished_style = overall_color
    task.complete_style = overall_color
    task.pulse_style = overall_color
    overall.update(overall_task_id, completed=completed, elapsed=_hms(elapsed_secs), eta=_hms(0), done=done, bar_color=overall_color, elapsed_color=overall_color, eta_color=overall_color)


def _update_task_status(status: Progress, task_id: int, name: str, attempt: int, estimated_secs: float, result: RunResult):
    color = "green" if result.ok else "red"
    status.update(task_id, description=f"[{color}]{_label(attempt, name)}[/{color}]", time=f"[{color}]{_hms(result.secs)}[/{color}]", completed=estimated_secs, bar_color=color, **({} if result.ok else {"failed": True}))


def _update_overall(overall: Progress, task_id: int, now: float, started_at: float, completed: float, done: int, eta_secs_override: Optional[float] = None):
    total = float(overall.tasks[task_id].total or 0.0)
    completed = min(float(completed), total)
    eta_secs = max(0.0, (total - completed) if eta_secs_override is None else float(eta_secs_override))
    elapsed_secs = now - started_at
    overall.update(task_id, completed=completed, elapsed=_hms(elapsed_secs), eta=_hms(eta_secs), done=done)


class RichRunUI:
    def __init__(self, spec: Any, key: str, items: Iterable[Any], get_item_est: Callable[[Any], float], refresh_per_second: int = 6, *, use_live: bool = True, console: Optional[Console] = None):
        self.spec = spec
        self.key = key
        self.items: List[Any] = list(items)
        self.get_item_est = get_item_est
        self.refresh_per_second = refresh_per_second
        self.use_live = bool(use_live)

        self.attempt_by_item: Dict[Any, int] = {item: 1 for item in self.items}
        self.est_by_item: Dict[Any, float] = {item: float(get_item_est(item)) for item in self.items}

        all_estimated = list(self.est_by_item.values())
        if not all_estimated:
            total_estimated = 0.0
        elif spec.total_strategy == "max":
            total_estimated = float(max(all_estimated))
        else:  # "sum"
            total_estimated = float(sum(all_estimated))

        self.console = console or Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))

        self.overall = Progress(TextColumn("[bold {task.fields[elapsed_color]}]{task.fields[elapsed]}[/bold {task.fields[elapsed_color]}]"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("[bold {task.fields[eta_color]}]{task.fields[eta]}[/bold {task.fields[eta_color]}]"), TextColumn("[bold green]{task.fields[done]}/{task.fields[total_count]} " + spec.count_label + "[/bold green] " + "[bold #66d6f2]{task.fields[group_label]}[/bold #66d6f2]", table_column=Column(ratio=1, overflow="ellipsis", no_wrap=True)), SpinnerColumn(style="bold #f266e0"), console=self.console, refresh_per_second=refresh_per_second)
        self.status = Progress(TextColumn("{task.fields[time]}"), PerTaskBarColumn(bar_width=20, default_bar="#f266e0"), TextColumn("{task.description}"), console=self.console, refresh_per_second=refresh_per_second)

        self.overall_task_id = self.overall.add_task(spec.overall_task_name, total=total_estimated, elapsed=_hms(0), eta=_hms(total_estimated), done=0, total_count=len(self.items), group_label=key, bar_color="#f266e0", elapsed_color="#9c27f5", eta_color="orange1")

        self.status_task_id_by_item: Dict[Any, int] = {}
        for item in self.items:
            name = spec.get_item_name(item)
            est = self.est_by_item[item]
            attempt = self.attempt_by_item[item]
            task_id = self.status.add_task(f"[yellow]{_label(attempt, name)}[/yellow]", total=est, completed=0.0, time=f"[yellow]       [/yellow]", bar_color="#f266e0", attempt=attempt, failed=False, start=False)
            self.status_task_id_by_item[item] = task_id

        self._live: Optional[Live] = None
        if self.use_live:
            self._live = Live(self.renderable, console=self.console, refresh_per_second=refresh_per_second)

        self._overall_started_at: Optional[float] = None
        self._start_by_item: Dict[Any, float] = {}
        self._done: Set[Any] = set()
        self._results: List[RunResult] = []

    @property
    def renderable(self) -> RenderableType:
        return Group(self.overall, self.status)

    def __enter__(self) -> "RichRunUI":
        if self._live is not None:
            self._live.__enter__()
        self._overall_started_at = time.time()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._live is not None:
            self._live.__exit__(exc_type, exc, tb)

    @property
    def overall_started_at(self) -> float:
        return float(self._overall_started_at or time.time())

    def start_item(self, item: Any, attempt: int = 1, started_at: Optional[float] = None) -> None:
        started_at = float(started_at if started_at is not None else time.time())
        attempt = int(attempt)

        self.attempt_by_item[item] = attempt
        self._start_by_item[item] = started_at

        task_id = self.status_task_id_by_item[item]
        self.status.start_task(task_id)
        name = self.spec.get_item_name(item)

        self.status.update(task_id, description=f"[yellow]{_label(attempt, name)}[/yellow]", completed=0.0, time=f"[yellow]       [/yellow]", bar_color="#f266e0", failed=False, attempt=attempt)
        self.tick(now=started_at)

    def retry_item(self, item: Any, attempt: int, started_at: Optional[float] = None) -> None:
        started_at = float(started_at if started_at is not None else time.time())
        attempt = int(attempt)

        # If we somehow get duplicate signals, ignore going backwards
        prev = int(self.attempt_by_item.get(item, 1))
        if attempt <= prev:
            return

        self.attempt_by_item[item] = attempt
        self._start_by_item[item] = started_at

        task_id = self.status_task_id_by_item[item]
        self.status.start_task(task_id)
        name = self.spec.get_item_name(item)

        self.status.update(task_id, description=f"[yellow]{_label(attempt, name)}[/yellow]", completed=0.0, time=f"[yellow]       [/yellow]", bar_color="#f266e0", failed=False, attempt=attempt)
        self.tick(now=started_at)

    def tick(self, now: Optional[float] = None) -> None:
        now = float(now if now is not None else time.time())
        done_count = len(self._done)

        # Update per-task bars for items that started and aren't done
        for item, started in self._start_by_item.items():
            if item in self._done:
                continue
            task_id = self.status_task_id_by_item[item]
            est = self.est_by_item[item]
            elapsed = now - started
            self.status.update(task_id, completed=min(elapsed, est), time=f"[yellow]{_hms(elapsed)}[/yellow]")

        # Compute overall totals/completed/eta based on *current attempt only*
        ests: Dict[Any, float] = {item: float(self.est_by_item[item]) for item in self.items}
        if self.spec.total_strategy == "sum":  # Sequential
            overall_total, completed = float(sum(ests.values())), 0.0
            for item in self.items:
                est = ests[item]
                if item in self._done:
                    completed += est
                    continue
                started = self._start_by_item.get(item)
                if started is None:
                    continue
                elapsed = min(max(now - started, 0.0), est)
                completed += elapsed
            eta_override = None

        else:  # Parallel
            remaining_max = 0.0
            for item in self.items:
                est = float(self.est_by_item[item])
                if item in self._done:
                    r = 0.0
                else:
                    started = self._start_by_item.get(item)
                    if started is None:
                        r = est
                    else:
                        elapsed = min(max(now - started, 0.0), est)
                        r = max(0.0, est - elapsed)
                if r > remaining_max:
                    remaining_max = r
            elapsed_overall = max(0.0, now - self.overall_started_at)
            overall_total, completed, eta_override = elapsed_overall + remaining_max, elapsed_overall, remaining_max

        self.overall.update(self.overall_task_id, total=overall_total)
        _update_overall(self.overall, self.overall_task_id, now, self.overall_started_at, completed, done_count, eta_secs_override=eta_override)

    def finish_item(self, item: Any, result: RunResult, now: Optional[float] = None) -> None:
        self._done.add(item)
        self._results.append(result)

        task_id = self.status_task_id_by_item[item]
        est = self.est_by_item[item]
        name = self.spec.get_item_name(item)
        attempt = int(self.attempt_by_item.get(item, 1))
        _update_task_status(self.status, task_id, name, attempt, est, result)

        self.tick(now=now)

    def finalize(self, now: Optional[float] = None) -> None:
        now = float(now if now is not None else time.time())
        done_count = len(self._done)
        all_ok = all(result.ok for result in self._results) if self._results else True
        total = float(self.overall.tasks[self.overall_task_id].total or 0.0)
        elapsed = now - self.overall_started_at
        _finalize_overall_bar(self.overall, self.overall_task_id, all_ok, total, elapsed, done_count)
