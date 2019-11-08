import os
import time


class ScraperLogger:
    """
    Base Logger class - should implement a more specific Logger that inherits from this class
    """
    def __init__(self):
        pass

    @staticmethod
    def get_date():
        """
        :return: current date
        """
        c_date: str = str(time.localtime()[0]) + "-" + str(time.localtime()[1]) + "-" + str(time.localtime()[2])
        return c_date

    @staticmethod
    def get_time():
        """
        :return: current time
        """
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

    def error(self, msg: str):
        pass

    def make_request(self, url: str, agent: str, proxies: dict):
        pass

    def message(self, msg: str):
        pass


class SilentScraperLogger(ScraperLogger):
    """
    No logging - don't generate any log file or logging data
    """
    pass


class ErrorScraperLogger(ScraperLogger):
    """
    Log error messages only
    """
    def __init__(self):
        """
        Create a log directory if needed, and log file, named using the current date/time,
        """
        super().__init__()

        # make directory for logs if it doesn't exist
        if not os.path.exists("logs"):
            os.mkdir("logs")

        # start log file
        c_date: str = self.get_date()
        c_time: str = self.get_time()
        logfile_name: str = "logs/" + c_date + "_" + c_time + "_logfile.txt"
        if not os.path.exists(logfile_name):
            self.logfile = open(logfile_name, "a")
            self.logfile.write("LOG FILE STARTED: {}\n\n".format(time.asctime()))
        else:
            self.logfile = open(logfile_name, "a")

    def __del__(self):
        self.logfile.close()

    def error(self, msg: str):
        self.logfile.write("{} - {}\n".format(self.get_time(), msg))


class VerboseScraperLogger(ErrorScraperLogger):
    """
    Log all events to log file
    """
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

    def make_request(self, url: str, agent: str, proxies: dict):
        self.logfile.write(
            "{} - Using PROXY: {} to make request for URL: {} using USER AGENT: {}\n\n".format(self.get_time(), proxies,
                                                                                               url, agent))

    def message(self, msg: str):
        self.logfile.write(msg + '\n')
