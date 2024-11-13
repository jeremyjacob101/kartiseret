import React, { useState } from "react";
import MovieCarousel from "./components/MovieCarousel";
import CinemaColorKey from "./components/CinemaColorKey";
import SnifFilter from "./components/SnifFilter";
import ComingSoons from "./components/ComingSoons";

const App = () => {
  const [selectedSnifs, setSelectedSnifs] = useState(["Jerusalem"]);
  const [dayOffset, setDayOffset] = useState(0);

  return (
    <>
      {/* <div className="home">
        <div className="main-sections-drop"></div>
      </div> */}
      <div class="testing-title-holder">
        {/* <CinemaColorKey selectedSnifs={selectedSnifs} dayOffset={dayOffset} /> */}
        <span>כרטיסרט</span>
        <SnifFilter
          selectedSnifs={selectedSnifs}
          setSelectedSnifs={setSelectedSnifs}
        />
      </div>
      <div className="main-carousel-holder">
        <ComingSoons selectedSnifs={selectedSnifs} />
        <MovieCarousel
          selectedSnifs={selectedSnifs}
          setDayOffset={setDayOffset}
        />
      </div>
    </>
  );
};

export default App;
