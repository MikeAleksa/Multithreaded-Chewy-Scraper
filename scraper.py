import sqlite3

from logger import SilentScraperLogger


class Scraper:
    def __init__(self, max_threads, logger_class, database):
        self.db = database
        self.queue = []
        self.max_threads = max_threads
        self._running_threads = 0

        if logger_class:
            self.logger = logger_class(self)
        else:
            self.logger = SilentScraperLogger(self)

    def start(self):
        """
        enqueue all search pages to be scraped on different threads
        """
        pass

    def _scrape_search_results(self, url):
        """
        scrape a page of search results and enqueue all foods to be scraped
        """
        self.logger.scrape_search_results(url)
        # scrape search results URLs here

    def _scrape_food(self, url) -> dict:
        """
        scrape page for dog food details and return a dict to be added to the db
        """
        food = {'item_num': None,
                'url': None,
                'ingredients': None,
                'brand': None,
                'xsm_breed': None,
                'sm_breed': None,
                'md_breed': None,
                'lg_breed': None,
                'xlg_breed': None,
                'food_form': None,
                'lifestage': None,
                'special_diet': None,
                'fda_guidelines': None,
                }
        # scrape food data here
        return food

    def _enter_in_db(self, food):
        """
        enter a food item into the database
        """
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        cur.execute('INSERT INTO foods VALUES ({})'.format(food.items()))
        # enter food data into db here

    def _enqueue_url(self, url, func):
        """
        enqueue url to be scraped and scraper function in the scraper queue
        """
        self.logger.enqueue(url, func)

    def _food_in_db(self, url) -> bool:
        """
        check the database to see if details about a food already exist
        """
        self.logger.food_in_db(url)

        # open connection to database
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        results = cur.execute('SELECT * FROM foods WHERE url = {}'.format(url))
        conn.close()

        if results:
            return True
        else:
            return False

    def _check_and_enter_food(self, url):
        """
        check if a food is already in the database
        if it is not, scrape and add to the database
        """
        if not self._food_in_db(url):
            food = self._scrape_food(url)
            self._enter_in_db(food)
        else:
            return
