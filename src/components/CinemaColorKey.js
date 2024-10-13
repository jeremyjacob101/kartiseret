import React from "react";
import "../componentsCSS/CinemaColorKey.css"; // Optional CSS file for styling

const CinemaColorKey = () => {
  return (
    <div className="cinema-key">
      <div className="key-item">
        <div className="showtime-time yes-planet"></div>
        <span>Yes Planet</span>
      </div>
      <div className="key-item">
        <div className="showtime-time cinema-city"></div>
        <span>Cinema City</span>
      </div>
      <div className="key-item">
        <div className="showtime-time lev-cinema"></div>
        <span>Lev Cinema</span>
      </div>
      <div className="key-item">
        <div className="showtime-time rav-hen-cinema"></div>
        <span>Rav Hen</span>
      </div>
    </div>
  );
};

export default CinemaColorKey;
