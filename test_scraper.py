import sqlite3
import threading
from unittest import TestCase

from logger import VerboseScraperLogger
from scraper import Scraper


class TestScraper(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.logger = VerboseScraperLogger()

    def setUp(self) -> None:
        self.s1 = Scraper(database="test_db.sqlite3", logger=self.logger)
        self.s2 = Scraper(database="test_db2.sqlite3", logger=self.logger)

    def tearDown(self) -> None:
        conn = sqlite3.connect(self.s1.db)
        cur = conn.cursor()
        query = 'DELETE FROM foods WHERE url NOT LIKE "www.test.com/1/_____"'
        cur.execute(query)
        conn.commit()
        conn.close()

    def test_scrape_food_if_new(self):
        # TODO: test scrape_food_if_new()
        self.fail("No test written for this method")

    def test_scrape_search_results(self):
        # url for search results containing only 4 foods
        url = "https://www.chewy.com/s?rh=c%3A288%2Cc%3A332%2Cbrand_facet%3AAdirondack"

        # dont use 6-digit number after final /dp/ - corresponds to size of product and doesn't reliable return the
        #   same size; doesn't matter for scraper since we're not looking at price per pound, etc.
        expected_jobs = {("https://www.chewy.com/adirondack-30-high-fat-puppy/dp/",
                          self.s1.scrape_food_if_new),
                         ("https://www.chewy.com/adirondack-26-adult-active-recipe-dry/dp/",
                          self.s1.scrape_food_if_new),
                         ("https://www.chewy.com/adirondack-large-breed-recipe-dry-dog/dp/",
                          self.s1.scrape_food_if_new),
                         ("https://www.chewy.com/adirondack-21-adult-everyday-recipe/dp/",
                          self.s1.scrape_food_if_new)}
        self.s1.scrape_search_results(url)
        generated_jobs = set()
        while not self.s1.scrape_queue.empty():
            job = self.s1.scrape_queue.get()
            job = (job[0][:-6], job[1])
            generated_jobs.add(job)
        self.assertEqual(expected_jobs, generated_jobs)

    def test__scrape_food_details(self):
        url1 = "https://www.chewy.com/earthborn-holistic-great-plains-feast/dp/36412"
        test_food1 = {"item_num": 51256,
                      "url": "https://www.chewy.com/earthborn-holistic-great-plains-feast/dp/36412",
                      "ingredients": (
                          "Bison Meal, Peas, Pea Protein, Tapioca, Dried Egg, Canola Oil (preserved with Mixed "
                          "Tocopherols), Beef Meal, Pacific Whiting Meal, Pea Starch, Chickpeas, Flaxseed, "
                          "Alaska Pollock Meal, Natural Flavors, Pea Fiber, Blueberries, Cranberries, Apples, "
                          "Carrots, Spinach, Salt, Potassium Chloride, Choline Chloride, DL-Methionine, "
                          "L-Lysine, Taurine, L-Carnitine, Beta-Carotene, Vitamin A Supplement, Vitamin D3 "
                          "Supplement, Vitamin E Supplement, Zinc Sulfate, Ferrous Sulfate, Niacin, Folic Acid, "
                          "Biotin, Manganese Sulfate, Copper Sulfate, Calcium Pantothenate, Thiamine Mononitrate, "
                          "Pyridoxine Hydrochloride, Riboflavin Supplement, L-Ascorbyl-2-Polyphosphate (source of "
                          "Vitamin C), Zinc Proteinate, Manganese Proteinate, Copper Proteinate, Calcium Iodate, "
                          "Sodium Selenite, Cobalt Carbonate, Vitamin B12 Supplement, Yucca Schidigera Extract, "
                          "Rosemary Extract, Dried Enterococcus Faecium Fermentation Product, Dried "
                          "Lactobacillus Casei Fermentation Product, Dried Lactobacillus Acidophilus "
                          "Fermentation Product."),
                      "brand": "Earthborn Holistic",
                      "xsm_breed": 0,
                      "sm_breed": 1,
                      "md_breed": 1,
                      "lg_breed": 1,
                      "xlg_breed": 0,
                      "food_form": "Dry Food",
                      "lifestage": "Adult",
                      "special_diet": ["Grain-Free",
                                       "Gluten Free"],
                      "fda_guidelines": 0,
                      }

        url2 = "https://www.chewy.com/natural-balance-lid-limited/dp/104666"
        test_food2 = {"item_num": 76793,
                      "url": "https://www.chewy.com/natural-balance-lid-limited/dp/104666",
                      "ingredients": (
                          "Sweet Potatoes, Bison, Potato Protein, Pea Protein, Canola Oil (Preserved with "
                          "Mixed Tocopherols), Dicalcium Phosphate, Natural Flavor, Salmon Oil (Preserved "
                          "with Mixed Tocopherols), Potato Fiber, Salt, Calcium Carbonate, Flaxseed, "
                          "DL-Methionine, Minerals (Zinc Amino Acid Chelate, Zinc Sulfate, Ferrous "
                          "Sulfate, Iron Amino Acid Chelate, Copper Sulfate, Copper Amino Acid Chelate, "
                          "Sodium Selenite, Manganese Sulfate, Manganese Amino Acid Chelate, Calcium "
                          "Iodate), Vitamins (Vitamin E Supplement, Niacin, d-Calcium Pantothenate, "
                          "Vitamin A Supplement, Riboflavin Supplement, Thiamine Mononitrate, Biotin, "
                          "Vitamin B12 Supplement, Pyridoxine Hydrochloride, Vitamin D3 Supplement, "
                          "Folic Acid), Choline Chloride, Taurine, Citric Acid (preservative), Mixed "
                          "Tocopherols (preservative), Rosemary Extract."),
                      "brand": "Natural Balance",
                      "xsm_breed": 0,
                      "sm_breed": 1,
                      "md_breed": 1,
                      "lg_breed": 1,
                      "xlg_breed": 0,
                      "food_form": "Dry Food",
                      "lifestage": "Adult",
                      "special_diet": [
                          "Sensitive Digestion",
                          "Limited Ingredient Diet",
                          "No Corn No Wheat No Soy",
                          "Grain-Free"],
                      "fda_guidelines": 0,
                      }

        self.assertEqual(test_food1, self.s1._scrape_food_details(url1))
        self.assertEqual(test_food2, self.s1._scrape_food_details(url2))
        
    def test__enter_in_db(self):
        import time

        test_key = hash(time.localtime)
        test_url = str(test_key) + "/12345"
        test_diets = ['Sensitive Digestion', 'Limited Ingredient Diet', 'No Corn No Wheat No Soy', 'Grain-Free']
        new_food = {
            "item_num": test_key,
            "url": test_url,
            "ingredients": "None",
            "brand": "None",
            "xsm_breed": 0,
            "sm_breed": 0,
            "md_breed": 0,
            "lg_breed": 0,
            "xlg_breed": 0,
            "food_form": "None",
            "lifestage": "None",
            "fda_guidelines": 0,
            "special_diet": test_diets,
        }

        self.assertFalse(self.s1._check_db_for_food(url=test_url))
        self.s1._enter_in_db(new_food)
        self.assertTrue(self.s1._check_db_for_food(url=test_url))

    def test__enqueue_url(self):
        def dummy_function():
            pass

        self.s1._enqueue_url("www.test.com", dummy_function)
        url, func = self.s1.scrape_queue.get()
        self.assertEqual("www.test.com", url)
        self.assertEqual(dummy_function, func)

    def test__check_db_for_food(self):
        self.assertTrue(self.s1._check_db_for_food(url="www.test.com/1/12345"))
        self.assertFalse(self.s1._check_db_for_food(url="this entry is not in the database/12345"))
        self.assertFalse(self.s2._check_db_for_food(url=None))

    def test__check_ingredients(self):
        food1 = {"ingredients": "chicken, lentils, potatoes - this one's bad", "fda_guidelines": 0}
        food2 = {"ingredients": "just chicken in this food - its good!", "fda_guidelines": 0}
        food3 = {
            "ingredients": "this food has good ingredients, vitamins and minerals, then sweet potatoes - it's ok!",
            "fda_guidelines": 0}

        food1 = self.s1._check_ingredients(food1)
        food2 = self.s1._check_ingredients(food2)
        food3 = self.s1._check_ingredients(food3)

        self.assertEqual(0, food1['fda_guidelines'])
        self.assertEqual(1, food2['fda_guidelines'])
        self.assertEqual(1, food3['fda_guidelines'])

    def test__make_request(self):
        r1 = self.s1._make_request("https://www.google.com/")
        r2 = self.s1._make_request("https://www.google.com/notarealsite")
        self.assertEqual(200, r1.status_code)
        self.assertEqual(404, r2.status_code)

        # TODO: get return value from threads to check with assertion
        threads = []
        results = []
        for _ in range(10):
            threads.append(threading.Thread(target=self.s1._make_request, args=("https://www.google.com/",)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
