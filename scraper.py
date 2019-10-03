import sqlite3

from logger import SilentScraperLogger


class Scraper:
    def __init__(self, max_threads: int, logger_class, database: str):
        self.db: str = database
        self.queue = []
        self.max_threads: int = max_threads
        self._running_threads: int = 0

        if logger_class:
            self.logger = logger_class(self)
        else:
            self.logger = SilentScraperLogger(self)

    def start(self) -> None:
        """
        enqueue all search pages to be scraped on different threads
        """
        pass

    def _scrape_food(self, url: str) -> dict:
        """
        scrape page for dog food details and return a dict to be added to the db
        """
        self.logger.scrape_food(url)
        food = {"item_num": None,
                "url": None,
                "ingredients": None,
                "brand": None,
                "xsm_breed": None,
                "sm_breed": None,
                "md_breed": None,
                "lg_breed": None,
                "xlg_breed": None,
                "food_form": None,
                "lifestage": None,
                "special_diet": None,
                "fda_guidelines": None,
                }
        # scrape food data here
        return food

    def _scrape_search_results(self, url: str) -> None:
        """
        scrape a page of search results and enqueue all foods to be scraped
        """
        self.logger.scrape_search_results(url)
        # scrape search results URLs here

    def _enter_in_db(self, food: dict) -> None:
        """
        enter a food item into the database
        """
        self.logger.enter_in_db(food)
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute("INSERT INTO foods VALUES ({})".format(food.items()))
        # enter food data into db here

    def _enqueue_url(self, url: str, func) -> None:
        """
        enqueue url to be scraped and scraper function in the scraper queue
        """
        self.logger.enqueue(url, func)

    def _food_in_db(self, url: str) -> bool:
        """
        check the database to see if details about a food already exist
        """
        self.logger.food_in_db(url)

        # open connection to database
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        results = cur.execute("SELECT * FROM foods WHERE url = {}".format(url))
        conn.close()

        if results:
            return True
        else:
            return False

    def _check_and_enter_food(self, url: str) -> None:
        """
        check if a food is already in the database
        if it is not, scrape and add to the database
        """
        if not self._food_in_db(url):
            food = self._scrape_food(url)
            food = self._check_ingredients(food)
            self._enter_in_db(food)
        return

    def _check_ingredients(self, food: dict) -> dict:
        """
        use regex to check for bad ingredients in a food
        """
        self.logger.check_ingredients(food)
        return food
