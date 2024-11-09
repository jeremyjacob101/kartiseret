import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/ComingSoons.css";

const showtimes_csv = "/CSVs/05-11-24-comingsoons.csv";
const defaultPoster = "/images/defposter.jpeg";

// Function to check if the showtime date is valid
const isValidShowtimeDate = (date) => {
  if (!date) return false; // Ensure date is defined
  const [day, month, year] = date.split("/").map(Number);
  const showtimeDate = new Date(year, month - 1, day);
  const now = new Date();

  return showtimeDate >= now;
};

const ComingSoons = ({ selectedSnifs }) => {
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
            // Ensure all required fields are present and valid
            return (
              movie.date &&
              movie.title &&
              movie.poster &&
              isValidShowtimeDate(movie.date)
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
    return null;
  }

  return (
    <>
      <h2 className="coming-soon-header-name">
        <span>Coming Soon</span>
      </h2>
      <div className="coming-soon-carousel-wrapper">
        <div className="coming-soon-carousel">
          <div className="coming-soon-carousel-inner">
            {movies.map((movie, index) => {
              const { date, title, poster } = movie;
              const isVisible = visibleMovies.includes(index);
              const posterSrc =
                !poster || poster === "N/A" ? defaultPoster : poster;

              return (
                <div
                  key={index}
                  className="coming-soon-card"
                  data-index={index}
                >
                  {isVisible ? (
                    <a href="#" target="_blank" rel="noopener noreferrer">
                      <img
                        src={posterSrc}
                        alt={title}
                        className="coming-soon-poster"
                        loading="lazy"
                        onError={(e) => {
                          if (e.target.src !== defaultPoster) {
                            e.target.src = defaultPoster;
                          }
                        }}
                      />
                    </a>
                  ) : (
                    <div className="coming-soon-placeholder">Loading...</div>
                  )}
                  <div className="coming-soon-details">
                    <h3 className="coming-soon-title">{title}</h3>
                    <p>{date}</p>
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

export default ComingSoons;
