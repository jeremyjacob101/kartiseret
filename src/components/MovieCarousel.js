import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/MovieCarousel.css";
import MoviesSection from "./MoviesSection";
import CarouselControls from "./CarouselControls"; // Import new component

const showtimes_csv = "/CSVs/25-01-01-showtimes.csv";
const movies_csv = "/CSVs/25-01-01-movies.csv";

// Changed only the return value from "dd/mm/yyyy" to "yy-mm-dd"
const getFormattedDate = (dayOffset) => {
  const today = new Date();
  today.setDate(today.getDate() + dayOffset);

  const year = String(today.getFullYear()).slice(-2);
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
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
    showtimeMinutes >= currentMinutesSinceMidnight
  );
};

const MovieCarousel = ({ selectedSnifs, setSelectedSnifs, setDayOffset }) => {
  const [movies, setMovies] = useState([]);
  const [dayOffsetLocal, setDayOffsetLocal] = useState(0); // Local dayOffset state
  const [sortByTheater, setSortByTheater] = useState(true);

  const offsatDay = getFormattedDate(dayOffsetLocal);

  useEffect(() => {
    const loadMovieData = async () => {
      const showtimesData = await (await fetch(showtimes_csv)).text();
      const moviesData = await (await fetch(movies_csv)).text();

      const currentTime = new Date();
      const currentMinutesSinceMidnight =
        currentTime.getHours() * 60 + currentTime.getMinutes();
      const today = getFormattedDate(0);

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
              imdbRating: movie.imdbRating,
              imdbVotes: movie.imdbVotes,
              rtRating: movie.rtRating,
            };
          });
        },
      });

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
                )
            )
            .map((movie) => ({
              ...movie,
              poster: movieInfoMap[movie.title]?.poster || null,
              runtime: movieInfoMap[movie.title]?.runtime || null,
              popularity: movieInfoMap[movie.title]?.popularity || 0,
              imdbRating: movieInfoMap[movie.title]?.imdbRating || 0,
              imdbVotes: movieInfoMap[movie.title]?.imdbVotes || 0,
              rtRating: movieInfoMap[movie.title]?.rtRating || 0,
            }));
          setMovies(filteredMovies);
        },
      });
    };

    loadMovieData();
    setDayOffset(dayOffsetLocal); // Update global dayOffset when local dayOffset changes
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
        selectedSnifs={selectedSnifs} // Pass props to CarouselControls
        setSelectedSnifs={setSelectedSnifs} // Pass props to CarouselControls
        sortByTheater={sortByTheater} // Pass to CarouselControls
        setSortByTheater={setSortByTheater} // Pass to CarouselControls
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
