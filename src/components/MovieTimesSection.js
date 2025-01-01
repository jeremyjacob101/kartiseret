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

function getShowtimeURL(showtime) {
  const { cinema, timeHref, snif } = showtime;

  switch (cinema) {
    case "HC":
      return `https://hotcinema.co.il/movie/${timeHref}`;
    case "CC":
      return `https://www.cinema-city.co.il/movie/${timeHref}`;

    case "YP": {
      let theaterId;
      switch (snif) {
        case "Rishon Letzion":
          theaterId = "1072";
          break;
        case "Ayalon":
          theaterId = "1025";
          break;
        case "Beer Sheva":
          theaterId = "1074";
          break;
        case "Zichron Yaakov":
          theaterId = "1075";
          break;
        case "Haifa":
          theaterId = "1070";
          break;
        case "Jerusalem":
          theaterId = "1073";
          break;
        default:
          theaterId = "9999";
      }
      return `https://tickets3.planetcinema.co.il/site/${theaterId}?code=${theaterId}-${timeHref}&languageId=en-GB`;
    }

    case "ML": {
      let theaterId;
      switch (snif) {
        case "Carmiel":
          theaterId = "1290";
          break;
        case "Haifa":
          theaterId = "1291";
          break;
        case "Netanya":
          theaterId = "1292";
          break;
        case "Glilot":
          theaterId = "1293";
          break;
        default:
          theaterId = "9999";
      }
      return `https://www.movieland-cinema.co.il/order/?eventID=${timeHref}&theaterId=${theaterId}`;
    }

    case "LC":
      return `https://ticket.lev.co.il/order/${timeHref}?lang=en`;

    case "RH": {
      let theaterId;
      switch (snif) {
        case "Givatayim":
          theaterId = "1058";
          break;
        case "Tel Aviv":
          theaterId = "1071";
          break;
        case "Kiryat Ono":
          theaterId = "1062";
          break;
        default:
          theaterId = "9999";
      }
      return `https://tickets3.rav-hen.co.il/site/${theaterId}?code=${theaterId}-${timeHref}&languageId=en-GB`;
    }

    default:
      return timeHref;
  }
}

const areFirstFourShowtimesRegular = (showtimes) =>
  showtimes.slice(0, 4).every((showtime) => showtime.type === "R");

// const areAllShowtimesRegular = (showtimes) =>
//   showtimes.every((showtime) => showtime.type === "R");

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
        const [hours, minutes] = time.split(":").map(Number);
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
      const [hours, minutes] = time.split(":").map(Number);
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
  const [openMapPopup, setOpenMapPopup] = useState(null); // { title, cinema }
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
                          href={getShowtimeURL(showtime)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="showtime-link" // Optional class for styling if you wish
                        >
                          <div className="showtime-background">
                            {showtime.type !== "R" && (
                              <div className="showtime-type">
                                {showtime.type}
                              </div>
                            )}
                            <div
                              className={`showtime-time ${getCinemaClass(
                                showtime.cinema
                              )}`}
                            >
                              {showtime.time}
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
                href={getShowtimeURL(showtime)}
                target="_blank"
                rel="noopener noreferrer"
                className="showtime-link" // Optional class for styling if you wish
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
              </a>
            </div>
          ))}
    </div>
  );
};

export default MovieTimesSection;
