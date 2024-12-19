import React, { useState } from "react";
import MovieCarousel from "./components/MovieCarousel";
import CinemaColorKey from "./components/CinemaColorKey";
import SnifFilter from "./components/SnifFilter";
import ComingSoons from "./components/ComingSoons";
import Cinemateques from "./components/Cinemateques";
// import useDeviceType from "./utils/useDeviceType";

const App = () => {
  const [selectedSnifs, setSelectedSnifs] = useState(["Jerusalem"]);
  const [dayOffset, setDayOffset] = useState(0);

  // const isMobile = useDeviceType();
  // if (isMobile) {
  //   const mobileCSS = true;
  // }

  return (
    <>
      {/* <div className="home">
        <div className="main-sections-drop"></div>
      </div> */}
      <div className="testing-title-holder">
        <img src="/images/kartiseretAiLogoTry1.jpeg" alt="כרטיסרט" />
        <CinemaColorKey selectedSnifs={selectedSnifs} dayOffset={dayOffset} />
      </div>
      <div className="main-carousel-holder">
        <ComingSoons selectedSnifs={selectedSnifs} />
        <Cinemateques selectedSnifs={selectedSnifs} />
        <MovieCarousel
          selectedSnifs={selectedSnifs}
          setSelectedSnifs={setSelectedSnifs}
          setDayOffset={setDayOffset}
        />
      </div>
    </>
  );
};

export default App;
