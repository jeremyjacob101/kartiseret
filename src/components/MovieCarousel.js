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
  const [dayOffsetLocal, setDayOffsetLocal] = useState(0);
  const [sortByTheater, setSortByTheater] = useState(true);

  const offsatDay = getFormattedDate(dayOffsetLocal);

  const fetchAllShowtimesForDay = async (dayString) => {
    const chunkSize = 1000;
    let allShowtimes = [];
    let from = 0;

    while (true) {
      const { data, error } = await supabase
        .from("showtimes")
        .select("*")
        .eq("datetext", dayString)
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
        .from("movies")
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
        validMovieTitles.add(movie.title);
        movieInfoMap[movie.title] = {
          poster: movie.poster,
          runtime: movie.runtime,
          popularity: movie.popularity,
          imdbRating: movie.imdbRating,
          imdbVotes: movie.imdbVotes,
          rtRating: movie.rtRating,
          imdbID: movie.imdbID,
        };
      });

      const filteredMovies = showtimesData
        .filter(
          (showtime) =>
            showtime.datetext === offsatDay &&
            (selectedSnifs.length === 0 ||
              selectedSnifs.includes(showtime.snif)) &&
            validMovieTitles.has(showtime.title) &&
            isValidShowtime(
              showtime.timetext,
              showtime.datetext,
              today,
              currentMinutesSinceMidnight
            )
        )
        .map((showtime) => ({
          ...showtime,
          poster: movieInfoMap[showtime.title]?.poster || "",
          runtime: movieInfoMap[showtime.title]?.runtime || 0,
          popularity: movieInfoMap[showtime.title]?.popularity || 0,
          imdbRating: movieInfoMap[showtime.title]?.imdbRating || 0,
          imdbVotes: movieInfoMap[showtime.title]?.imdbVotes || 0,
          rtRating: movieInfoMap[showtime.title]?.rtRating || 0,
          imdbID: movieInfoMap[showtime.title]?.imdbID || "",
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
