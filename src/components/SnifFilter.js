import React from "react";
import "../componentsCSS/SnifFilter.css"; // Optional CSS file for styling

const snifs = [
  "Rishon Letzion",
  "Jerusalem",
  "Haifa",
  "Ashdod",
  "Tel Aviv",
  "Zichron Yaakov",
  "Beer Sheva",
  "Chadera",
  "Kfar Saba",
  "Netanya",
  "Herziliya",
  "Raanana",
  "Ramat Hasharon",
  "Shoham",
  "Givataim",
  "Kiryat Ono",
  "Ayalon",
  "Even Yehuda"
];

const SnifFilter = ({ selectedSnifs, setSelectedSnifs }) => {
  const handleSnifChange = (event) => {
    const { value, checked } = event.target;
    if (checked) {
      setSelectedSnifs((prev) => [...prev, value]); // Add snif to the selection
    } else {
      setSelectedSnifs((prev) => prev.filter((snif) => snif !== value)); // Remove snif from the selection
    }
  };

  return (
    <div className="snif-filter">
      <h4>Filter by Snif (Cinema)</h4>
      {snifs.map((snif) => (
        <div key={snif}>
          <label>
            <input
              type="checkbox"
              value={snif}
              checked={selectedSnifs.includes(snif)}
              onChange={handleSnifChange}
            />
            {snif}
          </label>
        </div>
      ))}
    </div>
  );
};

export default SnifFilter;
