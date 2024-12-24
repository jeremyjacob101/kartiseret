import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/ComingSoons.css";

const showtimes_csv = "/CSVs/24-12-24-comingsoons.csv";
const defaultPoster = "/images/defposter.jpeg";

// Function to check if the showtime date is valid
const isValidShowtimeDate = (date) => {
  if (!date) return false; // Ensure date is defined
  const [year, month, day] = date.split("-").map(Number); // Parse as numbers
  const showtimeDate = new Date(2000 + year, month - 1, day); // Add 2000 to ensure full year
  const now = new Date();

  return showtimeDate >= now;
};

const ComingSoons = ({ selectedSnifs }) => {
  const [movies, setMovies] = useState([]);
  const [isOpen, setIsOpen] = useState(false); // State to manage open/close functionality

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
              const { date, title, poster } = movie;

              return (
                <div key={index} className="coming-soon-card">
                  <img
                    src={poster || defaultPoster}
                    alt={title}
                    className="coming-soon-poster"
                    onError={(e) => {
                      e.target.onerror = null; // Prevent infinite loop in case default poster also fails
                      e.target.src = defaultPoster;
                    }}
                  />
                  <div className="coming-soon-details">
                    <h3 className="coming-soon-title">{title}</h3>
                    <p> {date.split("-").reverse().slice(0, 2).join(".")} </p>
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
