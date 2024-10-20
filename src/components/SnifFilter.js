import React from "react";
import "../componentsCSS/SnifFilter.css"; // Optional CSS file for styling

const snifs = [
  /* TLV */
  "Tel Aviv",
  /* North of TLV */
  "Herziliya",
  "Raanana",
  "Ramat Hasharon",
  "Kfar Saba",
  "Glilot",
  /* East of TLV */
  "Petach Tikvah",
  "Ayalon",
  "Givataim",
  "Kiryat Ono",
  /* South of TLV */
  "Rishon Letzion",
  "Rehovot",

  /* South of Rishon */
  "Ashkelon",
  "Ashdod",
  /* Netanya */
  "Netanya",
  "Even Yehuda",
  /* Between Netanya and Haifa */
  "Zichron Yaakov",
  "Chadera",
  /* Haifa */
  "Haifa",
  "Kiryat Bialik",
  /* Modiin */
  "Modiin",
  "Shoham",
  /* JLEM */
  "Jerusalem",
  /* North */
  "Nahariya",
  "Carmiel",
  /* South */
  "Beer Sheva",
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
