from backend.dataflow.utils.DataflowHelpers import DataflowHelpers, setUpSupabase


class BaseDataflowData(DataflowHelpers):
    STARTING_TABLE_NAME: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setUpSupabase(self)  # Sets up supabase client for each dataflow
        self.table_rows = self.selectAll(self.STARTING_TABLE_NAME)
        self.visited_already = set()
        self.delete_these = []
        self.PRIMARY_KEY = "id"

        self.fake_runtimes = [60, 90, 100, 120, 150, 180, 200, 240, 250]

    def logic(self):
        raise NotImplementedError("Each dataflow must implement its own logic()")

    def dataRun(self):
        try:
            self.logic()  # Dataflow logic
        except Exception:
            raise
