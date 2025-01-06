import { useEffect, useState } from "react";
import { supabase } from "../supabaseClient"; // Import the Supabase client
import "../componentsCSS/Cinematheques.css";

const cinemathequeCities = {
  HFCT: "Haifa",
  JLMCT: "Jerusalem",
  HRZCT: "Herziliya",
  TLVCT: "Tel Aviv",
  JAFC: "Tel Aviv",
};

const ChevronUp = "/icons/chevron-up.svg";
const ChevronDown = "/icons/chevron-down.svg";

// Function to check if the showtime is valid
const isValidShowtime = (date, time) => {
  if (!date || !time) return false; // Ensure date and time are not undefined
  const [year, month, day] = date.split("-").map(Number);
  const [hours, minutes] = time.split(":").map(Number);

  const showtimeDate = new Date(year + 2000, month - 1, day, hours, minutes);
  const now = new Date();

  return showtimeDate >= now;
};

const Cinematheques = ({ selectedSnifs }) => {
  const [cinemaMovies, setCinemaMovies] = useState({});
  const [openSections, setOpenSections] = useState({});

  useEffect(() => {
    const loadShowtimeData = async () => {
      try {
        // Fetch data from the "cinematheques" table in Supabase
        const { data: showtimes, error } = await supabase
          .from("cinematheques")
          .select("*");

        if (error) {
          console.error("Error fetching data from Supabase:", error);
          return;
        }

        // Group movies by cinema
        const groupedMovies = showtimes.reduce((acc, movie) => {
          const cinema = movie.cinema;
          const city = cinema ? cinemathequeCities[cinema] : undefined;
          const isSelected =
            selectedSnifs.length === 0 || selectedSnifs.includes(city);

          // Only include if showtime is valid
          if (
            city &&
            isSelected &&
            isValidShowtime(movie.datetext, movie.timetext)
          ) {
            if (!acc[cinema]) acc[cinema] = [];
            acc[cinema].push(movie);
          }
          return acc;
        }, {});

        setCinemaMovies(groupedMovies);
      } catch (err) {
        console.error("Error loading showtime data:", err);
      }
    };

    loadShowtimeData();
  }, [selectedSnifs]);

  const toggleSection = (cinema) => {
    setOpenSections((prevState) => ({
      ...prevState,
      [cinema]: !prevState[cinema],
    }));
  };

  if (!Object.keys(cinemaMovies).length) {
    return null;
  }

  return (
    <>
      {Object.entries(cinemaMovies).map(([cinema, movies]) => (
        <div key={cinema} className="cinematheque-section">
          <h2
            className="cinematheque-header-name"
            onClick={() => toggleSection(cinema)}
          >
            <span>
              {cinema === "JAFC"
                ? "Jaffa Cinema"
                : `${cinemathequeCities[cinema]} Cinematheque`}
            </span>
            <img
              src={openSections[cinema] ? ChevronUp : ChevronDown}
              alt={openSections[cinema] ? "Close" : "Open"}
              className="cinematheque-chevron"
            />
          </h2>
          <div
            className={`cinematheque-carousel-wrapper ${
              openSections[cinema] ? "open" : "closed"
            }`}
          >
            <div className="cinematheque-carousel">
              <div className="cinematheque-carousel-inner">
                {movies.map((movie, index) => {
                  const { datetext, timetext, title, year, href, poster } =
                    movie;

                  return (
                    <div key={index} className="cinematheque-card">
                      <a href={href} target="_blank" rel="noopener noreferrer">
                        <img
                          src={poster || "/images/defposter.jpeg"}
                          alt={title}
                          className="cinematheque-poster"
                          loading="lazy"
                          onError={(e) => {
                            e.target.onerror = null; // Prevent infinite loop in case default poster also fails
                            e.target.src = "/images/defposter.jpeg";
                          }}
                        />
                      </a>
                      <div className="cinematheque-details">
                        <h3 className="cinematheque-title">{title}</h3>
                        <h3>({year})</h3>
                        <div>
                          <p>
                            {datetext
                              .split("-")
                              .reverse()
                              .slice(0, 2)
                              .join(".")}
                          </p>
                          <p>@{timetext}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      ))}
    </>
  );
};

export default Cinematheques;
