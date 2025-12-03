from backend.dataflow.BaseDataflowData import BaseDataflowData
import requests


class ComingSoonsOmdb(BaseDataflowData):
    MAIN_TABLE_NAME = "testingSoons"

    def logic(self):
        dune_name = "dune"
        omdb_url = f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&s={dune_name}"
        print(self.OMDB_API_KEY)
        print(omdb_url)
        response = requests.get(omdb_url)
        movie_data = response.json()
        if movie_data.get("Response") == "False":
            print("error")
        else:
            print(movie_data)
