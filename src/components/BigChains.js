import React, { useState, useRef, useEffect } from "react";
import "../componentsCSS/BigChains.css";

const defaultPoster = "/images/defposter.jpeg";
const imdbLogo = "/images/imdbLogo.png";
const rtLogo = "/images/rtLogo.png";
const dropdownIcon = "/icons/more-horizontal.svg";

const theaterNames = {
  LC: "Lev Cinema",
  HC: "Hot Cinema",
  CC: "Cinema City",
  YP: "Yes Planet",
  ML: "MovieLand",
  RH: "Rav Hen",
};

const getCinemaClass = (cinema) => {
  switch (cinema) {
    case "YP":
      return "yes-planet";
    case "CC":
      return "cinema-city";
    case "LC":
      return "lev-cinema";
    case "HC":
      return "hot-cinema";
    case "ML":
      return "movieland-cinema";
    case "RH":
      return "rav-hen-cinema";
    default:
      return "";
  }
};

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

const groupShowtimesByTheater = (showtimes) => {
  const groupedByTheater = {};

  showtimes.forEach((showtime) => {
    if (!groupedByTheater[showtime.cinema]) {
      groupedByTheater[showtime.cinema] = [];
    }
    groupedByTheater[showtime.cinema].push(showtime);
  });

  Object.values(groupedByTheater).forEach((group) =>
    group.sort((a, b) => {
      const getMinutes = (time) => {
        const [hours, minutes] = time.split(":").map(Number);
        return hours * 60 + minutes;
      };
      return getMinutes(a.time) - getMinutes(b.time);
    })
  );

  return groupedByTheater;
};

const BigChains = ({ movies }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [sortByTheater, setSortByTheater] = useState(true);
  const dropdownRef = useRef(null);

  const groupedMovies = groupShowtimesByTitle(movies);
  const sortedTitles = Object.keys(groupedMovies).sort(
    (a, b) => groupedMovies[b][0].popularity - groupedMovies[a][0].popularity
  );

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  return (
    <div className="movie-list">
      {/* Dropdown Button */}
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

      {/* Movies */}
      {sortedTitles.map((title, index) => (
        <>
          {/* Divider Lines */}
          {index !== 0 && <div className="divider-line"></div>}
          <div className="movie-block">
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
                <div className="movie-title">{title}</div>
                <div className="movie-runtime">
                  {groupedMovies[title][0].runtime} minutes
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

            {/* Showtimes */}
            <div
              className={
                sortByTheater
                  ? "by-theater-movie-times-sub-block"
                  : "movie-times-sub-block"
              }
            >
              {sortByTheater
                ? Object.entries(
                    groupShowtimesByTheater(groupedMovies[title])
                  ).map(([cinema, showtimes]) => (
                    <div key={cinema} className="theater-block">
                      <div className={`theater-title`}>
                        {theaterNames[cinema] || cinema}
                      </div>
                      <div className="by-theater-showtimes">
                        {showtimes.map((showtime, index) => (
                          <div className="each-showtime" key={index}>
                            <div
                              className={`showtime-time ${getCinemaClass(
                                showtime.cinema
                              )}`}
                            >
                              {showtime.time}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))
                : groupedMovies[title].map((showtime, index) => (
                    <div className="each-showtime" key={index}>
                      <div
                        className={`showtime-time ${getCinemaClass(
                          showtime.cinema
                        )}`}
                      >
                        {showtime.time}
                      </div>
                    </div>
                  ))}
            </div>
          </div>
        </>
      ))}
    </div>
  );
};

export default BigChains;
