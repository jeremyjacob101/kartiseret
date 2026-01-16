from datetime import datetime, date
import re, unicodedata


class DataflowHelpers:
    def dateToDate(self, v):
        if isinstance(v, date):
            return v
        return datetime.fromisoformat(str(v)).date()

    def datetimeToDatetime(self, v):
        if isinstance(v, datetime):
            return v

        s = str(v).replace("T", " ")
        if s.endswith("+00"):
            s = s[:-3] + "+0000"
        elif s.endswith("+00:00"):
            s = s[:-6] + "+0000"
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f%z")

    def removeBadTitle(self, title: str) -> bool:
        if not isinstance(title, str) or title.strip() == "":
            return True  # Empty
        if re.search(r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F\u1C80-\u1C8F]", title):
            return True  # Russian
        if re.search(r"[\u0590-\u05FF\uFB1D-\uFB4F]", title):
            return True  # Hebrew
        if "HOT CINEMA" in title:
            return True  # Cinema
        return False

    def removeRussianHebrewTitle(self, title: str) -> bool:
        if re.search(r"[\u0400-\u04FF\u0500-\u052F\u2DE0-\u2DFF\uA640-\uA69F\u1C80-\u1C8F]", title):
            return True  # Russian
        return False

    def normalizeTitle(self, title: str) -> str:
        if not isinstance(title, str):
            return ""

        title = unicodedata.normalize("NFKD", title)
        title = title.encode("ascii", "ignore").decode("ascii")

        title = title.lower()
        title = re.sub(r"[-–—:?!&]+", " ", title)
        title = re.sub(r"[^a-z0-9 ]+", "", title)
        title = re.sub(r"\s+", " ", title)
        return title.strip()

    def tryExceptNone(self, func):
        try:
            return func()
        except:
            return None

    def tryExceptPass(self, func):
        try:
            func()
        except:
            pass
