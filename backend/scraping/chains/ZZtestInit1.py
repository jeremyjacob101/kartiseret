#
# RENAME AND USE AS
#   __init__.py
#
# then in runner.py:
#   from backend.scraping.chains import ALL_CHAIN_CLASSES
#

from .CinemaCity import CinemaCity
from .YesPlanet import YesPlanet
from .LevCinema import LevCinema
from .RavHen import RavHen
from .MovieLand import MovieLand
from .HotCinema import HotCinema

# what "from … import *" will expose
__all__ = [
    "CinemaCity",
    "YesPlanet",
    "LevCinema",
    "RavHen",
    "MovieLand",
    "HotCinema",
]

# handy group you can import once
ALL_CHAIN_CLASSES = [
    CinemaCity,
    YesPlanet,
    LevCinema,
    RavHen,
    MovieLand,
    HotCinema,
]
