import React, { useState, useEffect } from "react";
import Papa from "papaparse";
import "../componentsCSS/CinemaColorKey.css";

const showtimes_csv = "/CSVs/31-10-24-showtimes.csv";

const CinemaColorKey = ({ selectedSnifs, dayOffset }) => {
  const [availableCinemas, setAvailableCinemas] = useState(new Set());

  const getFormattedDate = (dayOffset) => {
    const today = new Date();
    today.setDate(today.getDate() + dayOffset);
    return `${String(today.getDate()).padStart(2, "0")}/${String(
      today.getMonth() + 1
    ).padStart(2, "0")}/${today.getFullYear()}`;
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
            if (!showtime.time) {
              // Skip if time is missing or undefined
              return;
            }

            const [hours, minutes] = showtime.time.split(":").map(Number);
            const showtimeMinutes = hours * 60 + minutes;

            // Check if showtime matches the selected date, selected snif, and is in the future if today
            if (
              showtime.date === selectedDate &&
              (selectedSnifs.length === 0 ||
                selectedSnifs.includes(showtime.snif)) &&
              (showtime.date !== getFormattedDate(0) ||
                showtimeMinutes >= currentTimeMinutes)
            ) {
              cinemaSet.add(showtime.cinema);
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

  return (
    <div className="cinema-key">
      <div className="cinema-key-heading">Legend</div>
      {Array.from(availableCinemas).map((cinema) => (
        <div key={cinema} className="key-item">
          <div className={`showtime-time ${cinemaClasses[cinema]}`}>19:30</div>
          <span>{cinemaNames[cinema]}</span>
        </div>
      ))}
    </div>
  );
};

export default CinemaColorKey;
