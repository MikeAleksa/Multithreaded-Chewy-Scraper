# logger.py defines a logger object for logging and debugging the scraper

import os
import time


class ScraperLogger:
    def __init__(self, scraper):
        self.scraper = scraper

        # make directory for logs if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')

        # start log file
        c_date = self.get_date()
        c_time = self.get_time()
        self.logfile = open("logs/" + c_date + "_" + c_time + "_logfile.txt", "w")
        self.logfile.write("LOG FILE STARTED: {} {}".format(c_date, c_time))

    def __del___(self):
        self.logfile.close()

    @staticmethod
    def get_date():
        c_date = str(time.localtime()[0]) + '-' + str(time.localtime()[1]) + '-' + str(time.localtime()[2])
        return c_date

    @staticmethod
    def get_time():
        c_time = str(time.localtime()[3]) + ':' + str(time.localtime()[4]) + ':' + str(time.localtime()[5])
        return c_time

    def scrape_food(self, url):
        pass

    def scrape_search_results(self, url):
        pass

    def enqueue(self, url, func):
        pass

    def food_in_db(self, url):
        pass

    def enter_in_db(self, food):
        pass


class SilentScraperLogger(ScraperLogger):
    pass


class VerboseScraperLogger(ScraperLogger):
    def scrape_food(self, url):
        self.logfile.write(self.get_time() + " - Attempting to scrape food details from URL: {}".format(url))

    def scrape_search_results(self, url):
        self.logfile.write(self.get_time() + " - Attempting to scrape search results from URL: {}".format(url))

    def enqueue(self, url, func):
        self.logfile.write(self.get_time() + " - Enqueuing URL: {} with FUNC: {}".format(url, func))

    def food_in_db(self, url):
        self.logfile.write(self.get_time() + " - Checking DB for entry with URL: {}".format(url))

    def enter_in_db(self, food):
        self.logfile.write(self.get_time() + " - Entering food: {} into database...".format(food))
