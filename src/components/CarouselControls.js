import React from "react";
import "../componentsCSS/CarouselControls.css";

const CarouselControls = ({
  dayOffsetLocal,
  offsatDay,
  handlePrevDay,
  handleNextDay,
}) => {
  return (
    <>
      <div className="carousel-controls">
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
    </>
  );
};

export default CarouselControls;
