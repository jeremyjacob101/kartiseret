import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/ComingSoons.css";

const showtimes_csv = "/CSVs/24-12-24-comingsoons.csv";
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
