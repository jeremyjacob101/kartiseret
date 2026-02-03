import re
import requests
from urllib.parse import quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
}

TESTS = [
    ("inception", 2010),
    ("interstellar", 2014),
    ("the dark knight", 2008),
    ("dune", 2021),
    ("mad max: fury road", 2015),
]

for q, target_year in TESTS:
    search_url = f"https://www.rottentomatoes.com/search?search={quote_plus(q)}"
    search_html = requests.get(search_url, headers=HEADERS, timeout=20).text or ""

    rows = re.findall(r"<search-page-media-row\b.*?>.*?</search-page-media-row>", search_html, flags=re.S | re.I)

    picked_url = None
    for row in rows:
        y = re.search(r'release-year="(\d{4})"', row, flags=re.I)
        if not y:
            continue
        try:
            yr = int(y.group(1))
        except Exception:
            continue
        if abs(yr - int(target_year)) > 1:
            continue

        href = re.search(r'href="(https?://www\.rottentomatoes\.com/m/[^"]+)"', row, flags=re.I)
        if href:
            picked_url = href.group(1)
            break

    if not picked_url:
        continue

    html = requests.get(picked_url, headers={**HEADERS, "Referer": search_url}, timeout=20).text or ""

    m_critic_pct = re.search(r'<rt-text[^>]*slot="critics-score"[^>]*>\s*([0-9]{1,3})%\s*</rt-text>', html, flags=re.I)
    m_aud_pct = re.search(r'<rt-text[^>]*slot="audience-score"[^>]*>\s*([0-9]{1,3})%\s*</rt-text>', html, flags=re.I)
    m_critic_reviews = re.search(r'<rt-link[^>]*slot="critics-reviews"[^>]*>\s*([\d,]+)\s*Reviews\s*</rt-link>', html, flags=re.I)
    m_aud_ratings = re.search(r'<rt-link[^>]*slot="audience-reviews"[^>]*>\s*([\d,]+\+?)\s*Ratings\s*</rt-link>', html, flags=re.I)
    rtCriticRating = int(m_critic_pct.group(1)) if m_critic_pct else None
    rtAudienceRating = int(m_aud_pct.group(1)) if m_aud_pct else None
    rtCriticVotes = int(re.sub(r"[^\d]", "", (m_critic_reviews.group(1) or "").replace(",", "").replace("+", ""))) if m_critic_reviews and re.sub(r"[^\d]", "", (m_critic_reviews.group(1) or "").replace(",", "").replace("+", "")) else None
    rtAudienceVotes = int(re.sub(r"[^\d]", "", (m_aud_ratings.group(1) or "").replace(",", "").replace("+", ""))) if m_aud_ratings and re.sub(r"[^\d]", "", (m_aud_ratings.group(1) or "").replace(",", "").replace("+", "")) else None
