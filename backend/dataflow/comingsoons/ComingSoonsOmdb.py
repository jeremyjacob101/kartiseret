from backend.dataflow.BaseDataflowData import BaseDataflowData
import requests


class ComingSoonsOmdb(BaseDataflowData):
    MAIN_TABLE_NAME = "testingSoons"

    def logic(self):
        for row in self.main_table_rows:
            print(f"{row["english_title"]}\n")
            omdb_url = f"http://www.omdbapi.com/?apikey={self.OMDB_API_KEY}&s={row["english_title"]}"
            movie_data = requests.get(omdb_url).json()
            if movie_data.get("Response") == "False":
                print("error")
            else:
                print(movie_data)

            print("\n\n\n")