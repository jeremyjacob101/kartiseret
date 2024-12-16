import React, { useState, useRef, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/BigChains.css";

const theaters_csv = "/CSVs/theaters.csv";

const defaultPoster = "/images/defposter.jpeg";
const imdbLogo = "/images/imdbLogo.png";
const rtLogo = "/images/rtLogo.png";
const dropdownIcon = "/icons/more-horizontal.svg";
const mapIcon = "/icons/map.svg";

const theaterNames = {
  LC: "Lev Cinema",
  HC: "Hot Cinema",
  CC: "Cinema City",
  YP: "Yes Planet",
  ML: "MovieLand",
  RH: "Rav Hen",
};

const areFirstFourShowtimesRegular = (showtimes) =>
  showtimes.slice(0, 4).every((showtime) => showtime.type === "R");

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

const BigChains = ({ movies, selectedSnifs }) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [sortByTheater, setSortByTheater] = useState(true);
  const [theatersData, setTheatersData] = useState([]);
  const [openMapPopup, setOpenMapPopup] = useState(null); // { title, cinema }
  const dropdownRef = useRef(null);
  const popupRef = useRef(null);

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

  // Close dropdown and map popup on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      const clickedOutsideDropdown =
        dropdownRef.current && !dropdownRef.current.contains(e.target);
      const clickedOutsidePopup =
        popupRef.current && !popupRef.current.contains(e.target);

      if (clickedOutsideDropdown && clickedOutsidePopup) {
        setShowDropdown(false);
        setOpenMapPopup(null);
      } else if (clickedOutsideDropdown) {
        setShowDropdown(false);
      } else if (openMapPopup && clickedOutsidePopup) {
        setOpenMapPopup(null);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [openMapPopup]);

  const toggleMapPopup = (title, cinema) => {
    setOpenMapPopup((prev) =>
      prev && prev.title === title && prev.cinema === cinema
        ? null
        : { title, cinema }
    );
  };

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

      {/* Movies */}
      {sortedTitles.map((title, index) => (
        <>
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
                  ).map(([cinema, showtimes]) => {
                    // Find theaterInfo by chain and the currently selected city
                    const theaterInfo = theatersData.find(
                      (t) => t.chain === cinema && t.city === selectedCity
                    );

                    return (
                      <div key={cinema} className="theater-block">
                        <div className="theater-title">
                          {theaterInfo && (
                            <img
                              src={mapIcon}
                              alt="Map Icon"
                              className="map-icon"
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleMapPopup(title, cinema);
                              }}
                            />
                          )}
                          {theaterNames[cinema] || cinema}
                          {openMapPopup &&
                            openMapPopup.title === title &&
                            openMapPopup.cinema === cinema &&
                            theaterInfo && (
                              <div className="map-popup" ref={popupRef}>
                                <a
                                  href={theaterInfo.location}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                >
                                  {theaterInfo.address}
                                </a>
                              </div>
                            )}
                        </div>
                        <div className="by-theater-showtimes">
                          {showtimes.map((showtime, index) => (
                            <div
                              className={`each-showtime${
                                areFirstFourShowtimesRegular(showtimes) &&
                                index < 4
                                  ? " smaller-showtime"
                                  : ""
                              }`}
                              key={index}
                            >
                              <div className="showtime-background">
                                {showtime.type !== "R" && (
                                  <div className="showtime-type">
                                    {showtime.type}
                                  </div>
                                )}
                                <div
                                  className={`showtime-time ${getCinemaClass(
                                    showtime.cinema
                                  )}`}
                                >
                                  {showtime.time}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })
                : groupedMovies[title].map((showtime, index) => (
                    <div
                      className={`each-showtime ${
                        areFirstFourShowtimesRegular(groupedMovies[title]) &&
                        index < 4
                          ? "smaller-showtime"
                          : ""
                      }`}
                      key={index}
                    >
                      <div className="showtime-background">
                        {showtime.type !== "R" && (
                          <div className="showtime-type">{showtime.type}</div>
                        )}
                        <div
                          className={`showtime-time ${getCinemaClass(
                            showtime.cinema
                          )}`}
                        >
                          {showtime.time}
                        </div>
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
