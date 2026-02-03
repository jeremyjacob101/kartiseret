# testRT_requests_scores.py
# Goal: using requests (no Selenium) to get:
#   - rtCriticRating   (Tomatometer %)
#   - rtAudienceRating (Popcornmeter %)
#   - rtCriticVotes    (Tomatometer review count)
#   - rtAudienceVotes  (Audience rating count)
#
# Strategy:
# 1) Hit RottenTomatoes search page: https://www.rottentomatoes.com/search?search=<title year>
#    Extract the first /m/<slug> result link from the returned HTML.
# 2) Fetch that movie page and parse the <score-board ...> web component attributes.
#    Fallback to regexes over embedded JSON if the scoreboard attrs aren't present.
#
# IMPORTANT: RT sometimes serves bot checks; this file prints minimal debug per test.

import re
import time
import requests
from urllib.parse import quote_plus

TESTS = [
    {"title": "Inception", "year": "2010"},
    {"title": "Interstellar", "year": "2014"},
    {"title": "Furious 7", "year": "2015"},
    {"title": "The Dark Knight", "year": "2008"},
    {"title": "Dune", "year": "2021"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close",
}

MAX_TRIES = 4
SLEEP_BETWEEN_TRIES = 1.5


def looks_blocked(html: str, status: int) -> bool:
    t = (html or "").lower()
    if status in (403, 429, 503):
        return True
    markers = [
        "captcha",
        "verify you are human",
        "access denied",
        "bot detection",
        "incapsula",
        "cloudflare",
    ]
    return any(m in t for m in markers)


def first_movie_url_from_search(html: str):
    # Try to find /m/<slug> links (movie pages)
    # Search page includes lots of links; we want the first movie result.
    candidates = re.findall(r'href="(/m/[^"/?#]+[^"]*)"', html or "")
    if not candidates:
        candidates = re.findall(r'https?://www\.rottentomatoes\.com/m/[^"\s<]+', html or "")

    # Normalize to absolute and de-dup in order
    seen = set()
    out = []
    for c in candidates:
        url = c
        if url.startswith("/m/"):
            url = "https://www.rottentomatoes.com" + url
        url = url.split("?")[0]
        if url not in seen:
            seen.add(url)
            out.append(url)
        if len(out) >= 10:
            break

    return out[0] if out else None


def parse_scores_from_movie_page(html: str):
    # Primary: <score-board ...> attributes
    # Common attributes seen on RT:
    #   tomatometerscore="94" audiencescore="91"
    #   tomatometerreviewcount="386" audiencereviewcount="250000+"
    #
    # We'll accept a few name variations just in case.
    def grab_attr(name: str):
        m = re.search(fr'{name}\s*=\s*"([^"]+)"', html or "", flags=re.I)
        return m.group(1).strip() if m else None

    critic_score = grab_attr("tomatometerscore")
    audience_score = grab_attr("audiencescore")

    critic_count = (
        grab_attr("tomatometerreviewcount")
        or grab_attr("tomatometerreviewcountall")
        or grab_attr("tomatometerreviewcount[a-z]*")  # safety; might not hit
    )
    audience_count = (
        grab_attr("audiencereviewcount")
        or grab_attr("audiencereviewcountall")
        or grab_attr("audienceratingcount")
        or grab_attr("audiencecount")
    )

    # If attrs weren't found, fallback to embedded JSON-ish patterns
    if critic_score is None:
        m = re.search(r'"tomatometerScore"\s*:\s*([0-9]{1,3})', html or "")
        critic_score = m.group(1) if m else None
    if audience_score is None:
        m = re.search(r'"audienceScore"\s*:\s*([0-9]{1,3})', html or "")
        audience_score = m.group(1) if m else None

    if critic_count is None:
        m = re.search(r'"tomatometerCount"\s*:\s*([0-9]+)', html or "")
        critic_count = m.group(1) if m else None
    if audience_count is None:
        m = re.search(r'"audienceCount"\s*:\s*([0-9]+)', html or "")
        audience_count = m.group(1) if m else None

    # Clean/convert
    def to_int_score(v):
        if v is None:
            return None
        v = v.strip()
        if v.upper() in ("N/A", "NA", ""):
            return None
        v = re.sub(r"[^\d]", "", v)
        return int(v) if v else None

    def to_int_count(v):
        if v is None:
            return None
        v = v.strip()
        if v.upper() in ("N/A", "NA", ""):
            return None
        # remove commas and plus signs, keep digits
        v = re.sub(r"[^\d]", "", v)
        return int(v) if v else None

    return {
        "rtCriticRating": to_int_score(critic_score),
        "rtAudienceRating": to_int_score(audience_score),
        "rtCriticVotes": to_int_count(critic_count),
        "rtAudienceVotes": to_int_count(audience_count),
    }


if __name__ == "__main__":
    s = requests.Session()

    for t in TESTS:
        q = f"{t['title']} {t['year']}".strip()
        search_url = f"https://www.rottentomatoes.com/search?search={quote_plus(q)}"

        movie_url = None
        last_status = None
        blocked = False

        # --- SEARCH ---
        for attempt in range(MAX_TRIES):
            if attempt:
                time.sleep(SLEEP_BETWEEN_TRIES)

            try:
                r = s.get(search_url, headers=HEADERS, timeout=20, allow_redirects=True)
            except Exception:
                continue

            last_status = r.status_code
            html = r.text or ""
            blocked = looks_blocked(html, r.status_code)
            if blocked:
                continue

            movie_url = first_movie_url_from_search(html)
            if movie_url:
                break

        print("=" * 100)
        print("query:", q)
        print("search_status:", last_status)
        print("resolved_movie_url:", movie_url)
        if not movie_url:
            print("result: could not resolve movie URL from search (blocked or no /m/ link).")
            continue

        # --- MOVIE PAGE ---
        page_status = None
        page_blocked = False
        scores = {"rtCriticRating": None, "rtAudienceRating": None, "rtCriticVotes": None, "rtAudienceVotes": None}

        for attempt in range(MAX_TRIES):
            if attempt:
                time.sleep(SLEEP_BETWEEN_TRIES)

            try:
                r2 = s.get(movie_url, headers={**HEADERS, "Referer": search_url}, timeout=20, allow_redirects=True)
            except Exception:
                continue

            page_status = r2.status_code
            page_html = r2.text or ""
            page_blocked = looks_blocked(page_html, r2.status_code)
            if page_blocked:
                continue

            scores = parse_scores_from_movie_page(page_html)
            break

        print("page_status:", page_status)
        print("rtCriticRating:", scores["rtCriticRating"])
        print("rtCriticVotes:", scores["rtCriticVotes"])
        print("rtAudienceRating:", scores["rtAudienceRating"])
        print("rtAudienceVotes:", scores["rtAudienceVotes"])
