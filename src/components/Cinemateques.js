import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/Cinemateques.css";

const showtimes_csv = "/CSVs/31-10-24-cinemateques.csv";
const defaultPoster = "/images/defposter.jpeg";

const cinematequeCities = {
  HFCT: "Haifa",
  JLMCT: "Jerusalem",
  HRZCT: "Herziliya",
  TLVCT: "Tel Aviv",
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
  const [movies, setMovies] = useState([]);
  const [visibleMovies, setVisibleMovies] = useState([]);

  useEffect(() => {
    const loadShowtimeData = async () => {
      const showtimesData = await (await fetch(showtimes_csv)).text();

      Papa.parse(showtimesData, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          const filteredMovies = results.data.filter((movie) => {
            const cinema = movie.cinema;
            const city = cinema ? cinematequeCities[cinema] : undefined;
            const isSelected =
              selectedSnifs.length === 0 || selectedSnifs.includes(city);

            // Only include if showtime is valid
            return (
              city && isSelected && isValidShowtime(movie.date, movie.time)
            );
          });

          setMovies(filteredMovies);
          setVisibleMovies(filteredMovies.map((_, index) => index));
        },
      });
    };

    loadShowtimeData();
  }, [selectedSnifs]);

  if (!movies.length) {
    return <p>No showtimes available for the selected city/cities.</p>;
  }

  return (
    <>
      <h2 className="cinemateque-header-name">
        {movies.length > 0
          ? `${cinematequeCities[movies[0].cinema]} Cinemateque`
          : "Cinemateque"}
      </h2>
      <div className="cinemateque-carousel-wrapper">
        <div className="cinemateque-carousel">
          <div className="cinemateque-carousel-inner">
            {movies.map((movie, index) => {
              const { date, time, title, year, href, poster } = movie;
              const isVisible = visibleMovies.includes(index);
              const posterSrc =
                !poster || poster === "N/A" ? defaultPoster : poster;

              return (
                <div
                  key={index}
                  className="cinemateque-card"
                  data-index={index}
                >
                  {isVisible ? (
                    <a href={href} target="_blank" rel="noopener noreferrer">
                      <img
                        src={posterSrc}
                        alt={title}
                        className="cinemateque-poster"
                        loading="lazy"
                        onError={(e) => {
                          if (e.target.src !== defaultPoster) {
                            e.target.src = defaultPoster;
                          }
                        }}
                      />
                    </a>
                  ) : (
                    <div className="cinemateque-placeholder">Loading...</div>
                  )}
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
    </>
  );
};

export default Cinemateques;
