from backend.dataflow.BaseDataflow import BaseDataflow


class NowPlayingsUpdate(BaseDataflow):
    MAIN_TABLE_NAME = "finalMovies"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)
