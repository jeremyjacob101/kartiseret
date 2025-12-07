from backend.dataflow.BaseDataflow import BaseDataflow


class ComingSoonsOpenAI(BaseDataflow):
    MAIN_TABLE_NAME = "testingSoons"
    CHOSEN_IMDB_ID = 0

    def guess_imdb_id(self, desc_parts):
        description = " ".join(str(p) for p in desc_parts if p)

        response = self.openAiClient.responses.create(
            model="gpt-5-nano",
            input=("You are an assistant that identifies movies and returns their IMDb ID. You are based in Israel, so be aware that there might be Israeli titles (or small, European titles, too) alongside more well known U.S. or indie releases.\n" "Use web_search if needed.\n\n" "Given the following description, respond with ONLY the IMDb ID of the film you " "think it is, in the format 'tt1234567', and nothing else.\n\n" f"Description: {description}"),
            tools=[{"type": "web_search"}],
            tool_choice="auto",
        )

        imdb_id = response.output_text.strip()
        return imdb_id

    def logic(self):
        for row in self.main_table_rows:
            self.CHOSEN_IMDB_ID = 0

            english_title = str(row["english_title"]) if row.get("english_title") not in (None, "", "null") else ""
            hebrew_title = str(row["hebrew_title"]) if row.get("hebrew_title") not in (None, "", "null") else ""
            release_year = int(row["release_year"]) if row.get("release_year") not in (None, "", "null") else None
            row_director = str(row["directed_by"]) if row.get("directed_by") not in (None, "", "null") else ""
            row_runtime = int(row["runtime"]) if row.get("runtime") not in (None, "", "null") else None

            if english_title:
                try:
                    desc_parts = [english_title]
                    if release_year:
                        desc_parts.append(str(release_year))
                    if row_director:
                        desc_parts.append(row_director)
                    if row_runtime:
                        desc_parts.append(f"{row_runtime} min")
                    if hebrew_title:
                        desc_parts.append(f"{hebrew_title} min")

                    guessed_id = self.guess_imdb_id(desc_parts)
                    self.CHOSEN_IMDB_ID = guessed_id
                    print(f"{english_title:20}: https://www.imdb.com/title/{guessed_id}")
                except Exception as e:
                    print("Error guessing IMDb ID:", e)
            else:
                print("No valid title found; cannot guess IMDb ID.")
