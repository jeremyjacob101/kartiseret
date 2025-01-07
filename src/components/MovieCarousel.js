import React, { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";
import "../componentsCSS/MovieCarousel.css";
import MoviesSection from "./MoviesSection";
import CarouselControls from "./CarouselControls";

const getFormattedDate = (dayOffset) => {
  const today = new Date();
  today.setDate(today.getDate() + dayOffset);

  const year = String(today.getFullYear()).slice(-2);
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  console.log("getFormattedDate:", { dayOffset, year, month, day });

  return `${year}-${month}-${day}`;
};

const isValidShowtime = (
  showtime,
  showtimeDate,
  today,
  currentMinutesSinceMidnight
) => {
  console.log(
    "Validating showtime:",
    showtime,
    "Showtime Date:",
    showtimeDate,
    "Today:",
    today,
    "Current Minutes Since Midnight:",
    currentMinutesSinceMidnight
  );

  if (!showtime || typeof showtime !== "string") {
    console.error("Invalid showtime value:", showtime);
    return false; // Invalid showtime
  }

  const [hours, minutes] = showtime.split(":").map(Number);
  const showtimeMinutes = hours * 60 + minutes;

  const isValid =
    showtimeDate !== today ||
    showtimeMinutes <= 60 ||
    showtimeMinutes >= currentMinutesSinceMidnight;

  if (!isValid) {
    console.warn("Showtime failed validation:", {
      showtime,
      showtimeMinutes,
      currentMinutesSinceMidnight,
      showtimeDate,
      today,
    });
  }

  return isValid;
};

const MovieCarousel = ({ selectedSnifs, setSelectedSnifs, setDayOffset }) => {
  const [movies, setMovies] = useState([]);
  const [dayOffsetLocal, setDayOffsetLocal] = useState(0);
  const [sortByTheater, setSortByTheater] = useState(true);

  const offsatDay = getFormattedDate(dayOffsetLocal);
  console.log("Calculated offsatDay (local timezone):", offsatDay);

  useEffect(() => {
    console.log("Calculated offsatDay:", offsatDay);

    console.log("Current local date (browser):", new Date());
    console.log("Current UTC date:", new Date().toISOString());

    const loadMovieData = async () => {
      try {
        // Fetch showtimes and movies data from Supabase
        const { data: showtimesData, error: showtimesError } = await supabase
          .from("showtimes")
          .select("*");
        const { data: moviesData, error: moviesError } = await supabase
          .from("movies")
          .select("*");

        if (showtimesError)
          console.error("Error fetching showtimes:", showtimesError);
        if (moviesError) console.error("Error fetching movies:", moviesError);

        console.log("Fetched showtimesData:", showtimesData);
        console.log("Fetched moviesData:", moviesData);

        const currentTime = new Date();
        const currentMinutesSinceMidnight =
          currentTime.getHours() * 60 + currentTime.getMinutes();
        const today = getFormattedDate(0);

        // Build valid movie titles and movie info map
        let validMovieTitles = new Set();
        let movieInfoMap = {};

        moviesData.forEach((movie) => {
          validMovieTitles.add(movie.title);
          movieInfoMap[movie.title] = {
            time: movie.timetext,
            poster: movie.poster,
            runtime: movie.runtime,
            popularity: movie.popularity,
            imdbRating: movie.imdbRating,
            imdbVotes: movie.imdbVotes,
            rtRating: movie.rtRating,
            imdbID: movie.imdbID,
          };
        });

        console.log("Valid movie titles:", [...validMovieTitles]);
        console.log("Movie info map:", movieInfoMap);

        console.log("Showtimes data:", showtimesData);

        // Filter and map showtimes to enrich with movie info
        const filteredMovies = showtimesData
          .filter((movie) => {
            const isValid =
              movie.datetext === offsatDay &&
              (selectedSnifs.length === 0 ||
                selectedSnifs.includes(movie.snif)) &&
              validMovieTitles.has(movie.title) &&
              isValidShowtime(
                movie.timetext,
                movie.datetext,
                today,
                currentMinutesSinceMidnight
              );

            if (!isValid) {
              console.log("Filtering movie:", {
                datetext: movie.datetext,
                timetext: movie.timetext,
                snif: movie.snif,
                title: movie.title,
              });

              // Check which condition failed
              if (movie.datetext !== offsatDay) {
                console.warn(
                  "Reason: Date mismatch. Expected:",
                  offsatDay,
                  "Got:",
                  movie.datetext
                );
              }

              if (
                !(
                  selectedSnifs.length === 0 ||
                  selectedSnifs.includes(movie.snif)
                )
              ) {
                console.warn(
                  "Reason: Snif mismatch. Selected Snifs:",
                  selectedSnifs,
                  "Got Snif:",
                  movie.snif
                );
              }

              if (!validMovieTitles.has(movie.title)) {
                console.warn(
                  "Reason: Invalid title. Valid Titles:",
                  [...validMovieTitles],
                  "Got Title:",
                  movie.title
                );
              }

              if (
                !isValidShowtime(
                  movie.timetext,
                  movie.datetext,
                  today,
                  currentMinutesSinceMidnight
                )
              ) {
                console.warn(
                  "Reason: Invalid showtime. Showtime:",
                  movie.timetext,
                  "Date:",
                  movie.datetext,
                  "Today:",
                  today,
                  "Current Time (Minutes Since Midnight):",
                  currentMinutesSinceMidnight
                );
              }
            }

            return isValid;
          })
          .map((movie) => ({
            ...movie,
            time: movie.timetext,
            poster:
              movieInfoMap[movie.title]?.poster || "/images/defposter.jpeg",
            runtime: movieInfoMap[movie.title]?.runtime || 0,
            popularity: movieInfoMap[movie.title]?.popularity || 0,
            imdbRating: movieInfoMap[movie.title]?.imdbRating || 0,
            imdbVotes: movieInfoMap[movie.title]?.imdbVotes || 0,
            rtRating: movieInfoMap[movie.title]?.rtRating || 0,
            imdbID: movieInfoMap[movie.title]?.imdbID || 0,
          }));

        console.log("Filtered movies:", filteredMovies);

        setMovies(filteredMovies);
      } catch (err) {
        console.error("Unexpected error while loading movie data:", err);
      }
    };

    loadMovieData();
    setDayOffset(dayOffsetLocal);
  }, [offsatDay, selectedSnifs, dayOffsetLocal, setDayOffset]);

  const handleNextDay = () => setDayOffsetLocal((prev) => prev + 1);
  const handlePrevDay = () =>
    setDayOffsetLocal((prev) => (prev > 0 ? prev - 1 : 0));

  return (
    <div className="main-carousel">
      <CarouselControls
        dayOffsetLocal={dayOffsetLocal}
        offsatDay={offsatDay}
        handlePrevDay={handlePrevDay}
        handleNextDay={handleNextDay}
        selectedSnifs={selectedSnifs}
        setSelectedSnifs={setSelectedSnifs}
        sortByTheater={sortByTheater}
        setSortByTheater={setSortByTheater}
      />
      <div className="carousel-movie-list-area">
        <MoviesSection
          movies={movies}
          selectedSnifs={selectedSnifs}
          sortByTheater={sortByTheater}
        />
      </div>
    </div>
  );
};

export default MovieCarousel;
