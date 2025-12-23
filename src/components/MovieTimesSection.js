import React, { useState, useRef, useEffect } from "react";
import "../componentsCSS/MovieTimesSection.css";

const mapIcon = "/icons/navigation.svg";

const theaterNames = {
  LC: "Lev Cinema",
  HC: "Hot Cinema",
  CC: "Cinema City",
  YP: "Yes Planet",
  ML: "MovieLand",
  RH: "Rav Hen",
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

const areFirstFourShowtimesRegular = (showtimes) =>
  showtimes.slice(0, 4).every((showtime) => showtime.type === "2D");

// const areAllShowtimesRegular = (showtimes) =>
//   showtimes.every((showtime) => showtime.type === "2D");

const groupShowtimesByTheater = (showtimes) => {
  const groupedByTheater = {};

  showtimes.forEach((showtime) => {
    if (!groupedByTheater[showtime.cinema]) {
      groupedByTheater[showtime.cinema] = [];
    }
    groupedByTheater[showtime.cinema].push(showtime);
  });

  Object.values(groupedByTheater).forEach((group) => {
    group.sort((a, b) => {
      const getMinutes = (time) => {
        const [hours, minutes] = time.split(":").slice(0, 2).map(Number);
        return hours * 60 + minutes;
      };

      const aMinutes = getMinutes(a.time);
      const bMinutes = getMinutes(b.time);
      const isAMidnight = aMinutes <= 120; // Midnight range: 00:00–02:00
      const isBMidnight = bMinutes <= 120;
      if (isAMidnight && !isBMidnight) return 1; // Midnight goes last
      if (!isAMidnight && isBMidnight) return -1; // Non-midnight goes first
      return aMinutes - bMinutes;
    });
  });

  return groupedByTheater;
};

function sortShowtimes(showtimes) {
  return [...showtimes].sort((a, b) => {
    const getMinutes = (time) => {
      const [hours, minutes] = time.split(":").slice(0, 2).map(Number);
      return hours * 60 + minutes;
    };
    const aMinutes = getMinutes(a.time);
    const bMinutes = getMinutes(b.time);
    const isAMidnight = aMinutes <= 120; // up to 00:30
    const isBMidnight = bMinutes <= 120;
    if (isAMidnight && !isBMidnight) return 1; // put midnight last
    if (!isAMidnight && isBMidnight) return -1;
    return aMinutes - bMinutes;
  });
}

const MovieTimesSection = ({
  title,
  showtimes,
  sortByTheater,
  theatersData,
  selectedCity,
}) => {
  const [openMapPopup, setOpenMapPopup] = useState(null);
  const popupRef = useRef(null);

  const toggleMapPopup = (title, cinema) => {
    setOpenMapPopup((prev) =>
      prev && prev.title === title && prev.cinema === cinema
        ? null
        : { title, cinema }
    );
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      const clickedOutsidePopup =
        popupRef.current && !popupRef.current.contains(e.target);

      if (openMapPopup && clickedOutsidePopup) {
        setOpenMapPopup(null);
      }
    };
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [openMapPopup]);

  return (
    <div
      className={
        sortByTheater
          ? "by-theater-movie-times-sub-block"
          : "movie-times-sub-block"
      }
    >
      {sortByTheater
        ? Object.entries(groupShowtimesByTheater(showtimes)).map(
            ([cinema, perCinemaShowtimes]) => {
              const theaterInfo = theatersData.find(
                (t) => t.chain === cinema && t.city === selectedCity
              );
              return (
                <div key={cinema} className="theater-block">
                  <div className="theater-title">
                    {theaterInfo && (
                      <img
                        src={mapIcon}
                        alt="Map Icon"
                        className="map-icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleMapPopup(title, cinema);
                        }}
                      />
                    )}
                    {theaterNames[cinema] || cinema}
                    {openMapPopup &&
                      openMapPopup.title === title &&
                      openMapPopup.cinema === cinema &&
                      theaterInfo && (
                        <div className="map-popup" ref={popupRef}>
                          <a
                            href={theaterInfo.location}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {theaterInfo.address}
                          </a>
                        </div>
                      )}
                  </div>
                  <div className="by-theater-showtimes">
                    {perCinemaShowtimes.map((showtime, sIndex) => (
                      <div
                        className={`each-showtime${
                          areFirstFourShowtimesRegular(perCinemaShowtimes) &&
                          sIndex < 4
                            ? " smaller-showtime"
                            : ""
                        }`}
                        key={sIndex}
                      >
                        <a
                          href={showtime.timeHref}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="showtime-link"
                        >
                          <div className="showtime-background">
                            {showtime.type !== "2D" && (
                              <div className="showtime-type">
                                {showtime.type}
                              </div>
                            )}
                            <div
                              className={`showtime-time ${getCinemaClass(
                                showtime.cinema
                              )}`}
                            >
                              {showtime.time?.slice(0, 5)}
                            </div>
                          </div>
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              );
            }
          )
        : sortShowtimes(showtimes).map((showtime, sIndex) => (
            <div
              className={`each-showtime${
                areFirstFourShowtimesRegular(showtimes) && sIndex < 4
                  ? " smaller-showtime"
                  : ""
              }`}
              key={sIndex}
            >
              <a
                href={showtime.timeHref}
                target="_blank"
                rel="noopener noreferrer"
                className="showtime-link"
              >
                <div className="showtime-background">
                  {showtime.type !== "2D" && (
                    <div className="showtime-type">{showtime.type}</div>
                  )}
                  <div
                    className={`showtime-time ${getCinemaClass(
                      showtime.cinema
                    )}`}
                  >
                    {showtime.time?.slice(0, 5)}
                  </div>
                </div>
              </a>
            </div>
          ))}
    </div>
  );
};

export default MovieTimesSection;
