from scraping.chains.BaseCinema import BaseCinema


class LevCinema(BaseCinema):
    NAME = "Lev Cinema"
    URL = "https://www.lev.co.il/en/"

    def logic(self, items):
        print(f"scraping lev cinema")
        for i in range(
            1,
            self.elementsCSS("#categoryfeatures_portfolio > li:nth-child(2)"),
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
            print(f"{self.trying_names[i]}")
