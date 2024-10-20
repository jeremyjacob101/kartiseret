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
      imdbScore: movie.imdbScore,
      imdbVotes: movie.imdbVotes,
      rtScore: movie.rtScore,
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
    case "Yes Planet":
      return "yes-planet";
    case "Cinema City":
      return "cinema-city";
    case "Lev Cinema":
      return "lev-cinema";
    case "Hot Cinema":
      return "hot-cinema";
    case "MovieLand":
      return "movieland-cinema";
    case "Rav Hen":
      return "rav-hen-cinema";
    default:
      return "";
  }
};

const areFirstFiveShowtimesRegular = (showtimes) =>
  showtimes.slice(0, 5).every((showtime) => showtime.type === "Regular");

const BigChains = ({ movies }) => {
  const groupedMovies = groupShowtimesByTitle(movies);
  const sortedTitles = Object.keys(groupedMovies).sort(
    (a, b) => groupedMovies[b][0].popularity - groupedMovies[a][0].popularity
  );

  return (
    <div className="movie-list">
      {sortedTitles.map((title) => (
        <div className="movie-block" key={title}>
          <div className="movie-poster-sub-block">
            <img src={groupedMovies[title][0].poster} alt={`${title} poster`} />
          </div>
          <div className="movie-info-sub-block">
            <div className="movie-title">{title}</div>
            <div className="movie-runtime">
              {groupedMovies[title][0].runtime} minutes
            </div>
            <div className="movie-ratings-block">
              <div className="movie-ratings-sub-block-imdb">
                <img src="/images/imdbLogo.png" alt="IMDB logo" />
                {groupedMovies[title][0].imdbScore}/10 (
                {groupedMovies[title][0].imdbVotes})
              </div>
              <div className="movie-ratings-sub-block-rt">
                <img src="/images/rtLogo.png" alt="Rotten Tomatoes logo" />
                {groupedMovies[title][0].rtScore}%
              </div>
            </div>
          </div>
          <div className="movie-times-sub-block">
            {groupedMovies[title].map((showtime, index) => (
              <div
                className={`each-showtime ${
                  areFirstFiveShowtimesRegular(groupedMovies[title]) &&
                  index < 5
                    ? "smaller-showtime"
                    : ""
                }`}
                key={index}
              >
                <div className="showtime-background">
                  {showtime.type !== "Regular" && (
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
      ))}
    </div>
  );
};

export default BigChains;
