from logger import VerboseScraperLogger
from scraper import Scraper

THREADS = 1
LOGGER = VerboseScraperLogger
DATABASE = "db.sqlite3"


def main():
    scraper = Scraper(max_threads=THREADS, logger_class=LOGGER, database=DATABASE)
    scraper.start()


if __name__ == "__main__":
    main()
