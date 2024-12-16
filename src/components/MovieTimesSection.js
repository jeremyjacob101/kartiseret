import React, { useState, useRef, useEffect } from "react";
import "../componentsCSS/MovieTimesSection.css";

const mapIcon = "/icons/map.svg";

const theaterNames = {
  LC: "Lev Cinema",
  HC: "Hot Cinema",
  CC: "Cinema City",
  YP: "Yes Planet",
  ML: "MovieLand",
  RH: "Rav Hen",
};

const areFirstFourShowtimesRegular = (showtimes) =>
  showtimes.slice(0, 4).every((showtime) => showtime.type === "R");

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

const groupShowtimesByTheater = (showtimes) => {
  const groupedByTheater = {};

  showtimes.forEach((showtime) => {
    if (!groupedByTheater[showtime.cinema]) {
      groupedByTheater[showtime.cinema] = [];
    }
    groupedByTheater[showtime.cinema].push(showtime);
  });

  Object.values(groupedByTheater).forEach((group) =>
    group.sort((a, b) => {
      const getMinutes = (time) => {
        const [hours, minutes] = time.split(":").map(Number);
        return hours * 60 + minutes;
      };
      return getMinutes(a.time) - getMinutes(b.time);
    })
  );

  return groupedByTheater;
};

const MovieTimesSection = ({
  title,
  showtimes,
  sortByTheater,
  theatersData,
  selectedCity,
}) => {
  const [openMapPopup, setOpenMapPopup] = useState(null); // { title, cinema }
  const popupRef = useRef(null);

  const toggleMapPopup = (title, cinema) => {
    setOpenMapPopup((prev) =>
      prev && prev.title === title && prev.cinema === cinema
        ? null
        : { title, cinema }
    );
  };

  // Close map popup on outside click
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
            ([cinema, cShowtimes]) => {
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
                    {cShowtimes.map((showtime, sIndex) => (
                      <div
                        className={`each-showtime${
                          areFirstFourShowtimesRegular(cShowtimes) && sIndex < 4
                            ? " smaller-showtime"
                            : ""
                        }`}
                        key={sIndex}
                      >
                        <div className="showtime-background">
                          {showtime.type !== "R" && (
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
              );
            }
          )
        : showtimes.map((showtime, sIndex) => (
            <div
              className={`each-showtime ${
                areFirstFourShowtimesRegular(showtimes) && sIndex < 4
                  ? "smaller-showtime"
                  : ""
              }`}
              key={sIndex}
            >
              <div className="showtime-background">
                {showtime.type !== "R" && (
                  <div className="showtime-type">{showtime.type}</div>
                )}
                <div
                  className={`showtime-time ${getCinemaClass(showtime.cinema)}`}
                >
                  {showtime.time}
                </div>
              </div>
            </div>
          ))}
    </div>
  );
};

export default MovieTimesSection;
