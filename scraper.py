import re
import sqlite3

from logger import SilentScraperLogger


class Scraper:
    COLUMNS = ["item_num", "url", "ingredients", "brand", "xsm_breed", "sm_breed", "md_breed",
               "lg_breed", "xlg_breed", "food_form", "lifestage", "special_diet", "fda_guidelines", ]

    COLUMN_NAMES = ", ".join(COLUMNS)

    BAD_INGREDIENTS = re.compile('(pea)|(bean)|(lentil)|(potato)|(seed)|(soy)|(chickpea)')

    VITAMINS = re.compile('(mineral)|(vitamin)|(zinc)|(supplement)|(calcium)|(phosphorus)|' +
                          '(potassium)|(sodium)|(magnesium)|(sulfer)|(iron)|(iodine)|' +
                          '(selenium)|(copper)')

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
        conn = None
        values = str()

        # generate insert statement
        for index, value in enumerate(food.values()):
            if isinstance(value, str):
                values += ', "{}"'.format(value)
            else:
                if index != 0:
                    values += ", "
                values += str(value)
        query = "INSERT INTO foods ({}) VALUES({})".format(Scraper.COLUMN_NAMES, values)

        # try to execute and commit input statement
        try:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
        except sqlite3.Error as e:
            self.logger.error("Error while executing query: {}".format(query))
            self.logger.error("SQLITE3 ERROR: " + str(e.args))
            if conn:
                self.logger.error("Rolling back...")
                conn.rollback()
        finally:
            if conn:
                conn.close()

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
        results = None
        conn = None

        try:
            conn = sqlite3.connect(self.db)
            cur = conn.cursor()
            cur.execute('SELECT * FROM foods WHERE url = "{}"'.format(url))
            results = cur.fetchall()
        except sqlite3.Error as e:
            self.logger.error("Error checking if food in database: {}".format(url))
            self.logger.error("SQLITE3 ERROR: " + str(e.args))
            if conn:
                self.logger.error("Rolling back...")
                conn.rollback()
        finally:
            if conn:
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

        # find "main ingredients" - all ingredients before appearance of first vitamin or mineral
        main_ingredients = Scraper.VITAMINS.split(food["ingredients"].lower(), maxsplit=1)[0]
        results = Scraper.BAD_INGREDIENTS.findall(main_ingredients)

        if not results:
            food["fda_guidelines"] = 1
        else:
            food["fda_guidelines"] = 0

        return food
