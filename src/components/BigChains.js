import React from "react";
import "../componentsCSS/BigChains.css";

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
      // snif: movie.snif,
      runtime: movie.runtime,
      popularity: movie.popularity,
      imdbRating: movie.imdbRating,
      imdbVotes: movie.imdbVotes,
      rtRating: movie.rtRating,
    });
  });

  // Order movie times chronologically (includes midnight showings)
  Object.keys(groupedMovies).forEach((title) => {
    groupedMovies[title].sort((a, b) => {
      const getMinutes = (time) => {
        const [hours, minutes] = time.split(":").map(Number);
        return hours * 60 + minutes;
      };

      return (
        (getMinutes(a.time) <= 60) - (getMinutes(b.time) <= 60) ||
        getMinutes(a.time) - getMinutes(b.time)
      );
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

const areFirstFiveShowtimesRegular = (showtimes) =>
  showtimes.slice(0, 5).every((showtime) => showtime.type === "R");

const BigChains = ({ movies }) => {
  const groupedMovies = groupShowtimesByTitle(movies);
  const sortedTitles = Object.keys(groupedMovies).sort(
    (a, b) => groupedMovies[b][0].popularity - groupedMovies[a][0].popularity
  );

  return (
    <div className="movie-list">
      {/* Iterate through each title in the sorted movie titles */}
      {sortedTitles.map((title) => (
        <div className="movie-block" key={title}>
          {/* Movie poster section */}
          <div className="movie-poster-sub-block">
            <img src={groupedMovies[title][0].poster} alt={`${title} poster`} />
          </div>

          {/* Movie information section */}
          <div className="movie-info-sub-block">
            <div className="movie-title">{title}</div>
            <div className="movie-runtime">
              {groupedMovies[title][0].runtime} minutes
            </div>
            <div className="movie-ratings-block">
              <div className="movie-ratings-sub-block-imdb">
                <img src="/images/imdbLogo.png" alt="IMDB logo" />
                {groupedMovies[title][0].imdbRating}/10 (
                {groupedMovies[title][0].imdbVotes})
              </div>
              <div className="movie-ratings-sub-block-rt">
                <img src="/images/rtLogo.png" alt="Rotten Tomatoes logo" />
                {groupedMovies[title][0].rtRating}%
              </div>
            </div>
          </div>

          {/* Showtimes section */}
          <div className="movie-times-sub-block">
            {/* Iterate through each showtime for the current movie */}
            {groupedMovies[title].map((showtime, index) => (
              // Each individual showtime block
              <div
                className={`each-showtime ${
                  areFirstFiveShowtimesRegular(groupedMovies[title]) &&
                  index < 5
                    ? "smaller-showtime" // Apply smaller height if conditions met
                    : ""
                }`}
                key={index}
              >
                <div className="showtime-background">
                  {/* Display the type if it's not "Regular" */}
                  {showtime.type !== "R" && (
                    <div className="showtime-type">{showtime.type}</div>
                  )}
                  {/* Display the showtime with cinema-specific styling */}
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
      ))}
    </div>
  );
};

export default BigChains;
