from backend.dataflow.BaseSupabaseData import BaseSupabaseData


class ComingSoonsData(BaseSupabaseData):
    def logic(self):
        comingSoons = self.selectAll("testingSoons")

        