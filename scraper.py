import queue
import re
import sqlite3
import threading

import requests
from bs4 import BeautifulSoup

from logger import ScraperLogger, SilentScraperLogger


class Scraper:

    COLUMN_NAMES = ", ".join(["item_num", "url", "ingredients", "brand", "xsm_breed", "sm_breed", "md_breed",
                              "lg_breed", "xlg_breed", "food_form", "lifestage", "special_diet", "fda_guidelines"])

    BAD_INGREDIENTS = re.compile('(pea)|(bean)|(lentil)|(potato)|(seed)|(soy)')

    VITAMINS = re.compile('(mineral)|(vitamin)|(zinc)|(supplement)|(calcium)|(phosphorus)|(potassium)|(sodium)|' +
                          '(magnesium)|(sulfer)|(sulfur)|(iron)|(iodine)|(selenium)|(copper)|(salt)|(chloride)|' +
                          '(choline)|(lysine)|(taurine)')

    def __init__(self, database: str, max_threads: int = 5, logger: ScraperLogger = SilentScraperLogger()):
        # TODO: implement locks in functions
        self.db: str = database
        self.queue = queue.Queue()
        self.logger = logger

        self._max_threads = max_threads
        self._running_threads = 0

        self.db_lock = threading.Lock()  # lock for database connection
        self.mt_lock = threading.Lock()  # lock for _max_threads
        self.rt_lock = threading.Lock()  # lock for _running_threads

    def scrape(self, url: str) -> None:
        # TODO: write comment for method
        """
        ...
        :param url:
        :return:
        """
        # TODO: write function to start scraping search pages from initial url and enqueue subsequent pages and found
        #  foods and continue spawning threads to execute jobs from queue while
        pass

    def scrape_food_if_new(self, url: str) -> None:
        """
        check if a food is already in the database
        if it is not, scrape and add to the database
        :param url: link to page containing food details
        """

        if not self._check_db_for_food(url):
            try:
                food = self._scrape_food_details(url)
                self._enter_in_db(food)
            except Exception as e:
                self.logger.error("Error while processing food at URL: {}".format(url))
                self.logger.error("ERROR: " + str(e.args))
                self.logger.error("Skipping food...")
        return

    def scrape_search_results(self, url: str) -> None:
        """
        scrape a page of search results and enqueue all foods to be scraped
        :param url: link to one page of search results
        """

        self.logger.scrape_search_results(url)

        r = self._make_request(url)
        if r is None:
            return

        soup = BeautifulSoup(r.content, 'html.parser')
        for link in soup.find_all('a', 'product'):
            product_link = "https://www.chewy.com" + link.get("href")
            self._enqueue_url(product_link, self.scrape_food_if_new)

    def _scrape_food_details(self, url: str) -> dict:
        """
        scrape page for dog food details and return a dict to be added to the db
        :param url: link to page containing food details
        :return: dictionary of food details
        """
        self.logger.scrape_food(url)

        r = self._make_request(url)
        if r.status_code != 200:
            raise Exception("Error requesting food at URL: {}".format(url))

        food = {"item_num": None,
                "url": url,
                "ingredients": None,
                "brand": None,
                "xsm_breed": 0,
                "sm_breed": 0,
                "md_breed": 0,
                "lg_breed": 0,
                "xlg_breed": 0,
                "food_form": None,
                "lifestage": None,
                "special_diet": [],
                "fda_guidelines": 0,
                }

        # TODO: scrape food details below

        # scrape item number

        # scrape ingredients

        # scrape brand

        # scrape breed sizes

        # scrape food form

        # scrape lifestage

        # scrape special diets

        # check ingredients for fda guidelines
        food = self._check_ingredients(food)

        return food

    def _make_request(self, url) -> requests.models.Response:
        """
        make a request for a web page using a new session header and proxy ip address
        :param url: link to web page
        :return: the response object from requests.get(), will be an empty response object if request fails
        """
        # TODO: Use a different header and proxy for each request
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0"}
        r = requests.models.Response()
        try:
            r = requests.get(url, headers=headers, timeout=1)
            r.raise_for_status()
        except requests.exceptions.Timeout as e:
            self.logger.error("Time out while requesting URL: {}".format(url))
            self.logger.error("REQUESTS ERROR: " + str(e.args))
            self.logger.error("Skipping URL...")
        except requests.exceptions.HTTPError as e:
            self.logger.error("HTTP Error while requesting URL: {}".format(url))
            self.logger.error("REQUESTS ERROR: " + str(e.args))
            self.logger.error("Skipping URL...")
        except Exception as e:
            self.logger.error("Unknown Error while requesting URL: {}".format(url))
            self.logger.error("ERROR: " + str(e.args))
            self.logger.error("Skipping URL...")
        finally:
            session.close()
        return r

    def _enter_in_db(self, food: dict) -> None:
        """
        enter a food item into the database
        :param food: dictionary containing food details to enter into database
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
        enqueue url to be scraped and scraper function in the scraper queue, for threads to start from
        :param url: url of page to scrape
        :param func: scraping method to use on url when job is executed - i.e. search page or food page
        """
        self.logger.enqueue(url, func)
        job = (url, func)
        self.queue.put(job)

    def _check_db_for_food(self, url: str) -> bool:
        """
        check the database to see if details about a food already exist
        :param url: link to page to check if details already exists in database
        :return: boolean True or False indicating if food at specified url is already in the database
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

    def _check_ingredients(self, food: dict) -> dict:
        """
        use regex to check for bad ingredients in a food
        :param food: dictionary containing details about food
        :return: new dictionary containing details about food, updated to reflect if it meets fda guidelines
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
