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

  const handleSnifClick = (snif) => {
    setSelectedSnifs([snif]); // Ensure only one snif is selected at a time
    setIsDropdownOpen(false); // Close the dropdown after selection
  };

  const toggleDropdown = () => {
    setIsDropdownOpen((prev) => !prev);
  };

  return (
    <div className="snif-filter">
      <button onClick={toggleDropdown} className="dropdown-button-snifs">
        Select City
      </button>
      {isDropdownOpen && (
        <div className="dropdown-menu-snifs">
          {snifs.map((snif) => (
            <div
              key={snif}
              className={`dropdown-item-snifs ${
                selectedSnifs.includes(snif) ? "checked" : ""
              }`}
              onClick={() => handleSnifClick(snif)}
            >
              {snif}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SnifFilter;
