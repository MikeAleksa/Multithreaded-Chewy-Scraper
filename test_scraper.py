from unittest import TestCase

from logger import VerboseScraperLogger
from scraper import Scraper


class TestScraper(TestCase):

    def setUp(self) -> None:
        pass

    def test_start(self):
        self.fail()

    def test__scrape_food(self):
        self.fail()

    def test__scrape_search_results(self):
        self.fail()

    def test__enter_in_db(self):
        import time

        test_key = hash(time.localtime)
        scraper = Scraper(1, VerboseScraperLogger, "test_db.sqlite3")

        new_food = {
            "item_num": test_key,
            "url": str(test_key),
            "ingredients": "None",
            "brand": "None",
            "xsm_breed": 0,
            "sm_breed": 0,
            "md_breed": 0,
            "lg_breed": 0,
            "xlg_breed": 0,
            "food_form": "None",
            "lifestage": "None",
            "special_diet": "None",
            "fda_guidelines": 0,
        }

        self.assertFalse(scraper._food_in_db(url=test_key))
        scraper._enter_in_db(new_food)
        self.assertTrue(scraper._food_in_db(url=test_key))

    def test__enqueue_url(self):
        self.fail()

    def test__food_in_db(self):
        scraper = Scraper(1, VerboseScraperLogger, "test_db.sqlite3")
        scraper2 = Scraper(1, VerboseScraperLogger, "this database doesn't exist - force error")

        self.assertTrue(scraper._food_in_db(url="www.test.com/1.html"))
        self.assertFalse(scraper._food_in_db(url="this entry is not in the database"))

        self.assertFalse(scraper2._food_in_db(url=None))

    def test__check_and_enter_food(self):
        self.fail()

    def test__check_ingredients(self):
        scraper = Scraper(1, VerboseScraperLogger, "test_db.sqlite3")

        food1 = {"ingredients": "chicken, lentils, potatoes - this one's bad", "fda_guidelines": 0}
        food2 = {"ingredients": "just chicken in this food - its good!", "fda_guidelines": 0}
        food3 = {"ingredients": "this food has good ingredients, vitamins and minerals, then sweet potatoes - it's ok!",
                 "fda_guidelines": 0}

        food1 = scraper._check_ingredients(food1)
        food2 = scraper._check_ingredients(food2)
        food3 = scraper._check_ingredients(food3)

        self.assertEqual(food1['fda_guidelines'], 0)
        self.assertEqual(food2['fda_guidelines'], 1)
        self.assertEqual(food3['fda_guidelines'], 1)
