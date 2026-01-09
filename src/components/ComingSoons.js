import React, { useState, useEffect } from "react";
import { supabase } from "../supabaseClient";
import "../componentsCSS/ComingSoons.css";

const defaultPoster = "/images/defposter.jpeg";

const isValidShowtimeDate = (date) => {
  if (!date) return false;

  const showtimeDate = new Date(date);
  if (Number.isNaN(showtimeDate.getTime())) return false;

  const now = new Date();
  now.setHours(0, 0, 0, 0);

  return showtimeDate >= now;
};

const ComingSoons = ({ selectedSnifs }) => {
  const [movies, setMovies] = useState([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    const loadShowtimeData = async () => {
      const { data: showtimes } = await supabase
        .from("finalSoons")
        .select("*");

      const filteredMovies = showtimes
        .filter((movie) => {
          return (
            movie.release_date &&
            movie.english_title &&
            isValidShowtimeDate(movie.release_date)
          );
        })
        .sort((a, b) => {
          const da = new Date(a.release_date);
          const db = new Date(b.release_date);
          return da - db;
        });

      setMovies(filteredMovies);
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
    <div className="coming-soon-section">
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
              const { release_date, english_title, poster, imdb_id } = movie;

              return (
                <div key={index} className="coming-soon-card">
                  <a
                    href={`https://www.imdb.com/title/${imdb_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <img
                      src={poster || defaultPoster}
                      alt={english_title}
                      className="coming-soon-poster"
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = defaultPoster;
                      }}
                    />
                  </a>

                  <div className="coming-soon-details">
                    <h3 className="coming-soon-title">{english_title}</h3>
                    <p>
                      {release_date.split("-").reverse().slice(0, 2).join(".")}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComingSoons;
