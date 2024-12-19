import React from "react";
import SnifFilter from "./SnifFilter";
import "../componentsCSS/CarouselControls.css";

const CarouselControls = ({
  dayOffsetLocal,
  offsatDay,
  handlePrevDay,
  handleNextDay,
  selectedSnifs,
  setSelectedSnifs,
}) => {
  return (
    <>
      <div className="carousel-controls">
        <SnifFilter
          selectedSnifs={selectedSnifs}
          setSelectedSnifs={setSelectedSnifs}
        />
        <div className="clicking-controls">
          <button
            className="previous-day-button"
            onClick={handlePrevDay}
            disabled={dayOffsetLocal === 0}
          >
            Previous
          </button>
          <div className="carousel-current-date">{offsatDay}</div>
          <button className="next-day-button" onClick={handleNextDay}>
            Next
          </button>
        </div>
      </div>
    </>
  );
};

export default CarouselControls;
