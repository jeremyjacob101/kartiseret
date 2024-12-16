import React, { useState, useRef, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/MoviesSection.css";
import MovieTimesSection from "./MovieTimesSection"; // Import the showtimes component

const theaters_csv = "/CSVs/theaters.csv";
const dropdownIcon = "/icons/more-horizontal.svg";
const defaultPoster = "/images/defposter.jpeg";
const imdbLogo = "/images/imdbLogo.png";
const rtLogo = "/images/rtLogo.png";

const MoviesSection = ({ movies, selectedSnifs }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [sortByTheater, setSortByTheater] = useState(true);
  const [theatersData, setTheatersData] = useState([]);
  const dropdownRef = useRef(null);

  // Group movies by title
  const groupShowtimesByTitle = (movies) => {
    const groupedMovies = {};

    movies.forEach((movie) => {
      if (!groupedMovies[movie.title]) {
        groupedMovies[movie.title] = [];
      }
      groupedMovies[movie.title].push({
        time: movie.time,
        cinema: movie.cinema,
        type: movie.type,
        poster: movie.poster,
        runtime: movie.runtime,
        popularity: movie.popularity,
        imdbRating: movie.imdbRating,
        imdbVotes: movie.imdbVotes,
        rtRating: movie.rtRating,
      });
    });

    Object.keys(groupedMovies).forEach((title) => {
      groupedMovies[title].sort((a, b) => {
        const getMinutes = (time) => {
          const [hours, minutes] = time.split(":").map(Number);
          return hours * 60 + minutes;
        };
        return getMinutes(a.time) - getMinutes(b.time);
      });
    });

    return groupedMovies;
  };

  const groupedMovies = groupShowtimesByTitle(movies);
  const sortedTitles = Object.keys(groupedMovies).sort(
    (a, b) => groupedMovies[b][0].popularity - groupedMovies[a][0].popularity
  );

  useEffect(() => {
    const loadTheatersData = async () => {
      const theatersText = await (await fetch(theaters_csv)).text();

      Papa.parse(theatersText, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          // Filter out rows that don't have a chain
          setTheatersData(results.data.filter((d) => d.chain));
        },
      });
    };

    loadTheatersData();
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      const clickedOutsideDropdown =
        dropdownRef.current && !dropdownRef.current.contains(e.target);

      if (clickedOutsideDropdown) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  const selectedCity =
    selectedSnifs && selectedSnifs.length > 0 ? selectedSnifs[0] : null;

  return (
    <div className="movie-list">
      <div className="by-theater-dropdown-container" ref={dropdownRef}>
        <img
          src={dropdownIcon}
          alt="Options"
          className="by-theater-dropdown-icon"
          onClick={() => setShowDropdown((prev) => !prev)}
        />
        {showDropdown && (
          <div className="by-theater-dropdown-menu">
            <label>
              <input
                type="checkbox"
                checked={sortByTheater}
                onChange={() => {
                  setSortByTheater((prev) => !prev);
                  setShowDropdown(false); // Close dropdown after selection
                }}
              />
              Display by theater
            </label>
          </div>
        )}
      </div>

      {sortedTitles.map((title, index) => (
        <>
          {index !== 0 && <div className="divider-line"></div>}
          <div className="movie-block">
            {/* Movie Poster and Info */}
            <div className="movie-poster-and-info-section">
              {/* Movie Poster */}
              <div className="movie-poster-sub-block">
                <img
                  src={groupedMovies[title][0].poster || defaultPoster}
                  alt={`${title} poster`}
                  onError={(e) => (e.target.src = defaultPoster)}
                />
              </div>

              {/* Movie Info */}
              <div className="movie-info-sub-block">
                <div className="movie-top-sub-block">
                  <div className="movie-title">{title}</div>
                  <div className="movie-runtime">
                    {groupedMovies[title][0].runtime} minutes
                  </div>
                </div>

                {/* Ratings */}
                <div className="movie-ratings-block">
                  <div className="movie-ratings-sub-block-imdb">
                    <img src={imdbLogo} alt="IMDB logo" />
                    {groupedMovies[title][0].imdbRating}/10 (
                    {groupedMovies[title][0].imdbVotes})
                  </div>
                  <div className="movie-ratings-sub-block-rt">
                    <img src={rtLogo} alt="Rotten Tomatoes logo" />
                    {groupedMovies[title][0].rtRating}%
                  </div>
                </div>
              </div>
            </div>

            {/* Showtimes Section */}
            <MovieTimesSection
              title={title}
              showtimes={groupedMovies[title]}
              sortByTheater={sortByTheater}
              theatersData={theatersData}
              selectedCity={selectedCity}
            />
          </div>
        </>
      ))}
    </div>
  );
};

export default MoviesSection;
