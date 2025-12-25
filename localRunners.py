from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.console import Console, Group
from rich.live import Live
from rich.theme import Theme
import time

from localRegistry import REGISTRY, DATAFLOW_REGISTRY
from utils.logger import artifactPrinting


def runCinemaType(type: str):
    classes = REGISTRY.get(type, [])

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
        return getattr(cls, "CINEMA_NAME", cls.__name__), time.time() - t0, ok

    console = Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))
    overall = Progress(TimeElapsedColumn(), TextColumn("[bold green]{task.completed}/{task.total} Threads[/bold green] " "[bold #66d6f2]{task.fields[cinema_type]}[bold /#66d6f2]"), SpinnerColumn(style="bold #f266e0"), console=console, refresh_per_second=6)
    status = Progress(TextColumn("{task.fields[time]}"), TextColumn("{task.description}"), console=console, refresh_per_second=6)

    status_task_by_name = {}
    with Live(Group(overall, status), console=console, refresh_per_second=6):
        overall_task = overall.add_task("scrape", total=len(classes), cinema_type=type)
        for cls in classes:
            name = getattr(cls, "CINEMA_NAME", cls.__name__)
            tid = status.add_task(f"[yellow]{name}[/yellow]", total=1, time=f"[yellow]       [/yellow]")
            status_task_by_name[name] = tid

        with ThreadPoolExecutor(max_workers=max(1, len(classes))) as ex:
            futures = [ex.submit(run_one, cls) for cls in classes]
            for future in as_completed(futures):
                name, secs, ok = future.result()
                tid = status_task_by_name[name]

                h, rem = divmod(int(secs), 3600)
                m, s = divmod(rem, 60)
                hms = f"{h}:{m:02d}:{s:02d}"

                if ok:
                    status.update(tid, description=f"[green]{name}[/green]", time=f"[green]{hms}[/green]", completed=1)
                else:
                    status.update(tid, description=f"[red]{name}[/red]", time=f"[red]{hms}[/red]", completed=1)
                overall.advance(overall_task, 1)


def runDataflows(flow_key: str):
    classes = DATAFLOW_REGISTRY.get(flow_key, [])
    if not classes:
        return

    console = Console(theme=Theme({"progress.elapsed": "bold #9c27f5"}))
    overall = Progress(TimeElapsedColumn(), TextColumn("[bold green]{task.completed}/{task.total} Dataflows[/bold green] " "[bold #66d6f2]{task.fields[flow_key]}[/bold #66d6f2]"), SpinnerColumn(style="bold #f266e0"), console=console, refresh_per_second=6)
    status = Progress(TextColumn("{task.fields[time]}"), TextColumn("{task.description}"), console=console, refresh_per_second=6)

    status_task_by_name = {}
    with Live(Group(overall, status), console=console, refresh_per_second=6):
        overall_task = overall.add_task("dataflow", total=len(classes), flow_key=flow_key)
        for cls in classes:
            tid = status.add_task(f"[yellow]{cls.__name__}[/yellow]", total=1, time=f"[yellow]       [/yellow]")
            status_task_by_name[cls.__name__] = tid

        for cls in classes:
            tid = status_task_by_name[cls.__name__]
            t0, instance, ok = time.time(), None, True
            try:
                instance = cls()
                instance.dataRun()
            except Exception:
                ok = False
                artifactPrinting(instance)

            secs = time.time() - t0
            h, rem = divmod(int(secs), 3600)
            m, s = divmod(rem, 60)
            hms = f"{h}:{m:02d}:{s:02d}"

            if ok:
                status.update(tid, description=f"[green]{cls.__name__}[/green]", time=f"[green]{hms}[/green]", completed=1)
            else:
                status.update(tid, description=f"[red]{cls.__name__}[/red]", time=f"[red]{hms}[/red]", completed=1)

            overall.advance(overall_task, 1)
