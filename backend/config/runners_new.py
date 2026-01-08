from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.utils.rich_support_new import RunResult, RichRunUI
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

from supabase import create_client
from types import SimpleNamespace
import time, os

from backend.config.registry import REGISTRY, DATAFLOW_REGISTRY
from backend.utils.logger import artifactPrinting

runningGithubActions = os.environ.get("GITHUB_ACTIONS") == "true"
RUNNER_MACHINE = os.environ.get("RUNNER_MACHINE")


cinemaDictionary = {"registry": REGISTRY, "make_instance": lambda cls, key, run_id: cls(cinema_type=key, supabase_table_name=key, run_id=run_id), "run_instance": lambda inst: inst.scrape(), "cleanup": lambda instance: (instance.driver.quit() if instance and getattr(instance, "driver", None) else None), "count_label": "Threads", "mode": "parallel", "total_strategy": "max", "overall_task_name": "overall", "get_item_name": lambda cls: getattr(cls, "CINEMA_NAME", cls.__name__)}
dataflowDictionary = {"registry": DATAFLOW_REGISTRY, "make_instance": lambda cls, _key, run_id: cls(run_id=run_id), "run_instance": lambda inst: inst.dataRun(), "cleanup": lambda instance: None, "count_label": "Dataflows", "mode": "sequential", "total_strategy": "sum", "overall_task_name": "dataflows", "get_item_name": lambda cls: cls.__name__}
SPEC_BY_KIND = {"cinema": cinemaDictionary, "dataflow": dataflowDictionary}


def runGroup(kind: str, key: str, run_id: int):
    spec_dict = SPEC_BY_KIND.get(kind)
    spec = SimpleNamespace(**spec_dict)
    classes = spec.registry.get(key, [])
    if not classes:
        return None

    def run_one(cls: type) -> RunResult:
        starting_time, instance, ok = time.time(), None, True
        try:
            instance = spec.make_instance(cls, key, run_id)
            spec.run_instance(instance)
        except Exception:
            ok = False
            artifactPrinting(instance)
        finally:
            spec.cleanup(instance)

        return RunResult(name=cls.__name__, secs=time.time() - starting_time, ok=ok)

    # GITHUB ACTIONS LOGIC
    if runningGithubActions:
        results: list[RunResult] = []
        if spec.mode == "parallel":
            with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
                futures = [ex.submit(run_one, cls) for cls in classes]
                for fut in as_completed(futures):
                    results.append(fut.result())
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

        with RichRunUI(spec, key, classes, get_item_est) as ui:
            if not classes:
                ui.finalize()
                return

            if spec.mode == "parallel":
                with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
                    future_to_item = {ex.submit(run_one, item): item for item in classes}

                    for item in classes:
                        ui.start_item(item)

                    pending = set(future_to_item.keys())
                    while pending:
                        ui.tick()

                        done_futures, _ = wait(pending, timeout=0, return_when=FIRST_COMPLETED)
                        for fut in done_futures:
                            pending.discard(fut)
                            item = future_to_item[fut]
                            result = fut.result()
                            ui.finish_item(item, result)

                        time.sleep(0.2)

                ui.finalize()

            else:  # sequential
                with ThreadPoolExecutor(max_workers=1) as ex:
                    for item in classes:
                        ui.start_item(item)
                        fut = ex.submit(run_one, item)

                        while not fut.done():
                            ui.tick()
                            time.sleep(0.2)

                        result = fut.result()
                        ui.finish_item(item, result)

                ui.finalize()
