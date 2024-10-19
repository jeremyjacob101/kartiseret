import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/MovieCarousel.css";
import BigChains from "./BigChains.js";

const showtimes_csv = "/CSVs/20-10-24-showtimes.csv";
const movies_csv = "/CSVs/20-10-24-movies.csv"; // The new CSV file for posters, titles, and popularity

const getFormattedDate = (dayOffset) => {
  const today = new Date();
  today.setDate(today.getDate() + dayOffset);
  return `${String(today.getDate()).padStart(2, "0")}/${String(
    today.getMonth() + 1
  ).padStart(2, "0")}/${today.getFullYear()}`;
};

const isValidShowtime = (
  showtime,
  showtimeDate,
  today,
  currentMinutesSinceMidnight
) => {
  const [hours, minutes] = showtime.split(":").map(Number);
  const showtimeMinutes = hours * 60 + minutes;

  return (
    showtimeDate !== today ||
    showtimeMinutes <= 60 ||
    showtimeMinutes >= currentMinutesSinceMidnight - 30
  );
};

const MovieCarousel = ({ selectedSnifs }) => {
  const [movies, setMovies] = useState([]);
  const [dayOffset, setDayOffset] = useState(0);

  const offsatDay = getFormattedDate(dayOffset);

  useEffect(() => {
    const loadMovieData = async () => {
      const currentTime = new Date();
      const currentMinutesSinceMidnight =
        currentTime.getHours() * 60 + currentTime.getMinutes();
      const today = getFormattedDate(0); // Today's date in the same format as showtimes

      // Load CSVs
      const showtimes_result = await (await fetch(showtimes_csv)).body
        .getReader()
        .read();
      const showtimesData = new TextDecoder("utf-8").decode(
        showtimes_result.value
      );
      const movies_result = await (await fetch(movies_csv)).body
        .getReader()
        .read();
      const moviesData = new TextDecoder("utf-8").decode(movies_result.value);

      // Parse the movies CSV to create a set of valid movie titles and poster/runtimes/popularity
      let validMovieTitles = new Set();
      let movieInfoMap = {};

      Papa.parse(moviesData, {
        header: true,
        dynamicTyping: true,

        complete: (results) => {
          results.data.forEach((movie) => {
            validMovieTitles.add(movie.title);
            movieInfoMap[movie.title] = {
              poster: movie.poster,
              runtime: movie.runtime,
              popularity: movie.popularity,
              imdbScore: movie.imdbScore,
              imdbVotes: movie.imdbVotes,
              rtScore: movie.rtScore,
            };
          });
        },
      });

      // Parse the showtimes CSV and filter by selected snifs, date, and valid title
      Papa.parse(showtimesData, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          const filteredMovies = results.data
            .filter(
              (movie) =>
                movie.date === offsatDay &&
                (selectedSnifs.length === 0 ||
                  selectedSnifs.includes(movie.snif)) &&
                validMovieTitles.has(movie.title) &&
                isValidShowtime(
                  movie.time,
                  movie.date,
                  today,
                  currentMinutesSinceMidnight
                ) // Check only today’s showtimes
            )
            .map((movie) => ({
              ...movie,
              poster: movieInfoMap[movie.title]?.poster || null, // Add the poster URL or null if none exists
              runtime: movieInfoMap[movie.title]?.runtime || null, // Add runtime or null if not found
              popularity: movieInfoMap[movie.title]?.popularity || 0, // Add popularity or default to 0 if not found
              imdbScore: movieInfoMap[movie.title]?.imdbScore || 0, // Add popularity or default to 0 if not found              popularity: movieInfoMap[movie.title]?.popularity || 0, // Add popularity or default to 0 if not found
              imdbVotes: movieInfoMap[movie.title]?.imdbVotes || 0, // Add popularity or default to 0 if not found
              rtScore: movieInfoMap[movie.title]?.rtScore || 0, // Add popularity or default to 0 if not found
            }));
          setMovies(filteredMovies);
        },
      });
    };

    loadMovieData();
  }, [offsatDay, selectedSnifs]); // Re-fetch when the day or snif selection changes

  const handleNextDay = () => {
    setDayOffset(dayOffset + 1);
  };

  const handlePrevDay = () => {
    if (dayOffset > 0) {
      setDayOffset(dayOffset - 1);
    }
  };

  return (
    <div className="main-carousel">
      <div className="carousel-controls">
        <button onClick={handlePrevDay} disabled={dayOffset === 0}>
          Previous
        </button>
        <div className="carousel-current-date">{offsatDay}</div>
        <button onClick={handleNextDay}>Next</button>
      </div>

      <div className="carousel-movie-list-area">
        <BigChains movies={movies} />
      </div>
    </div>
  );
};

export default MovieCarousel;
