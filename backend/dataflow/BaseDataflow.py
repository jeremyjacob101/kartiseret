from backend.dataflow.utils.SupabaseTables import SupabaseTables
from backend.dataflow.utils.DataflowHelpers import DataflowHelpers
from backend.dataflow.utils.InitializeBaseDataflow import InitializeBaseDataflow, setUpSupabase, setUpOmdb, setUpTmdb, setUpOpenAI
from backend.dataflow.comingsoons.utils.ComingSoonsHelpers import ComingSoonsHelpers


class BaseDataflow(InitializeBaseDataflow, DataflowHelpers, SupabaseTables, ComingSoonsHelpers):
    MAIN_TABLE_NAME: str = ""
    DUPLICATE_TABLE_NAME: str = ""
    MOVING_TO_TABLE_NAME: str = ""
    HELPER_TABLE_NAME: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        setUpSupabase(self)
        setUpOmdb(self)
        setUpTmdb(self)
        setUpOpenAI(self)

        self.main_table_rows = self.selectAll(self.MAIN_TABLE_NAME)
        self.duplicate_table_rows = self.selectAll(self.DUPLICATE_TABLE_NAME)
        self.moving_to_table_rows = self.selectAll(self.MOVING_TO_TABLE_NAME)
        self.helper_table_rows = self.selectAll(self.HELPER_TABLE_NAME)

    def logic(self):
        raise NotImplementedError("Each dataflow must implement its own logic()")

    def dataRun(self):
        try:
            self.logic()
        except Exception:
            raise
