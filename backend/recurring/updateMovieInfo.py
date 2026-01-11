from backend.dataflow.BaseDataflow import BaseDataflow


class updateMovieInfo(BaseDataflow):
    MAIN_TABLE_NAME = "allMovies"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)
