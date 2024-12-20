import React, { useState, useRef, useEffect } from "react";
import SnifFilter from "./SnifFilter";
import "../componentsCSS/CarouselControls.css";

const dropdownIcon = "/icons/more-horizontal.svg";
const rightChevronIcon = "/icons/chevron-right.svg";
const leftChevronIcon = "/icons/chevron-left.svg";

const CarouselControls = ({
  dayOffsetLocal,
  offsatDay,
  handlePrevDay,
  handleNextDay,
  selectedSnifs,
  setSelectedSnifs,
  sortByTheater, // Add sortByTheater as prop
  setSortByTheater, // Add setSortByTheater as prop
}) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  return (
    <>
      <div className="carousel-controls">
        {/* Snif Filter */}
        <SnifFilter
          selectedSnifs={selectedSnifs}
          setSelectedSnifs={setSelectedSnifs}
        />

        {/* Dates */}
        <div className="clicking-controls">
          <div
            className={`chevron-container ${
              dayOffsetLocal === 0 ? "disabled" : ""
            }`}
            onClick={dayOffsetLocal > 0 ? handlePrevDay : null} // Only trigger if not disabled
          >
            <img
              src={leftChevronIcon}
              alt="Previous Day"
              className="chevron-icon"
            />
          </div>

          <div className="carousel-current-date">{offsatDay}</div>

          <div className="chevron-container" onClick={handleNextDay}>
            <img
              src={rightChevronIcon}
              alt="Next Day"
              className="chevron-icon"
            />
          </div>
        </div>

        {/* Dropdown for sortByTheater */}
        <div className="by-theater-dropdown-container" ref={dropdownRef}>
          <img
            src={dropdownIcon}
            alt="Options"
            className="by-theater-dropdown-icon"
            onClick={() => setShowDropdown((prev) => !prev)}
          />
          {showDropdown && (
            <div className="by-theater-dropdown-menu">
              <label>
                <input
                  type="checkbox"
                  checked={sortByTheater}
                  onChange={() => {
                    setSortByTheater((prev) => !prev);
                    setShowDropdown(false); // Close dropdown after selection
                  }}
                />
                Display by theater
              </label>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CarouselControls;
