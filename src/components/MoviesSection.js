import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/MoviesSection.css";
import MovieTimesSection from "./MovieTimesSection";

const theaters_csv = "/CSVs/theaters.csv";
const defaultPoster = "/images/defposter.jpeg";
const imdbLogo = "/images/imdbLogo.png";
const rtLogo = "/images/rtLogo.png";

const MoviesSection = ({ movies, selectedSnifs, sortByTheater }) => {
  const [theatersData, setTheatersData] = useState([]);

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
        snif: movie.snif,
        timeHref: movie.timeHref,
        poster: movie.poster,
        runtime: movie.runtime,
        popularity: movie.popularity,
        imdbRating: movie.imdbRating,
        imdbVotes: movie.imdbVotes,
        rtRating: movie.rtRating,
        imdbID: movie.imdbID,
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
          setTheatersData(results.data.filter((d) => d.chain));
        },
      });
    };

    loadTheatersData();
  }, []);

  const selectedCity =
    selectedSnifs && selectedSnifs.length > 0 ? selectedSnifs[0] : null;

  return (
    <div className="movie-list">
      {sortedTitles.map((title, index) => (
        <>
          {index !== 0 && <div className="divider-line"></div>}
          <div className="movie-block">
            <div className="movie-poster-and-info-section">
              <div className="movie-poster-sub-block">
                <img
                  src={groupedMovies[title][0].poster || defaultPoster}
                  alt={`${title} poster`}
                  onError={(e) => (e.target.src = defaultPoster)}
                />
              </div>
              <div className="movie-info-sub-block">
                <div className="movie-top-sub-block">
                  <div className="movie-title">{title}</div>
                  <div className="movie-runtime">
                    {groupedMovies[title][0].runtime} minutes
                  </div>
                </div>
                <div className="movie-ratings-block">
                  <div className="movie-ratings-sub-block-imdb">
                    <a
                      href={`https://www.imdb.com/title/${groupedMovies[title][0].imdbID}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ textDecoration: "none", color: "inherit" }}
                    >
                      <img src={imdbLogo} alt="IMDB logo" />
                    </a>
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
