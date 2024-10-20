import React from "react";
import "../componentsCSS/CinemaColorKey.css"; // Optional CSS file for styling

const CinemaColorKey = () => {
  return (
    <div className="cinema-key">
      <div className="cinema-key-heading">Legend</div>
      <div className="key-item">
        <div className="showtime-time yes-planet">19:30</div>
        <span>Yes Planet</span>
      </div>
      <div className="key-item">
        <div className="showtime-time cinema-city">19:30</div>
        <span>Cinema City</span>
      </div>
      <div className="key-item">
        <div className="showtime-time rav-hen-cinema">19:30</div>
        <span>Rav Hen</span>
      </div>
      <div className="key-item">
        <div className="showtime-time hot-cinema">19:30</div>
        <span>Hot Cinema</span>
      </div>
      <div className="key-item">
        <div className="showtime-time movieland-cinema">19:30</div>
        <span>MovieLand</span>
      </div>
      <div className="key-item">
        <div className="showtime-time lev-cinema">19:30</div>
        <span>Lev Cinema</span>
      </div>
    </div>
  );
};

export default CinemaColorKey;
