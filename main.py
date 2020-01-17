from scraper import Scraper
from scraper_logger import *

THREADS = 5
DATABASE = "scraperdb.cnf"
SEARCH_URL = "https://www.chewy.com/s?rh=c%3A288%2Cc%3A332&page="  # contains all dog foods


def main():
    logger = VerboseScraperLogger()
    scraper = Scraper(database=DATABASE, logger=logger, num_threads=THREADS)
    scraper.scrape(url=SEARCH_URL)


if __name__ == "__main__":
    main()
