import React, { useState } from "react";
import MovieCarousel from "./components/MovieCarousel";
import CinemaColorKey from "./components/CinemaColorKey";
import SnifFilter from "./components/SnifFilter";
import Cinemateques from "./components/Cinemateques";

const App = () => {
  const [selectedSnifs, setSelectedSnifs] = useState(["Jerusalem"]);
  const [dayOffset] = useState(0);

  return (
    <>
      {/* <div className="home">
        <div className="main-sections-drop"></div>
      </div> */}
      <div class="testing-title-holder">
        <span>כרטיסרט</span>
      </div>
      <div className="main-carousel-holder">
        <div className="pre-carousel">
          <CinemaColorKey selectedSnifs={selectedSnifs} dayOffset={dayOffset} />
          <SnifFilter
            selectedSnifs={selectedSnifs}
            setSelectedSnifs={setSelectedSnifs}
          />
        </div>
        <MovieCarousel selectedSnifs={selectedSnifs} />
        <Cinemateques selectedSnifs={selectedSnifs} />
      </div>
    </>
  );
};

export default App;
