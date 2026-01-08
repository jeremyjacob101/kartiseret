from backend.dataflow.utils.SupabaseTables import SupabaseTables
from backend.dataflow.utils.DataflowHelpers import DataflowHelpers
from backend.dataflow.utils.InitializeBaseDataflow import InitializeBaseDataflow, setUpSupabase, setUpTmdb, logSuccessfulRun
from backend.dataflow.comingsoons.utils.ComingSoonsHelpers import ComingSoonsHelpers
from backend.dataflow.nowplayings.utils.NowPlayingsHelpers import NowPlayingsHelpers


class BaseDataflow(InitializeBaseDataflow, DataflowHelpers, SupabaseTables, ComingSoonsHelpers, NowPlayingsHelpers):
    MAIN_TABLE_NAME: str = ""
    DUPLICATE_TABLE_NAME: str = ""
    MOVING_TO_TABLE_NAME: str = ""
    MOVING_TO_TABLE_NAME_2: str = ""
    HELPER_TABLE_NAME: str = ""
    HELPER_TABLE_NAME_2: str = ""
    HELPER_TABLE_NAME_3: str = ""
    HELPER_TABLE_NAME_4: str = ""

    def __init__(self, run_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_id = run_id

        setUpSupabase(self)
        setUpTmdb(self)

        self.refreshAllTables()

    def logic(self):
        raise NotImplementedError("Each dataflow must implement its own logic()")

    def dataRun(self):
        try:
            self.logic()
            logSuccessfulRun(self)
        except Exception:
            raise
