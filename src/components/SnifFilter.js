import React, { useState } from "react";
import "../componentsCSS/SnifFilter.css"; // Optional CSS file for styling

const snifs = [
  /* JLEM */
  "Jerusalem",
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
  /* North */
  "Nahariya",
  "Carmiel",
  /* South */
  "Beer Sheva",
];

const SnifFilter = ({ selectedSnifs, setSelectedSnifs }) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleSnifChange = (event) => {
    const { value, checked } = event.target;
    if (checked) {
      setSelectedSnifs((prev) => [...prev, value]); // Add snif to the selection
    } else {
      setSelectedSnifs((prev) => prev.filter((snif) => snif !== value)); // Remove snif from the selection
    }
  };

  const toggleDropdown = () => {
    setIsDropdownOpen((prev) => !prev);
  };

  return (
    <div className="snif-filter">
      <button onClick={toggleDropdown} className="dropdown-button">
        Filter by Location
      </button>
      {isDropdownOpen && (
        <div className="dropdown-menu">
          {snifs.map((snif) => (
            <div key={snif} className="dropdown-item">
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
      )}
    </div>
  );
};

export default SnifFilter;
