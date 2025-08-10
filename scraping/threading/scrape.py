import threading
from scraping.chains.CinemaCity import CinemaCity
from scraping.chains.YesPlanet import YesPlanet
from scraping.chains.LevCinema import LevCinema


def worker(cinema_cls):
    inst = cinema_cls()
    inst.scrape()


def main():
    cinema_classes = [CinemaCity, YesPlanet, LevCinema]
    threads = []
    for cls in cinema_classes:
        t = threading.Thread(target=worker, args=(cls,), name=cls.__name__)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
