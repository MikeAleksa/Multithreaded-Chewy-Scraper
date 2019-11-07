import json
import queue
import re
import sqlite3
from threading import Thread
from time import sleep

import requests
from bs4 import BeautifulSoup

from logger import ScraperLogger, SilentScraperLogger
from session_builder.session_builder import SessionBuilder


class Scraper:
    def __init__(self, database: str, num_threads: int = 5, db_connections: int = 5,
                 logger: ScraperLogger = SilentScraperLogger()):
        self.logger = logger

        # variables for queue of scraping jobs, thread pool
        self.threads = []
        for i in range(num_threads):
            self.threads.append(Thread(target=self.worker))
        self.scrape_queue = queue.Queue()

        # read useragents from file for scraping requests - for SessionBuilder()
        useragents = []
        try:
            with open("useragents.txt", "r") as useragent_file:
                for useragent in useragent_file.readlines():
                    useragents.append(useragent.strip())
        except FileNotFoundError:
            logger.error("Error opening useragents file...")

        # read api url and key from file for proxies - for SessionBuilder()
        api_data = None
        try:
            with open("api_data.json", "r") as api_data_file:
                api_data = json.load(api_data_file)
        except FileNotFoundError:
            logger.error("Error opening api-data file...")

        # create a session helper object for making new sessions using new useragents and proxies
        self.session_builder = SessionBuilder(api_data=api_data, useragents=useragents)

        # variables for managing database connections
        self.db: str = database

        # constants and compiled regex patterns
        self.db_columns = ", ".join(["item_num", "url", "ingredients", "brand", "xsm_breed", "sm_breed", "md_breed",
                                     "lg_breed", "xlg_breed", "food_form", "lifestage", "fda_guidelines"])
        self.vitamins_pattern = re.compile(
            "(mineral)|(vitamin)|(zinc)|(supplement)|(calcium)|(phosphorus)|(potassium)|(sodium)|" +
            "(magnesium)|(sulfer)|(sulfur)|(iron)|(iodine)|(selenium)|(copper)|(salt)|(chloride)|" +
            "(choline)|(lysine)|(taurine)"
        )
        self.bad_ingredients_pattern = re.compile("(pea)|(bean)|(lentil)|(potato)|(seed)|(soy)")

    def worker(self):
        """
        worker to pull jobs off of scrape_queue and execute the job, until queue is empty
        """
        while True:
            job = self.scrape_queue.get()
            if job is None:
                break
            url, scrape_func = job[0], job[1]
            scrape_func(url)
            self.scrape_queue.task_done()
            sleep(5)  # sleep for 5 seconds before making the next request

    def scrape(self, url: str, pages_of_results: int = 1) -> None:
        """
        Enqueue jobs to scrape all search pages for dog foods, which subsequently enqueue jobs to scrape food pages
        :param pages_of_results: the number of pages of search results to scrape through
        :param url: starting URL for search pages
        """
        # enqueue jobs to scrape all pages of search results
        for i in range(1, pages_of_results + 1):
            search_url = url + str(i)
            self._enqueue_url(search_url, self.scrape_search_results)

        # start worker threads
        for thread in self.threads:
            thread.start()

        # block until scrape queue is empty
        self.scrape_queue.join()

        # stop workers
        for _ in self.threads:
            self.scrape_queue.put(None)
        for thread in self.threads:
            thread.join()

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
                self.logger.error("Skipping food...\n")
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

        soup = BeautifulSoup(r.content, "html.parser")
        for link in soup.find_all("a", "product"):
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
                "fda_guidelines": 0,
                "special_diet": [],
                }

        soup = BeautifulSoup(r.content, "html.parser")

        # scrape item number
        self.logger.message("Scraping Item Number from {}".format(url))
        item_num = soup.find("div", string=re.compile("Item Number")).next_sibling.next_sibling.stripped_strings
        food["item_num"] = int(next(item_num))

        # scrape ingredients
        self.logger.message("Scraping Ingredients from {}".format(url))
        ingredients = soup.find("span", string=re.compile("Nutritional Info")).next_sibling.next_sibling
        food["ingredients"] = next(ingredients.p.stripped_strings)

        # scrape brand
        self.logger.message("Scraping Brand from {}".format(url))
        food["brand"] = str(soup.find("span", attrs={"itemprop": "brand"}).string)

        # scrape breed sizes
        self.logger.message("Scraping Breed Sizes from {}".format(url))
        breed_sizes = soup.find("div", string=re.compile("Breed Size"))
        if breed_sizes:
            breed_sizes = breed_sizes.next_sibling.next_sibling.stripped_strings
            breed_sizes = next(breed_sizes).split(', ')
            if "Extra Small & Toy Breeds" in breed_sizes:
                food["xsm_breed"] = 1
            if "Small Breeds" in breed_sizes:
                food["sm_breed"] = 1
            if "Medium Breeds" in breed_sizes:
                food["md_breed"] = 1
            if "Large Breeds" in breed_sizes:
                food["lg_breed"] = 1
            if "Giant Breeds" in breed_sizes:
                food["xlg_breed"] = 1

        # scrape food form
        self.logger.message("Scraping Food Form from {}".format(url))
        food_form = soup.find("div", string=re.compile("Food Form"))
        if food_form:
            food_form = food_form.next_sibling.next_sibling.stripped_strings
            food["food_form"] = next(food_form)

        # scrape lifestage
        self.logger.message("Scraping Lifestage from {}".format(url))
        lifestage = soup.find("div", string=re.compile("Lifestage"))
        if lifestage:
            lifestage.next_sibling.next_sibling.stripped_strings
            food["lifestage"] = next(lifestage)

        # scrape special diets
        self.logger.message("Scraping Special Diets from {}".format(url))
        special_diet = soup.find("div", string=re.compile("Special Diet"))
        if special_diet:
            special_diet.next_sibling.next_sibling.stripped_strings
            food["special_diet"] = next(special_diet).split(', ')

        # check ingredients for fda guidelines
        food = self._check_ingredients(food)

        return food

    def _make_request(self, url) -> requests.models.Response:
        """
        make a request for a web page using a new session header and proxy ip address
        :param url: link to web page
        :return: the response object from requests.get(), will be an empty response object if request fails
        """
        session = self.session_builder.create_session()
        r = requests.models.Response()
        self.logger.make_request(url, session.headers["User-Agent"], session.proxies)

        try:
            r = session.get(url, timeout=10)
            r.raise_for_status()
        except requests.exceptions.ProxyError as e:
            self.logger.error("Proxy Error while requesting URL: {} with PROXY {}".format(url, session.proxies))
            self.logger.error("PROXY ERROR: " + str(e.args))
            self.logger.error("Retrying with new proxy...\n")
            session.close()
            return self._make_request(url)
        except requests.exceptions.Timeout as e:
            self.logger.error("Time out while requesting URL: {}".format(url))
            self.logger.error("REQUESTS ERROR: " + str(e.args))
            self.logger.error("Skipping URL...\n")
        except requests.exceptions.HTTPError as e:
            self.logger.error("HTTP Error while requesting URL: {}".format(url))
            self.logger.error("REQUESTS ERROR: " + str(e.args))
            self.logger.error("Skipping URL...\n")
        except Exception as e:
            self.logger.error("Unknown Error while requesting URL: {}".format(url))
            self.logger.error("ERROR: " + str(e.args))
            self.logger.error("Skipping URL...\n")
        finally:
            session.close()
        return r

    def _enter_in_db(self, food: dict) -> None:
        """
        enter a food item into the database
        :param food: dictionary containing food details to enter into database
        """
        self.logger.enter_in_db(food)

        # split special diets from food
        special_diets = food.pop('special_diet')

        # generate insert statements
        values = str()
        for index, value in enumerate(food.values()):
            if isinstance(value, str):
                values += ', "{}"'.format(value)
            else:
                if index != 0:
                    values += ", "
                values += str(value)
        food_query = 'INSERT INTO foods ({}) VALUES({})'.format(self.db_columns, values)

        # try to execute and commit input statement for food
        with sqlite3.connect(self.db) as conn:
            try:
                cur = conn.cursor()
                cur.execute(food_query)
                conn.commit()
            except sqlite3.Error as e:
                self.logger.error("Error while executing query: {}".format(food_query))
                self.logger.error("SQLITE3 ERROR: " + str(e.args))
                self.logger.error("Rolling back...\n")
                conn.rollback()

        # try to execute and commit input statement for special diets
        with sqlite3.connect(self.db) as conn:
            try:
                cur = conn.cursor()
                for diet in special_diets:
                    diet_query = 'INSERT INTO diets ("diet", "item_num") VALUES ("{}", "{}");'.format(diet,
                                                                                                      food['item_num'])
                    cur.execute(diet_query)
                conn.commit()
            except sqlite3.Error as e:
                self.logger.error("Error while executing query: {}".format(diet_query))
                self.logger.error("SQLITE3 ERROR: " + str(e.args))
                self.logger.error("Rolling back...\n")
                conn.rollback()

    def _enqueue_url(self, url: str, func) -> None:
        """
        enqueue url to be scraped and scraper function in the scraper queue, for threads to start from
        :param url: url of page to scrape
        :param func: scraping method to use on url when job is executed - i.e. search page or food page
        """
        self.logger.enqueue(url, func)
        job = (url, func)
        self.scrape_queue.put(job)

    def _check_db_for_food(self, url: str) -> bool:
        """
        check the database to see if details about a food already exist
        :param url: link to page to check if details already exists in database
        :return: boolean True or False indicating if food at specified url is already in the database
        """
        self.logger.food_in_db(url)
        results = None

        with sqlite3.connect(self.db) as conn:
            try:
                cur = conn.cursor()
                # trim final part of the url path, as it relates to the product size variants,
                #   which we aren't concerned with
                cur.execute('SELECT * FROM foods WHERE url LIKE "{}/_____"'.format(url[:-6]))
                results = cur.fetchall()
            except sqlite3.Error as e:
                self.logger.error("Error checking if food in database: {}".format(url))
                self.logger.error("SQLITE3 ERROR: " + str(e.args))
                self.logger.error("Rolling back...\n")
                conn.rollback()
            except TypeError as e:
                self.logger.error("Error checking if food in database: {}".format(url))
                self.logger.error("TypeError: " + str(e.args))
                self.logger.error("Rolling back...\n")

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
        main_ingredients = self.vitamins_pattern.split(food["ingredients"].lower(), maxsplit=1)[0]
        results = self.bad_ingredients_pattern.findall(main_ingredients)

        if not results:
            food["fda_guidelines"] = 1
        else:
            food["fda_guidelines"] = 0

        return food
