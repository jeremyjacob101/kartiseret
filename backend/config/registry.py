from backend.scraping.chains.CinemaCity import CinemaCity
from backend.scraping.chains.YesPlanet import YesPlanet
from backend.scraping.chains.LevCinema import LevCinema
from backend.scraping.chains.RavHen import RavHen
from backend.scraping.chains.MovieLand import MovieLand
from backend.scraping.chains.HotCinema import HotCinema

from backend.scraping.cinematheques.JLEMtheque import JLEMtheque
from backend.scraping.cinematheques.SSCtheque import SSCtheque
from backend.scraping.cinematheques.JAFCtheque import JAFCtheque
from backend.scraping.cinematheques.HAIFtheque import HAIFtheque
from backend.scraping.cinematheques.HERZtheque import HERZtheque
from backend.scraping.cinematheques.TLVtheque import TLVtheque
from backend.scraping.cinematheques.HOLONtheque import HOLONtheque

from backend.scraping.comingsoons.CCsoon import CCsoon
from backend.scraping.comingsoons.HCsoon import HCsoon
from backend.scraping.comingsoons.LCsoon import LCsoon
from backend.scraping.comingsoons.MLsoon import MLsoon
from backend.scraping.comingsoons.YPsoon import YPsoon

from backend.dataflow.comingsoons.ComingSoonsClean import ComingSoonsClean
from backend.dataflow.comingsoons.ComingSoonsOmdb import ComingSoonsOmdb
from backend.dataflow.comingsoons.ComingSoonsOpenAI import ComingSoonsOpenAI


REGISTRY = {
    "testingMovies": [
        CinemaCity,
        YesPlanet,
        LevCinema,
        RavHen,
        MovieLand,
        HotCinema,
    ],
    "testingTheques": [
        JLEMtheque,
        SSCtheque,
        JAFCtheque,
        HAIFtheque,
        HERZtheque,
        TLVtheque,
        HOLONtheque,
    ],
    "testingSoons": [
        CCsoon,
        HCsoon,
        LCsoon,
        MLsoon,
        YPsoon,
    ],
}

DATAFLOW_REGISTRY = {
    "comingSoonData": [
        # ComingSoonsClean,
        # ComingSoonsOmdb,
        ComingSoonsOpenAI,
    ],
}
