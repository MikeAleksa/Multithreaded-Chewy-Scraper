from logger import *
from scraper import Scraper

THREADS = 5
DATABASE = "db.sqlite3"
SEARCH_URL = "https://www.chewy.com/s?rh=c%3A288%2Cc%3A332&page="  # contains all dog foods


def main():
    logger = VerboseScraperLogger()
    scraper = Scraper(database=DATABASE, logger=logger, num_threads=THREADS)
    scraper.scrape(url=SEARCH_URL, pages_of_results=97)


if __name__ == "__main__":
    main()
