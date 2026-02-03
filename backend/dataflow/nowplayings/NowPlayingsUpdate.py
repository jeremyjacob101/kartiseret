from backend.dataflow.BaseDataflow import BaseDataflow
from urllib.parse import quote_plus
import requests, re, time


class NowPlayingsUpdate(BaseDataflow):
    MAIN_TABLE_NAME = "finalMovies"
    HEADLESS = False

    def logic(self):
        self.dedupeTable(self.MAIN_TABLE_NAME)

        for row in self.main_table_rows:
            self.reset_np_main_row_state()
            self.load_update_final_movies_main_row(row)
            new_row = dict(row)

            # TMDb
            try:
                data = requests.get(f"https://api.themoviedb.org/3/movie/{self.tmdb_id}", params={"api_key": self.TMDB_API_KEY, "append_to_response": "external_ids"}, timeout=10).json()
            except:
                continue
            new_row["english_title"] = data["title"].strip() if data.get("title") else self.english_title
            new_row["runtime"] = data["runtime"] if data.get("runtime") is not None else self.runtime
            new_row["popularity"] = data["popularity"] if data.get("popularity") is not None else self.popularity
            new_row["imdb_id"] = data.get("external_ids", {}).get("imdb_id") or self.imdb_id
            new_row["poster"] = "https://image.tmdb.org/t/p/w500" + data["poster_path"] if data.get("poster_path") else self.poster
            new_row["backdrop"] = "https://image.tmdb.org/t/p/w500" + data["backdrop_path"] if data.get("backdrop_path") else self.backdrop
            new_row["release_year"] = data["release_date"][:4] if data.get("release_date") else self.release_year
            new_row["tmdbRating"] = int(round(data["vote_average"] * 10)) if data.get("vote_average") is not None else self.tmdbRating
            new_row["tmdbVotes"] = data["vote_count"] if data.get("vote_count") is not None else self.tmdbVotes
            new_row["lb_id"] = f"tmdb/{self.tmdb_id}"

            # Letterboxd
            tmdb_url = f"https://letterboxd.com/tmdb/{self.tmdb_id}/"
            r0, loc, session, lb_resolved, film_url = None, None, None, False, ""
            for attempt in range(10):
                if attempt:
                    time.sleep(2)
                session = requests.Session()
                try:
                    session.get("https://letterboxd.com/", headers=self.requests_headers, timeout=20)
                except Exception:
                    pass
                try:
                    r0 = session.get(tmdb_url, headers=self.requests_headers, timeout=20, allow_redirects=False)
                except Exception:
                    continue
                loc = r0.headers.get("Location")
                if r0.status_code in (301, 302, 303, 307, 308) and loc:
                    lb_resolved = True
                    break
                if r0.status_code == 403:
                    t = (r0.text or "").lower()
                    if ("just a moment" in t) or ("cf-challenge" in t) or ("challenge-platform" in t):
                        continue
                break
            if lb_resolved:
                film_url = loc if (loc and (loc.startswith("http://") or loc.startswith("https://"))) else ("https://letterboxd.com" + loc if loc else "")
                if film_url and ("/film/" in film_url):
                    try:
                        rf = session.get(film_url, headers={**self.requests_headers, "Referer": tmdb_url}, timeout=20, allow_redirects=True)
                        html = rf.text or ""
                        m1 = re.search(r'meta name="twitter:data2" content="([\d.]+) out of 5"', html)
                        if m1:
                            try:
                                new_row["lbRating"] = round(float(m1.group(1)), 1)
                            except Exception:
                                new_row["lbRating"] = self.lbRating
                        m2 = re.search(r'"ratingCount":\s*(\d+)', html)
                        if m2:
                            try:
                                new_row["lbVotes"] = int(m2.group(1))
                            except Exception:
                                new_row["lbVotes"] = self.lbVotes
                    except Exception:
                        pass

            # IMDb
            if new_row.get("imdb_id"):
                imdb_id = new_row["imdb_id"].strip()
                if imdb_id:
                    try:
                        html = requests.get(f"https://www.imdb.com/title/{imdb_id}/", headers=self.requests_headers, timeout=20, allow_redirects=True).text
                    except:
                        html = ""
                    m = re.search(r'"ratingValue"\s*:\s*"?([\d.]+)"?', html or "")
                    new_row["imdbRating"] = m.group(1) if m else self.imdbRating
                    m = re.search(r'"ratingCount"\s*:\s*"?([\d,]+)"?', html or "")
                    new_row["imdbVotes"] = int(m.group(1).replace(",", "")) if m else self.imdbVotes

            # Rotten Tomatoes
            search_url = f"https://www.rottentomatoes.com/search?search={quote_plus(new_row['english_title'])}"
            search_html = requests.get(search_url, headers=self.requests_headers, timeout=20).text or ""
            rows = re.findall(r"<search-page-media-row\b.*?>.*?</search-page-media-row>", search_html, flags=re.S | re.I)
            picked_url = None
            for rt_row in rows:
                y = re.search(r'release-year="(\d{4})"', rt_row, flags=re.I)
                if not y:
                    continue
                try:
                    yr = int(y.group(1))
                except Exception:
                    continue
                try:
                    target_year = int(new_row.get("release_year") or 0)
                except Exception:
                    target_year = 0
                if not target_year or abs(yr - target_year) > 1:
                    continue

                href = re.search(r'href="(https?://www\.rottentomatoes\.com/m/[^"]+)"', rt_row, flags=re.I)
                if href:
                    picked_url = href.group(1)
                    m_path = re.search(r"rottentomatoes\.com(/m/[^/?#]+)", picked_url)
                    new_row["rt_id"] = m_path.group(1) if m_path else self.rt_id
                    break
            if picked_url:
                try:
                    html = requests.get(picked_url, headers={**self.requests_headers, "Referer": search_url}, timeout=20).text or ""

                    m_critic_pct = re.search(r'<rt-text[^>]*slot="critics-score"[^>]*>\s*([0-9]{1,3})%\s*</rt-text>', html, flags=re.I)
                    m_aud_pct = re.search(r'<rt-text[^>]*slot="audience-score"[^>]*>\s*([0-9]{1,3})%\s*</rt-text>', html, flags=re.I)
                    m_critic_reviews = re.search(r'<rt-link[^>]*slot="critics-reviews"[^>]*>\s*([\d,]+)\s*Reviews\s*</rt-link>', html, flags=re.I)
                    m_aud_ratings = re.search(r'<rt-link[^>]*slot="audience-reviews"[^>]*>\s*([\d,]+\+?)\s*Ratings\s*</rt-link>', html, flags=re.I)

                    new_row["rtCriticRating"] = int(m_critic_pct.group(1)) if m_critic_pct else self.rtCriticRating
                    new_row["rtAudienceRating"] = int(m_aud_pct.group(1)) if m_aud_pct else self.rtAudienceRating
                    new_row["rtCriticVotes"] = int(re.sub(r"[^\d]", "", (m_critic_reviews.group(1) or "").replace(",", "").replace("+", ""))) if m_critic_reviews and re.sub(r"[^\d]", "", (m_critic_reviews.group(1) or "").replace(",", "").replace("+", "")) else self.rtCriticVotes
                    new_row["rtAudienceVotes"] = int(re.sub(r"[^\d]", "", (m_aud_ratings.group(1) or "").replace(",", "").replace("+", ""))) if m_aud_ratings and re.sub(r"[^\d]", "", (m_aud_ratings.group(1) or "").replace(",", "").replace("+", "")) else self.rtAudienceVotes
                except:
                    pass

            self.updates.append(new_row)

        if self.updates:
            self.upsertUpdates(self.MAIN_TABLE_NAME)
            self.dedupeTable(self.MAIN_TABLE_NAME, sort_key=self.newestCreatedAtSortKey, sort_reverse=True)
