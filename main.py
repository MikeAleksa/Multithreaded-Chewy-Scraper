from logger import *
from scraper import Scraper

THREADS = 1
DATABASE = "db.sqlite3"


def main():
    logger = VerboseScraperLogger()
    scraper = Scraper(max_threads=THREADS, database=DATABASE, logger=logger)
    scraper.start()


if __name__ == "__main__":
    main()
