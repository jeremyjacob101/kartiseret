from scraping.chains.BaseCinema import BaseCinema
import re


class LevCinema(BaseCinema):
    NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self):
        print(f"scraping lev cinema")

        for tab in (1, 2):
            for i in range(
                1,
                self.elementsXPATH(
                    f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab}]/div/ul/li",
                    "featureItem",
                )
                + 1,
            ):
                name = self.elementXPATH(
                    f"{f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab}]/div/ul/li"}[{i}]/div/a[1]/img"
                ).get_attribute("alt")
                href = self.elementXPATH(
                    f"{f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[{tab}]/div/ul/li"}[{i}]/div/a[1]"
                ).get_attribute("href")
                self.trying_names.append(name)
                self.trying_hrefs.append(href)

        for i, href in enumerate(self.trying_hrefs):
            self.driver.get(self.trying_hrefs[i])

            release_year = self.elementXPATH(
                "/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[1]"
            ).text
            release_year = (
                m.group(0)
                if (m := re.search(r"\b(19|20)\d{2}\b", release_year))
                else ""
            )

            audio_language = self.elementXPATH(
                "/html/body/div[1]/div[2]/div[2]/div/div[1]/div/section/div[1]/div[2]/div[2]/div[1]/div[2]"
            ).text

            print(f"{self.trying_names[i]} - {release_year} - {audio_language}")
