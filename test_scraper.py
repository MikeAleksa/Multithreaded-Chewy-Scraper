from unittest import TestCase

from logger import VerboseScraperLogger
from scraper import Scraper


class TestScraper(TestCase):

    def setUp(self):
        self.s1 = Scraper(1, VerboseScraperLogger, "test_db.sqlite3")
        self.s2 = Scraper(1, VerboseScraperLogger, "test_db.sqlite3")

    def test_start(self):
        self.fail()

    def test__scrape_food(self):
        self.fail()

    def test__scrape_search_results(self):
        # url for search results containing only 4 foods
        url = "https://www.chewy.com/s?rh=c%3A288%2Cc%3A332%2Cc%3A294%2CFoodFlavor%3ABison&sort=relevance"
        expected_urls = {("https://www.chewy.com/earthborn-holistic-great-plains-feast/dp/36412",
                          self.s1._check_and_enter_food),
                         ("https://www.chewy.com/natural-balance-lid-limited/dp/104666",
                          self.s1._check_and_enter_food),
                         ("https://www.chewy.com/taste-wild-ancient-prairie-roasted/dp/217982",
                          self.s1._check_and_enter_food),
                         ("https://www.chewy.com/rachael-ray-nutrish-peak-natural/dp/181686",
                          self.s1._check_and_enter_food)}
        self.s1._scrape_search_results(url)
        self.assertEqual(self.s1.queue, expected_urls)

    def test__enter_in_db(self):
        import time

        test_key = hash(time.localtime)
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

        self.assertFalse(self.s1._food_in_db(url=str(test_key)))
        self.s1._enter_in_db(new_food)
        self.assertTrue(self.s1._food_in_db(url=str(test_key)))

    def test__enqueue_url(self):
        def dummyFunction():
            pass

        self.assertNotEqual(self.s1.queue, {('www.test.com', dummyFunction)})
        self.s1._enqueue_url('www.test.com', dummyFunction)
        self.assertEqual(self.s1.queue, {('www.test.com', dummyFunction)})

    def test__food_in_db(self):
        self.assertTrue(self.s1._food_in_db(url="www.test.com/1.html"))
        self.assertFalse(self.s1._food_in_db(url="this entry is not in the database"))
        self.assertFalse(self.s2._food_in_db(url=None))

    def test__check_and_enter_food(self):
        self.fail()

    def test__check_ingredients(self):
        food1 = {"ingredients": "chicken, lentils, potatoes - this one's bad", "fda_guidelines": 0}
        food2 = {"ingredients": "just chicken in this food - its good!", "fda_guidelines": 0}
        food3 = {"ingredients": "this food has good ingredients, vitamins and minerals, then sweet potatoes - it's ok!",
                 "fda_guidelines": 0}

        food1 = self.s1._check_ingredients(food1)
        food2 = self.s1._check_ingredients(food2)
        food3 = self.s1._check_ingredients(food3)

        self.assertEqual(food1['fda_guidelines'], 0)
        self.assertEqual(food2['fda_guidelines'], 1)
        self.assertEqual(food3['fda_guidelines'], 1)
