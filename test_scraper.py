from unittest import TestCase

from scraper import Scraper


class TestScraper(TestCase):

    def setUp(self) -> None:
        self.scraper = Scraper(1, None, 'db.sqlite3')

    def test_start(self):
        self.fail()

    def test__scrape_search_results(self):
        self.fail()

    def test__scrape_food(self):
        self.fail()

    def test__enter_in_db(self):
        self.fail()

    def test__enqueue_url(self):
        self.fail()

    def test__food_in_db(self):
        self.fail()

    def test__check_and_enter_food(self):
        self.fail()
