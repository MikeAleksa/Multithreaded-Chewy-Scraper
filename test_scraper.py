import sqlite3
from unittest import TestCase

from logger import VerboseScraperLogger
from scraper import Scraper


class TestScraper(TestCase):

    def setUp(self) -> None:
        self.s1 = Scraper(1, VerboseScraperLogger, "test_db.sqlite3")
        self.s2 = Scraper(1, VerboseScraperLogger, "test_db2.sqlite3")

    def tearDown(self) -> None:
        conn = sqlite3.connect(self.s1.db)
        cur = conn.cursor()
        query = 'DELETE FROM foods WHERE url != "www.test.com/1.html"'
        cur.execute(query)
        conn.commit()
        conn.close()

    def test_start(self):
        self.fail()

    def test__scrape_food(self):
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
                          "Pyridoxine Hydrochloride, Riboflavin Supplement, L-Ascorbyl-2-Polyphosphate (source of"
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

        self.assertEqual(self.s1._scrape_food(url1), test_food1)
        self.assertEqual(self.s1._scrape_food(url2), test_food2)
        
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
        food3 = {
            "ingredients": "this food has good ingredients, vitamins and minerals, then sweet potatoes - it's ok!",
            "fda_guidelines": 0}

        food1 = self.s1._check_ingredients(food1)
        food2 = self.s1._check_ingredients(food2)
        food3 = self.s1._check_ingredients(food3)

        self.assertEqual(food1['fda_guidelines'], 0)
        self.assertEqual(food2['fda_guidelines'], 1)
        self.assertEqual(food3['fda_guidelines'], 1)

    def test__make_request(self):
        r1 = self.s1._make_request("https://www.google.com/")
        r2 = self.s1._make_request("https://www.google.com/notarealsite")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r2.status_code, 404)
