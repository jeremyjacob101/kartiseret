import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/Cinemateques.css";

const showtimes_csv = "/CSVs/19-12-24-cinemateques.csv";

const ChevronUp = "/icons/chevron-up.svg";
const ChevronDown = "/icons/chevron-down.svg";
const defaultPoster = "/images/defposter.jpeg";

const cinematequeCities = {
  HFCT: "Haifa",
  JLMCT: "Jerusalem",
  HRZCT: "Herziliya",
  TLVCT: "Tel Aviv",
  JAFC: "Tel Aviv"
};

// Function to check if the showtime is valid
const isValidShowtime = (date, time) => {
  const [day, month, year] = date.split("/").map(Number);
  const [hours, minutes] = time.split(":").map(Number);

  const showtimeDate = new Date(year, month - 1, day, hours, minutes);
  const now = new Date();

  return showtimeDate >= now;
};

const Cinemateques = ({ selectedSnifs }) => {
  const [cinemaMovies, setCinemaMovies] = useState({});
  const [openSections, setOpenSections] = useState({});

  useEffect(() => {
    const loadShowtimeData = async () => {
      const showtimesData = await (await fetch(showtimes_csv)).text();

      Papa.parse(showtimesData, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          // Group movies by cinema
          const groupedMovies = results.data.reduce((acc, movie) => {
            const cinema = movie.cinema;
            const city = cinema ? cinematequeCities[cinema] : undefined;
            const isSelected =
              selectedSnifs.length === 0 || selectedSnifs.includes(city);

            // Only include if showtime is valid
            if (city && isSelected && isValidShowtime(movie.date, movie.time)) {
              if (!acc[cinema]) acc[cinema] = [];
              acc[cinema].push(movie);
            }
            return acc;
          }, {});

          setCinemaMovies(groupedMovies);
        },
      });
    };

    loadShowtimeData();
  }, [selectedSnifs]);

  const toggleSection = (cinema) => {
    setOpenSections((prevState) => ({
      ...prevState,
      [cinema]: !prevState[cinema],
    }));
  };

  if (!Object.keys(cinemaMovies).length) {
    return null;
  }

  return (
    <>
      {Object.entries(cinemaMovies).map(([cinema, movies]) => (
        <div key={cinema} className="cinemateque-section">
          <h2
            className="cinemateque-header-name"
            onClick={() => toggleSection(cinema)}
          >
            <span>
              {cinema === "JAFC"
                ? "Jaffa Cinema"
                : `Cinemateque`}
            </span>
            <img
              src={openSections[cinema] ? ChevronUp : ChevronDown}
              alt={openSections[cinema] ? "Close" : "Open"}
              className="cinemateque-chevron"
            />
          </h2>
          <div
            className={`cinemateque-carousel-wrapper ${
              openSections[cinema] ? "open" : "closed"
            }`}
          >
            <div className="cinemateque-carousel">
              <div className="cinemateque-carousel-inner">
                {movies.map((movie, index) => {
                  const { date, time, title, year, href, poster } = movie;
                  const posterSrc =
                    !poster || poster === "N/A" ? defaultPoster : poster;

                  return (
                    <div key={index} className="cinemateque-card">
                      <a href={href} target="_blank" rel="noopener noreferrer">
                        <img
                          src={posterSrc || defaultPoster}
                          alt={title}
                          className="cinemateque-poster"
                          loading="lazy"
                          onError={(e) => {
                            e.target.onerror = null; // Prevent infinite loop in case default poster also fails
                            e.target.src = defaultPoster;
                          }}
                        />
                      </a>
                      <div className="cinemateque-details">
                        <h3 className="cinemateque-title">{title}</h3>
                        <h3>({year})</h3>
                        <p>
                          {date} - {time}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      ))}
    </>
  );
};

export default Cinemateques;
