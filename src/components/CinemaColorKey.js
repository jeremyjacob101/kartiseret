import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/CinemaColorKey.css";

const showtimes_csv = "/CSVs/25-01-01-showtimes.csv";

const CinemaColorKey = ({ selectedSnifs, dayOffset }) => {
  const [availableCinemas, setAvailableCinemas] = useState(new Set());
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Now returning date in yy-mm-dd format
  const getFormattedDate = (dayOffset) => {
    const today = new Date();
    today.setDate(today.getDate() + dayOffset);

    const year = String(today.getFullYear()).slice(-2); // last two digits
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  };

  useEffect(() => {
    const selectedDate = getFormattedDate(dayOffset);
    const now = new Date();
    const currentTimeMinutes = now.getHours() * 60 + now.getMinutes();

    const loadShowtimeData = async () => {
      const showtimesData = await (await fetch(showtimes_csv)).text();

      Papa.parse(showtimesData, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          const cinemaSet = new Set();

          results.data.forEach((showtime) => {
            if (!showtime.time || !showtime.date) {
              return; // Skip invalid rows
            }

            const [hours, minutes] = showtime.time.split(":").map(Number);
            const showtimeMinutes = hours * 60 + minutes;

            const isSameDay = showtime.date === selectedDate;
            const isEarlyNextDay =
              showtime.date === getFormattedDate(dayOffset + 1);

            if (
              (isSameDay &&
                (dayOffset !== 0 || showtimeMinutes >= currentTimeMinutes)) ||
              (isEarlyNextDay && showtimeMinutes < 60)
            ) {
              if (
                selectedSnifs.length === 0 ||
                selectedSnifs.includes(showtime.snif)
              ) {
                cinemaSet.add(showtime.cinema);
              }
            }
          });

          setAvailableCinemas(cinemaSet);
        },
      });
    };

    loadShowtimeData();
  }, [selectedSnifs, dayOffset]);

  const cinemaClasses = {
    YP: "yes-planet",
    CC: "cinema-city",
    RH: "rav-hen-cinema",
    HC: "hot-cinema",
    ML: "movieland-cinema",
    LC: "lev-cinema",
  };
  const cinemaNames = {
    YP: "Yes Planet",
    CC: "Cinema City",
    RH: "Rav Hen",
    HC: "Hot Cinema",
    ML: "MovieLand",
    LC: "Lev Cinema",
  };

  if (availableCinemas.size === 0) {
    return null;
  }

  const toggleDropdown = () => {
    setIsDropdownOpen((prev) => !prev);
  };

  return (
    <div className="cinema-color-key">
      <button onClick={toggleDropdown} className="dropdown-button-legend">
        Legend
      </button>
      {isDropdownOpen && (
        <div className="dropdown-menu-legend">
          {Array.from(availableCinemas).map((cinema) => (
            <div key={cinema} className="dropdown-item-legend">
              <div className={`showtime-time ${cinemaClasses[cinema]}`}>
                19:30
              </div>
              <span>{cinemaNames[cinema]}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CinemaColorKey;
