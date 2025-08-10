from scraping.chains.BaseCinema import BaseCinema


class LevCinema(BaseCinema):
    NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self, items):
        print(f"scraping lev cinema")
        for i in range(
            1,
            self.elementsXPATH(
                "/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[1]/div/ul/li",
                "featureItem",
            )
            + 1,
        ):
            self.trying_names.append(
                self.elementCSS(
                    f"#categoryfeatures_portfolio > li:nth-child({i}) > div > a > img"
                ).get_attribute("alt")
            )
            self.trying_hrefs.append(
                self.elementCSS(
                    f"#categoryfeatures_portfolio > li:nth-child({i}) > div > a"
                ).get_attribute("href")
            )
        for i in range(
            1,
            self.elementsXPATH(
                "/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[2]/div/ul/li",
                "featureItem",
            )
            + 1,
        ):
            self.trying_names.append(
                self.elementCSS(
                    f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[2]/div/ul/li[{i}]/div/a[1]/img"
                ).get_attribute("alt")
            )
            self.trying_hrefs.append(
                self.elementCSS(
                    f"/html/body/div[1]/div[2]/div[3]/div/section/div[1]/div/div/div[2]/div/ul/li[{i}]/div/a[1]"
                ).get_attribute("href")
            )