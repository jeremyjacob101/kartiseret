from keys import OMDB_API_KEY


def getImdbInfo(items):
    print(f"\n\ngetting imdb info\n\n")
    for href in items["hrefs"]:
        print(href)

    # for i, href in enumerate(self):
    #     try:
    #         current_href_count += 1

    #         working_title = trying_names[i]
    #         working_title_print = working_title
    #         working_title = fix_text_from_csv(working_title, "CSVs/managing/fixes.csv")

    #         try:
    #             use_imdb_id = working_title.startswith("tt")
    #         except:
    #             print(f"working_title: {working_title}")

    #         # Modify the API call based on whether it's a title or an IMDb ID
    #         omdb_url = f"https://www.omdbapi.com/?{'i=' + working_title if use_imdb_id else 's=' + working_title}&apikey={OMDB_API_KEY}&type=movie"
    #         movie_data = requests.get(omdb_url).json()

    #         if movie_data.get("Response") == "False":
    #             print_to_error_csv("Lev Cinema", working_title)
    #             continue

    #         last_three_years = {current_year, current_year - 1, current_year - 2}
    #         movie_found, poster, actual_title, movie_year, imdb_id = False, None, None, None, None
    #         selected_movie = None

    #         if not use_imdb_id:
    #             # Loop through results to find a movie from the last three years
    #             for movie in movie_data["Search"]:
    #                 movie_year = int(movie["Year"])
    #                 if movie_year in last_three_years:
    #                     poster = movie["Poster"]
    #                     actual_title = movie["Title"]
    #                     imdb_id = movie["imdbID"]
    #                     movie_found = True
    #                     break  # Exit the loop after finding the first valid movie
    #             if not movie_found:
    #                 selected_movie = movie_data["Search"][0]
    #                 poster = selected_movie["Poster"]
    #                 imdb_id = selected_movie["imdbID"]
    #                 actual_title = selected_movie["Title"]
    #                 movie_year = int(selected_movie["Year"])
    #         else:
    #             # Use the returned movie data directly if it's an IMDb ID
    #             selected_movie = movie_data
    #             imdb_id = selected_movie["imdbID"]
    #             poster = selected_movie["Poster"]
    #             actual_title = selected_movie["Title"]
    #             movie_year = int(selected_movie["Year"])
    #             movie_found = True

    #         if poster == "N/A":
    #             print_to_error_csv("Lev Cinema", working_title)
    #             continue

    #         factor = 30 if ((current_href_count / num_films_soon) * 100) < 50 else 15

    #         if current_href_count < num_films_now:
    #             site_popularity = round(((((1 - (current_href_count / num_films_now))) * 100) / 1.4), 2)
    #         else:
    #             site_popularity = round(((((1 - (current_href_count / num_films_soon))) * 100)), 2) + factor

    #         # Get detailed movie data
    #         movie_data_i = requests.get(f"https://www.omdbapi.com/?i={imdb_id}&apikey={OMDB_API_KEY}").json()

    #         actual_runtime = movie_data_i.get("Runtime", "0").split()[0]
    #         imdb_rating = float(movie_data_i.get("imdbRating", 0)) if movie_data_i.get("imdbRating") != "N/A" else 0.0
    #         imdb_votes = int(movie_data_i.get("imdbVotes", "0").replace(",", "")) if movie_data_i.get("imdbVotes") != "N/A" else 0

    #         rt_rating = 0
    #         for rating in movie_data_i.get("Ratings", []):
    #             if rating["Source"] == "Rotten Tomatoes":
    #                 rt_rating = int(rating["Value"].strip("%")) if rating["Value"] != "N/A" else 0
    #                 break

    #         print(working_title_print)
    #         print(f"{actual_title} - {movie_year}\n{href}\n{poster}\n{site_popularity}  |||  imdbScore-{imdb_rating}({imdb_votes})--rtScore-{rt_rating}\n")
    #         items["posters"].append(poster)
    #         items["years"].append(movie_year)
    #         items["hrefs"].append(href)
    #         items["runtimes"].append(actual_runtime)
    #         items["titles"].append(actual_title)
    #         items["popularity"].append(site_popularity)
    #         items["imdbIDs"].append(imdb_id)
    #         items["imdbScores"].append(imdb_rating)
    #         items["imdbVotes"].append(imdb_votes)
    #         items["rtScores"].append(rt_rating)

    #     except Exception as e:
    #         print(f"broken link lev: {e}")
    #         continue
