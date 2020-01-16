from unittest import TestCase

from scraper import Scraper, Food
from scraper_logger import VerboseScraperLogger


class TestScraper(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.logger = VerboseScraperLogger()

    def setUp(self) -> None:
        self.s = Scraper(database="testscraperdb.cnf", logger=self.logger)
        self.s._enter_update_time()

    def tearDown(self) -> None:
        self.s.engine.dispose()

    def test_scrape_search_results(self):
        # url for search results containing only 4 foods
        url = "https://www.chewy.com/s?rh=c%3A288%2Cc%3A332%2Cbrand_facet%3AAdirondack"

        # dont use number after final /dp/ - corresponds to size of product and doesn't reliable return the
        #   same size; doesn't matter for scraper since we're not looking at price per pound, etc.
        expected_jobs = {("https://www.chewy.com/adirondack-30-high-fat-puppy/dp",
                          self.s.scrape_food_if_new),
                         ("https://www.chewy.com/adirondack-26-adult-active-recipe-dry/dp",
                          self.s.scrape_food_if_new),
                         ("https://www.chewy.com/adirondack-large-breed-recipe-dry-dog/dp",
                          self.s.scrape_food_if_new),
                         ("https://www.chewy.com/adirondack-21-adult-everyday-recipe/dp",
                          self.s.scrape_food_if_new)}

        self.s.scrape_search_results(url)
        generated_jobs = set()
        while not self.s.scrape_queue.empty():
            job = self.s.scrape_queue.get()
            job = (job[0].rsplit('/', 1)[0], job[1])
            generated_jobs.add(job)
        self.assertEqual(expected_jobs, generated_jobs)

    def test__scrape_food_details(self):
        url1 = "https://www.chewy.com/earthborn-holistic-great-plains-feast/dp/36412"
        food1, diets1 = self.s._scrape_food_details(url1)
        self.assertEqual(51256, food1.item_num)
        self.assertEqual("Earthborn Holistic Great Plains Feast Grain-Free Natural Dry Dog Food", food1.name)
        self.assertEqual("https://www.chewy.com/earthborn-holistic-great-plains-feast/dp/36412", food1.url)
        test_ingredients1 = (
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
            "Fermentation Product.")
        self.assertEqual(test_ingredients1, food1.ingredients)
        self.assertEqual("Earthborn Holistic", food1.brand)
        self.assertEqual(None, food1.xsm_breed)
        self.assertEqual(True, food1.sm_breed)
        self.assertEqual(True, food1.md_breed)
        self.assertEqual(True, food1.lg_breed)
        self.assertEqual(None, food1.xlg_breed)
        self.assertEqual("Dry Food", food1.food_form)
        self.assertEqual("Adult", food1.lifestage)
        self.assertEqual(False, food1.fda_guidelines)
        test_diets1 = ["Grain-Free",
                       "Gluten Free"]
        self.assertEqual(test_diets1, diets1)

        url2 = "https://www.chewy.com/natural-balance-lid-limited/dp/104666"
        food2, diets2 = self.s._scrape_food_details(url2)
        self.assertEqual(76793, food2.item_num)
        self.assertEqual(
            "Natural Balance L.I.D. Limited Ingredient Diets Sweet Potato & Bison Formula Grain-Free Dry Dog Food",
            food2.name)
        self.assertEqual("https://www.chewy.com/natural-balance-lid-limited/dp/104666", food2.url)
        test_ingredients2 = (
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
            "Tocopherols (preservative), Rosemary Extract.")
        self.assertEqual(test_ingredients2, food2.ingredients)
        self.assertEqual("Natural Balance", food2.brand)
        self.assertEqual(None, food2.xsm_breed)
        self.assertEqual(True, food2.sm_breed)
        self.assertEqual(True, food2.md_breed)
        self.assertEqual(True, food2.lg_breed)
        self.assertEqual(None, food2.xlg_breed)
        self.assertEqual("Dry Food", food2.food_form)
        self.assertEqual("Adult", food2.lifestage)
        self.assertEqual(False, food2.fda_guidelines)
        test_diets2 = [
            "Sensitive Digestion",
            "Limited Ingredient Diet",
            "No Corn No Wheat No Soy",
            "Grain-Free"]
        self.assertEqual(test_diets2, diets2)

    def test__enter_in_db(self):
        import time

        test_key = hash(time.localtime)
        test_url = str(test_key) + "/12345"
        test_name = str(test_key)
        test_diets = ['Sensitive Digestion', 'Limited Ingredient Diet', 'No Corn No Wheat No Soy', 'Grain-Free']
        test_food = Food(
            item_num=test_key,
            name=test_name,
            url=test_url,
            ingredients="None",
            brand="None",
            xsm_breed=False,
            sm_breed=False,
            md_breed=False,
            lg_breed=False,
            xlg_breed=False,
            food_form="None",
            lifestage="None",
            fda_guidelines=False
        )

        self.assertFalse(self.s._check_db_for_food(url=test_url))
        self.s._enter_in_db(test_food, test_diets)
        self.assertTrue(self.s._check_db_for_food(url=test_url))

    def test__enqueue_url(self):
        def dummy_function():
            pass

        self.s._enqueue_url("www.test.com", dummy_function)
        url, func = self.s.scrape_queue.get()
        self.assertEqual("www.test.com", url)
        self.assertEqual(dummy_function, func)

    def test__check_db_for_food(self):
        self.assertTrue(self.s._check_db_for_food(url="www.test.com/1/54321"))
        self.assertFalse(self.s._check_db_for_food(url="this entry is not in the database/12345"))

    def test__check_ingredients(self):
        food1 = Food(ingredients="chicken, lentils, potatoes - this one's bad")
        food2 = Food(ingredients="just chicken in this food - its good!")
        food3 = Food(ingredients="this food has good ingredients, vitamins and minerals, then sweet potatoes - ok!")

        food1 = self.s._check_ingredients(food1)
        food2 = self.s._check_ingredients(food2)
        food3 = self.s._check_ingredients(food3)

        self.assertEqual(False, food1.fda_guidelines)
        self.assertEqual(True, food2.fda_guidelines)
        self.assertEqual(True, food3.fda_guidelines)

    def test__make_request(self):
        r1 = self.s._make_request("https://www.google.com/")
        r2 = self.s._make_request("https://www.google.com/notarealsite")
        self.assertEqual(200, r1.status_code)
        self.assertEqual(404, r2.status_code)

    def test__pages_of_results(self):
        results = self.s._pages_of_results('https://www.chewy.com/s?rh=c%3A288%2Cc%3A332&page=1')
        self.assertEqual(100, results)
        results = self.s._pages_of_results('https://www.chewy.com/s?rh=c%3A288%2Cc%3A332%2Cc%3A294')
        self.assertEqual(43, results)
