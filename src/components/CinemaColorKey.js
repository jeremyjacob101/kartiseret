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
    const selectedDate = getFormattedDate(dayOffset); // Moved inside useEffect

    const loadShowtimeData = async () => {
      const showtimesData = await (await fetch(showtimes_csv)).text();

      Papa.parse(showtimesData, {
        header: true,
        dynamicTyping: true,
        complete: (results) => {
          const cinemaSet = new Set();

          results.data.forEach((showtime) => {
            // Check if showtime matches the selected date and selected snif
            if (
              showtime.date === selectedDate &&
              (selectedSnifs.length === 0 ||
                selectedSnifs.includes(showtime.snif))
            ) {
              cinemaSet.add(showtime.cinema);
            }
          });

          setAvailableCinemas(cinemaSet);
        },
      });
    };

    loadShowtimeData();
  }, [selectedSnifs, dayOffset]); // No need to add selectedDate here

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
