from backend.dataflow.BaseDataflow import BaseDataflow


class ComingSoonsOpenAI(BaseDataflow):
    MAIN_TABLE_NAME = "allSoons"

    def guess_imdb_id(self, eng_desc_parts, heb_desc_parts):
        eng_description = ", ".join(str(p) for p in eng_desc_parts if p)
        heb_description = ", ".join(str(p) for p in eng_desc_parts if p)

        fast_response = self.openAiClient.responses.create(
            model="gpt-5-nano",
            input=(
                "You are an assistant that identifies movies and returns their IMDb ID. You are based in Israel, so be aware that there might be Israeli titles (or small, European titles, too) alongside more well known U.S. or indie releases.\n"
                "Do not use web search. And respond quickly.\n\n"
                "Given the following description, respond with ONLY the IMDb ID of the film you "
                "think it is, in the format 'tt1234567', and nothing else.\n\n If you're really unsure, return unknown."
                f"Description: {eng_description}"
            ),
            tool_choice="none",
            max_output_tokens=1000,
            reasoning={"effort": "low"},
        )

        first_guess = fast_response.output_text.strip()

        if first_guess.startswith("tt"):
            return first_guess

        full_response = self.openAiClient.responses.create(
            model="gpt-5-nano",
            input=("You are an assistant that identifies movies and returns their IMDb ID. You are based in Israel, so be aware that there might be Israeli titles (or small, European titles, too) alongside more well known U.S. or indie releases.\n" "Use web_search if needed. And respond quickly.\n\n" "Given the following description, respond with ONLY the IMDb ID of the film you " "think it is, in the format 'tt1234567', and nothing else.\n\n" f"Description: {heb_description}"),
            tools=[{"type": "web_search"}],
            tool_choice="auto",
            max_output_tokens=1000,
            reasoning={"effort": "low"},
        )

        final_guess = full_response.output_text.strip()
        return f"{final_guess}/"

    def logic(self):
        for row in self.main_table_rows:
            english_title = str(row["english_title"]) if row.get("english_title") not in (None, "", "null") else ""
            hebrew_title = str(row["hebrew_title"]) if row.get("hebrew_title") not in (None, "", "null") else ""
            release_year = int(row["release_year"]) if row.get("release_year") not in (None, "", "null") else None
            row_director = str(row["directed_by"]) if row.get("directed_by") not in (None, "", "null") else ""
            row_runtime = int(row["runtime"]) if row.get("runtime") not in (None, "", "null") else None

            if english_title:
                try:
                    eng_desc_parts = [english_title]
                    heb_desc_parts = [english_title]
                    if release_year:
                        eng_desc_parts.append(str(release_year))
                        heb_desc_parts.append(str(release_year))
                    if row_director:
                        eng_desc_parts.append(row_director)
                        heb_desc_parts.append(row_director)
                    if row_runtime:
                        eng_desc_parts.append(f"{row_runtime} min")
                        heb_desc_parts.append(f"{row_runtime} min")
                    if hebrew_title:
                        heb_desc_parts.append(f"{hebrew_title}")

                    guessed_id = self.guess_imdb_id(eng_desc_parts, heb_desc_parts)
                    self.potential_chosen = guessed_id
                    print(f"{english_title:30}: https://www.imdb.com/title/{self.potential_chosen}")
                except Exception as e:
                    print("Error guessing IMDb ID:", e)
            else:
                print("No valid title found; cannot guess IMDb ID.")
