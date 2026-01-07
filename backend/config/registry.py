from backend.scraping.nowplayings.CinemaCity import CinemaCity
from backend.scraping.nowplayings.YesPlanet import YesPlanet
from backend.scraping.nowplayings.LevCinema import LevCinema
from backend.scraping.nowplayings.RavHen import RavHen
from backend.scraping.nowplayings.MovieLand import MovieLand
from backend.scraping.nowplayings.HotCinema import HotCinema

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
from backend.dataflow.comingsoons.ComingSoonsTmdb import ComingSoonsTmdb
from backend.dataflow.comingsoons.ComingSoonsOpenAI import ComingSoonsOpenAI

from backend.dataflow.nowplayings.NowPlayingsClean import NowPlayingsClean
from backend.dataflow.nowplayings.NowPlayingsTmdb import NowPlayingsTmdb

REGISTRY = {
    "testingShowtimes": [
        # LevCinema,
        # RavHen,
        # MovieLand,
        # HotCinema,
        # YesPlanet,
        CinemaCity,
    ],
    "testingTheques": [
        JAFCtheque,
        SSCtheque,
        HOLONtheque,
        HERZtheque,
        HAIFtheque,
        JLEMtheque,
        TLVtheque,
    ],
    "testingSoons": [
        LCsoon,
        YPsoon,
        CCsoon,
        HCsoon,
        MLsoon,
    ],
}

DATAFLOW_REGISTRY = {
    "comingSoonsData": [
        ComingSoonsClean,
        ComingSoonsTmdb,
    ],
    "nowPlayingData": [
        NowPlayingsClean,
        NowPlayingsTmdb,
    ],
}
