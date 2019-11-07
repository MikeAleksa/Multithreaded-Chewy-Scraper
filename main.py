from logger import *
from scraper import Scraper

THREADS = 5
DATABASE = "db.sqlite3"
SEARCH_URL = "https://www.chewy.com/s?rh=c%3A288%2Cc%3A332&page="  # contains all dog foods


def main():
    logger = VerboseScraperLogger()
    scraper = Scraper(database=DATABASE, logger=logger, num_threads=THREADS)

    # scrape all dog foods
    scraper.scrape(url=SEARCH_URL, pages_of_results=97)

    # scrape any individual foods here
    # single_url = "https://www.chewy.com/billy-margot-single-animal-protein/dp/206119"
    # scraper.scrape_food_if_new(single_url)


if __name__ == "__main__":
    main()
