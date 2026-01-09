import React, { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";
import "../componentsCSS/MovieCarousel.css";
import MoviesSection from "./MoviesSection";
import CarouselControls from "./CarouselControls";

const getFormattedDate = (dayOffset) => {
  const today = new Date();
  today.setDate(today.getDate() + dayOffset);

  const year = today.getFullYear(); // full 4 digits now
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
  const [hours, minutes] = showtime.split(":").slice(0, 2).map(Number);
  const showtimeMinutes = hours * 60 + minutes;

  return (
    showtimeDate !== today ||
    showtimeMinutes <= 60 ||
    showtimeMinutes >= currentMinutesSinceMidnight
  );
};

const MovieCarousel = ({ selectedSnifs, setSelectedSnifs, setDayOffset }) => {
  const [movies, setMovies] = useState([]);
  const [dayOffsetLocal, setDayOffsetLocal] = useState(0);
  const [sortByTheater, setSortByTheater] = useState(true);

  const offsatDay = getFormattedDate(dayOffsetLocal);

  const fetchAllShowtimesForDay = async (dayString) => {
    const chunkSize = 1000;
    let allShowtimes = [];
    let from = 0;

    while (true) {
      const { data, error } = await supabase
        .from("finalShowtimes")
        .select("*")
        .eq("date_of_showing", dayString)
        .range(from, from + chunkSize - 1);

      if (error) {
        console.error("Error fetching chunk:", error);
        break;
      }

      if (!data || data.length === 0) {
        break;
      }

      allShowtimes = allShowtimes.concat(data);
      // If we got less than chunkSize, we reached the end for this day
      if (data.length < chunkSize) {
        break;
      }

      from += chunkSize;
    }

    return allShowtimes;
  };

  useEffect(() => {
    const loadMovieData = async () => {
      const { data: moviesData } = await supabase
        .from("finalMovies")
        .select("*");

      const showtimesData = await fetchAllShowtimesForDay(offsatDay);

      // console.log("Filtering for offsatDay =", offsatDay);
      // console.log("Supabase showtimesData:", showtimesData);

      const currentTime = new Date();
      const currentMinutesSinceMidnight =
        currentTime.getHours() * 60 + currentTime.getMinutes();
      const today = getFormattedDate(0);

      let validMovieTitles = new Set();
      let movieInfoMap = {};

      moviesData.forEach((movie) => {
        validMovieTitles.add(movie.english_title);
        movieInfoMap[movie.english_title] = {
          poster: movie.poster,
          runtime: movie.runtime,
          popularity: movie.popularity,
          imdbRating: movie.imdbRating,
          imdbVotes: movie.imdbVotes,
          rtRating: movie.rtRating,
          tmdb_id: movie.tmdb_id,
        };
      });

      const filteredMovies = showtimesData
        .filter(
          (showtime) =>
            showtime.date_of_showing === offsatDay &&
            (selectedSnifs.length === 0 ||
              selectedSnifs.includes(showtime.screening_city)) &&
            validMovieTitles.has(showtime.english_title) &&
            isValidShowtime(
              showtime.showtime,
              showtime.date_of_showing,
              today,
              currentMinutesSinceMidnight
            )
        )
        .map((showtime) => ({
          ...showtime,
          poster: movieInfoMap[showtime.english_title]?.poster || "",
          runtime: movieInfoMap[showtime.english_title]?.runtime || 0,
          popularity: movieInfoMap[showtime.english_title]?.popularity || 0,
          imdbRating: movieInfoMap[showtime.english_title]?.imdbRating || 0,
          imdbVotes: movieInfoMap[showtime.english_title]?.imdbVotes || 0,
          rtRating: movieInfoMap[showtime.english_title]?.rtRating || 0,
          tmdb_id: movieInfoMap[showtime.english_title]?.tmdb_id || "",
        }));

      setMovies(filteredMovies);
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
