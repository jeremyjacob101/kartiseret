from backend.config.registry import REGISTRY, DATAFLOW_REGISTRY
from utils.logger import artifactPrinting
import threading, time


def runCinemaType(type: str):
    threads, runtimes, lock = [], {}, threading.Lock()

    classes = REGISTRY.get(type, [])
    for cls in classes:

        def _target(c=cls):
            t0 = time.time()
            instance = None
            try:
                instance = c(cinema_type=type, supabase_table_name=type)
                instance.scrape()
            except KeyboardInterrupt:
                return
            except Exception:
                artifactPrinting(instance)
            finally:
                dt = time.time() - t0
                with lock:
                    runtimes[c.__name__] = dt
                try:
                    if instance and getattr(instance, "driver", None):
                        instance.driver.quit()
                except Exception:
                    raise

        thread = threading.Thread(target=_target, name=cls.__name__)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\n\n\n--------------------\n")
    for name, secs in runtimes.items():
        m, s = divmod(int(secs), 60)
        print(f"{name}: {m:02d}m{s:02d}s\n")


def runDataflows():
    step_timings = []

    for key, classes in DATAFLOW_REGISTRY.items():
        for cls in classes:
            t0 = time.time()
            instance = None
            try:
                instance = cls()
                instance.dataRun()
            except KeyboardInterrupt:
                return
            except Exception:
                artifactPrinting(instance)
            finally:
                dt = time.time() - t0
                step_timings.append((f"{key}:{cls.__name__}", dt))

    print("\n\n\n--------------------\n")
    for name, secs in step_timings:
        m, s = divmod(int(secs), 60)
        print(f"{name}: {m}m{s:02d}s\n")
