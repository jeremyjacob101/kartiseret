from backend.dataflow.BaseDataflow import BaseDataflow


class ComingSoonsUpdate(BaseDataflow):
    MAIN_TABLE_NAME = "finalSoons"

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)
