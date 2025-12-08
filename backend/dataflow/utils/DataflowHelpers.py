from datetime import datetime, date
import re, unicodedata


class DataflowHelpers:
    def dateToDate(self, v):
        if isinstance(v, date):
            return v
        return datetime.fromisoformat(str(v)).date()

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

    def canonicalize_title(self, title):
        if not title:
            return ""

        t = unicodedata.normalize("NFKC", title.lower().strip())
        t = re.sub(r":\s*הסרט$", "", t)
        t = t.replace("-", " ")
        t = re.sub(r"\s+", " ", t).strip()
        t = re.sub(r"[^\w\s\u0590-\u05FF]", "", t)
        t = re.sub(r"\bשנים\b", "שנה", t)
        t = t.replace(" ", "")

        return t

    def levenshtein_distance(self, a, b, max_distance=1):
        if a == b:
            return 0

        if abs(len(a) - len(b)) > max_distance:
            return max_distance + 1

        if len(a) == len(b):
            diffs = [i for i in range(len(a)) if a[i] != b[i]]
            if len(diffs) == 2:
                i, j = diffs
                if j == i + 1 and a[i] == b[j] and a[j] == b[i]:
                    return 1

        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            curr = [i]
            min_row = i
            for j, cb in enumerate(b, 1):
                cost = 0 if ca == cb else 1
                insert_cost = curr[j - 1] + 1
                delete_cost = prev[j] + 1
                replace_cost = prev[j - 1] + cost
                val = min(insert_cost, delete_cost, replace_cost)
                curr.append(val)
                min_row = min(min_row, val)
            if min_row > max_distance:
                return max_distance + 1
            prev = curr

        return prev[-1]

    def fuzzy_key(self, title, cache=None):
        canonical = self.canonicalize_title(title)
        if cache is None:
            return canonical
        if canonical in cache:
            return cache[canonical]

        for k in cache.keys():
            if self.levenshtein_distance(canonical, k, max_distance=1) <= 1:
                cache[canonical] = k
                return k

        cache[canonical] = canonical
        return canonical
