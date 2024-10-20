import React, { useState } from "react";
import MovieCarousel from "./components/MovieCarousel";
import CinemaColorKey from "./components/CinemaColorKey";
import SnifFilter from "./components/SnifFilter";

const App = () => {
  const [selectedSnifs, setSelectedSnifs] = useState([]);

  return (
    <>
      <div className="main-carousel-holder">
        <div className="pre-carousel">
          <SnifFilter
            selectedSnifs={selectedSnifs}
            setSelectedSnifs={setSelectedSnifs}
          />
          <CinemaColorKey />
        </div>
        <MovieCarousel selectedSnifs={selectedSnifs} />{" "}
      </div>
    </>
  );
};

export default App;
