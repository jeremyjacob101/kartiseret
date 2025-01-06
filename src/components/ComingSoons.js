import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/ComingSoons.css";

const showtimes_csv = "/CSVs/25-01-01-comingsoons.csv";
const defaultPoster = "/images/defposter.jpeg";

// Function to check if the showtime date is valid
const isValidShowtimeDate = (date) => {
  if (!date) return false;
  const [year, month, day] = date.split("-").map(Number);
  const showtimeDate = new Date(2000 + year, month - 1, day);
  const now = new Date();
  return showtimeDate >= now;
};

const ComingSoons = ({ selectedSnifs }) => {
  const [movies, setMovies] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const loadShowtimeData = async () => {
      const showtimesData = await (await fetch(showtimes_csv)).text();

      Papa.parse(showtimesData, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          const filteredMovies = results.data.filter((movie) => {
            // Check fields and valid date
            return movie.datetext && movie.title && isValidShowtimeDate(movie.datetext);
          });

          setMovies(filteredMovies);
        },
      });
    };

    loadShowtimeData();
  }, [selectedSnifs]);

  if (!movies.length) {
    return null;
  }

  const toggleSection = () => {
    setIsOpen((prevState) => !prevState);
  };

  return (
    <>
      <h2 className="coming-soon-header-name" onClick={toggleSection}>
        <span>Coming Soon</span>
        <img
          src={isOpen ? "/icons/chevron-up.svg" : "/icons/chevron-down.svg"}
          alt={isOpen ? "Close" : "Open"}
          className="coming-soon-chevron"
        />
      </h2>
      <div
        className={`coming-soon-carousel-wrapper ${isOpen ? "open" : "closed"}`}
      >
        <div className="coming-soon-carousel">
          <div className="coming-soon-carousel-inner">
            {movies.map((movie, index) => {
              const { datetext, title, poster, imdbID } = movie;

              return (
                <div key={index} className="coming-soon-card">
                  <a
                    href={`https://www.imdb.com/title/${imdbID}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <img
                      src={poster || defaultPoster}
                      alt={title}
                      className="coming-soon-poster"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = defaultPoster;
                      }}
                    />
                  </a>

                  <div className="coming-soon-details">
                    <h3 className="coming-soon-title">{title}</h3>
                    <p>{datetext.split("-").reverse().slice(0, 2).join(".")}</p>
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
