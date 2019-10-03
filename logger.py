# logger.py defines a logger object for logging and debugging the scraper

import os
import time


class ScraperLogger:
    def __init__(self, scraper):
        self.scraper = scraper

    @staticmethod
    def get_date():
        c_date: str = str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + str(time.localtime()[2])
        return c_date

    @staticmethod
    def get_time():
        c_time: str = str(time.localtime()[3]) + ":" + str(time.localtime()[4]) + ":" + str(time.localtime()[5])
        return c_time

    def scrape_food(self, url: str):
        pass

    def scrape_search_results(self, url: str):
        pass

    def enqueue(self, url: str, func):
        pass

    def food_in_db(self, url: str):
        pass

    def enter_in_db(self, food: dict):
        pass

    def check_ingredients(self, food: dict):
        pass


class SilentScraperLogger(ScraperLogger):
    pass


class VerboseScraperLogger(ScraperLogger):
    def __init__(self, scraper):
        super().__init__(scraper)

        # make directory for logs if it doesn't exist
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # start log file
        c_date: str = self.get_date()
        c_time: str = self.get_time()
        logfile_name: str = "logs/" + c_date + "_" + c_time + "_logfile.txt"
        self.logfile = open(logfile_name, "w")
        self.logfile.write("LOG FILE STARTED: {} {}\n\n".format(c_date, c_time))

    def __del__(self):
        self.logfile.close()

    def scrape_food(self, url: str):
        self.logfile.write("{} - Scraping food details from URL: {}\n\n".format(self.get_time(), url))

    def scrape_search_results(self, url: str):
        self.logfile.write("{} - Scraping search results from URL: {}\n\n".format(self.get_time(), url))

    def enter_in_db(self, food: dict):
        self.logfile.write("{} - Entering food: {} into database...\n\n".format(self.get_time(), food))

    def enqueue(self, url: str, func):
        self.logfile.write("{} - Enqueuing URL: {} with FUNC: {}\n\n".format(self.get_time(), url, func))

    def food_in_db(self, url: str):
        self.logfile.write("{} - Checking DB for entry with URL: {}\n\n".format(self.get_time(), url))

    def check_ingredients(self, food: dict):
        self.logfile.write("{} - Checking ingredients in food: {}\n\n".format(self.get_time(), food))
