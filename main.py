from logger import *
from scraper import Scraper

THREADS = 1
DATABASE = "db.sqlite3"
INIT_URL = "https://www.chewy.com/s?rh=c%3A288%2Cc%3A332&sort=relevance"  # contains all dog foods


def main():
    logger = ErrorScraperLogger()
    scraper = Scraper(database=DATABASE, logger=logger, max_threads=THREADS)
    scraper.scrape(url=INIT_URL)


if __name__ == "__main__":
    main()
