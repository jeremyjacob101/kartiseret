from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, as_completed
from supabase import create_client
from types import SimpleNamespace
import time, os, queue

from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from backend.utils.console.progressBars import RunResult, RichRunUI
from backend.config.registry import REGISTRY, DATAFLOW_REGISTRY
from backend.utils.log.logger import artifactPrinting


runningGithubActions = os.environ.get("GITHUB_ACTIONS") == "true"
RUNNER_MACHINE = os.environ.get("RUNNER_MACHINE")
MAX_NUM_RETRIES = 3

cinemaDictionary = {"registry": REGISTRY, "make_instance": lambda cls, key, run_id: cls(cinema_type=key, supabase_table_name=key, run_id=run_id), "run_instance": lambda inst: inst.scrape(), "cleanup": lambda instance: (instance.driver.quit() if instance and getattr(instance, "driver", None) else None), "count_label": "Threads", "mode": "parallel", "total_strategy": "max", "overall_task_name": "overall", "get_item_name": lambda cls: getattr(cls, "CINEMA_NAME", cls.__name__)}
dataflowDictionary = {"registry": DATAFLOW_REGISTRY, "make_instance": lambda cls, _key, run_id: cls(run_id=run_id), "run_instance": lambda inst: inst.dataRun(), "cleanup": lambda instance: None, "count_label": "Dataflows", "mode": "sequential", "total_strategy": "sum", "overall_task_name": "dataflows", "get_item_name": lambda cls: cls.__name__}
SPEC_BY_KIND = {"cinema": cinemaDictionary, "dataflow": dataflowDictionary}

DEFAULT_PLAN: list[tuple[str, str]] = [("cinema", "testingSoons"), ("cinema", "testingShowtimes"), ("dataflow", "comingSoonsData"), ("dataflow", "nowPlayingData")]


def runGroup(kind: str, key: str, run_id: int, *, classes_override: list[type] | None = None, ui_parent: Live | None = None, header_renderable: RenderableType | None = None, console: Console | None = None):
    spec_dict = SPEC_BY_KIND.get(kind)
    spec = SimpleNamespace(**spec_dict)
    classes = list(classes_override) if classes_override is not None else spec.registry.get(key, [])
    if not classes:
        return None

    attempt_events: "queue.SimpleQueue[tuple]" = queue.SimpleQueue()

    def run_one(cls: type) -> RunResult:
        total_secs, last_attempt, ok = 0.0, 0, False

        for attempt in range(1, MAX_NUM_RETRIES + 1):
            starting_time, last_attempt, instance = time.time(), attempt, None
            attempt_events.put(("attempt_start", cls, attempt, starting_time))

            try:
                instance = spec.make_instance(cls, key, run_id)
                spec.run_instance(instance)
                ok = True
            except Exception:
                ok = False
                artifactPrinting(instance)
            finally:
                spec.cleanup(instance)

            total_secs += time.time() - starting_time
            if ok:
                break

        return RunResult(name=cls.__name__, secs=total_secs, ok=ok, attempts=last_attempt)

    def drain_attempt_events(ui: RichRunUI):
        while True:
            try:
                evt = attempt_events.get_nowait()
            except queue.Empty:
                return

            evt_type, item, attempt, started_at = evt
            if evt_type == "attempt_start":
                if attempt == 1:
                    ui.start_item(item, attempt=attempt, started_at=started_at)
                else:
                    ui.retry_item(item, attempt=attempt, started_at=started_at)

    # GITHUB ACTIONS LOGIC
    if runningGithubActions:
        results: list[RunResult] = []
        if spec.mode == "parallel":
            with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
                futures = [ex.submit(run_one, cls) for cls in classes]
                for future in as_completed(futures):
                    results.append(future.result())
        else:
            for cls in classes:
                results.append(run_one(cls))

        print("\n--------------------\n", flush=True)
        for result in results:
            minutes, seconds = divmod(int(result.secs), 60)
            print(f"{result.name}: {minutes:02d}m{seconds:02d}s", flush=True)
        print("\n--------------------\n", flush=True)

    # LOCAL MACHINE LOGIC
    if not runningGithubActions:
        FALLBACK = 60.0
        avg_by_name: dict[str, float] = {}

        url, svc_key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        avg_time_col = "avg_time_" + str(RUNNER_MACHINE)
        if url and svc_key:
            table, name_col, time_col = "utilAvgTime", "name", f"{avg_time_col}"
            class_names = [cls.__name__ for cls in classes]
            sb = create_client(url, svc_key)
            resp = sb.table(table).select(f"{name_col},{time_col}").in_(name_col, class_names).execute()

            rows = resp.data or []
            for row in rows:
                k = row.get(name_col)
                value = float(row.get(time_col) or 0.0)
                if value > 0:
                    avg_by_name[k] = value

        get_item_est = lambda item: float(avg_by_name.get(item.__name__) or FALLBACK)

        use_embedded = ui_parent is not None
        ui = RichRunUI(spec, key, classes, get_item_est, use_live=not use_embedded, console=console)

        with ui:
            if not classes:
                ui.finalize()
                return

            if use_embedded:
                hdr = header_renderable or Panel.fit(Text("Running...", style="bold"), border_style="grey37")
                ui_parent.update(Group(hdr, ui.renderable))

            if spec.mode == "parallel":
                with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
                    future_to_item = {ex.submit(run_one, item): item for item in classes}
                    pending = set(future_to_item.keys())
                    while pending:
                        drain_attempt_events(ui)
                        ui.tick()

                        done_futures, _ = wait(pending, timeout=0, return_when=FIRST_COMPLETED)
                        for future in done_futures:
                            pending.discard(future)
                            item = future_to_item[future]
                            result = future.result()
                            ui.finish_item(item, result)
                        time.sleep(0.2)

                drain_attempt_events(ui)
                ui.finalize()

            else:  # sequential
                with ThreadPoolExecutor(max_workers=1) as ex:
                    for item in classes:
                        future = ex.submit(run_one, item)

                        while not future.done():
                            drain_attempt_events(ui)
                            ui.tick()
                            time.sleep(0.2)

                        drain_attempt_events(ui)
                        result = future.result()
                        ui.finish_item(item, result)

                ui.finalize()

            if use_embedded:
                hdr = header_renderable or Panel.fit(Text("Running...", style="bold"), border_style="grey37")
                ui_parent.update(Group(hdr, ui.renderable))


def runPlan(run_id: int, plan: list[tuple[str, str]], header_renderable: RenderableType | None = None):
    console = Console()
    header_renderable = header_renderable or Panel(Text("Running…", style="bold"), title="Run Plan", border_style="grey37")

    placeholder = Panel.fit(Text("Starting…", style="yellow"), border_style="grey37")
    with Live(Group(header_renderable, placeholder), console=console, refresh_per_second=12) as live:
        if not plan:
            live.update(Group(header_renderable, Panel.fit(Text("Nothing selected.", style="red"), border_style="grey37")))
            return

        total = len(plan)
        for i, entry in enumerate(plan, start=1):
            if len(entry) == 2:
                kind, key = entry
                classes_override = None
            else:
                kind, key, classes_override = entry

            step = Panel.fit(Text(f"{i}/{total}: {kind} → {key}", style="grey70"), border_style="grey37")
            combined_header = Group(header_renderable, step)
            live.update(Group(combined_header, placeholder))

            runGroup(kind, key, run_id, classes_override=classes_override, ui_parent=live, header_renderable=combined_header, console=console)
