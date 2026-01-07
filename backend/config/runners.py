from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.utils.rich_support import RunResult, run_rich_ui

from supabase import create_client
from dataclasses import dataclass
from typing import Callable, Any
import time, os

from backend.config.registry import REGISTRY, DATAFLOW_REGISTRY
from backend.utils.logger import artifactPrinting

runningGithubActions = os.environ.get("GITHUB_ACTIONS") == "true"
RUNNER_MACHINE = os.environ.get("RUNNER_MACHINE")


@dataclass(frozen=True)
class KindSpec:
    registry: dict[str, list[type]]
    make_instance: Callable[[type, str], Any]
    run_instance: Callable[[Any], None]
    cleanup: Callable[[Any], None]
    count_label: str
    mode: str  # "parallel" | "sequential"
    total_strategy: str  # "max" | "sum"
    overall_task_name: str
    get_item_name: Callable[[type], str]


KIND_SPECS: dict[str, KindSpec] = {
    "cinema": KindSpec(registry=REGISTRY, make_instance=lambda cls, key: cls(cinema_type=key, supabase_table_name=key), run_instance=lambda inst: inst.scrape(), cleanup=lambda instance: (instance.driver.quit() if instance and getattr(instance, "driver", None) else None), count_label="Threads", mode="parallel", total_strategy="max", overall_task_name="overall", get_item_name=lambda cls: getattr(cls, "CINEMA_NAME", cls.__name__)),
    "dataflow": KindSpec(registry=DATAFLOW_REGISTRY, make_instance=lambda cls, key: cls(), run_instance=lambda inst: inst.dataRun(), cleanup=lambda instance: None, count_label="Dataflows", mode="sequential", total_strategy="sum", overall_task_name="dataflows", get_item_name=lambda cls: cls.__name__),
}


def runGroup(kind: str, key: str):
    spec = KIND_SPECS.get(kind)
    classes = spec.registry.get(key, [])
    if not classes:
        return None

    def run_one(cls: type) -> RunResult:
        starting_time, instance, ok = time.time(), None, True
        try:
            instance = spec.make_instance(cls, key)
            spec.run_instance(instance)
        except Exception:
            ok = False
            artifactPrinting(instance)
        finally:
            spec.cleanup(instance)

        return RunResult(name=cls.__name__, secs=time.time() - starting_time, ok=ok)

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

    if not runningGithubActions:
        FALLBACK = 60.0
        avg_by_name: dict[str, float] = {}

        url, svc_key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        avg_time_col = "avg_time_" + str(RUNNER_MACHINE)
        if url and svc_key:
            if kind == "dataflow":
                table, name_col, time_col = "utilAvgDataTime", "data_type", f"{avg_time_col}"
            if kind == "cinema":
                table, name_col, time_col = "utilAvgScrapeTime", "cinema_name", f"{avg_time_col}"

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
        run_rich_ui(spec, key, classes, get_item_est, run_one)
