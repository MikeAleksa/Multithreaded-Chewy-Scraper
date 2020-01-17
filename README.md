# Multithreaded-Chewy-Scraper
A webscraper for Chewy.com, using multi-threading, proxy cycling, and SQLAlchemy to scrape and save information about dog foods in a MySQL database.

This scraper is used to provide data for a Django web application, which allows people to search for and find a suitable food for their dog, or verify the suitability of a food they already buy.

# Overview
My vet recently cautioned me against grain-free diets and pointed me to a recent (2019) FDA study found [here](https://wayback.archive-it.org/7993/20190423043549/https://www.fda.gov/AnimalVeterinary/NewsEvents/ucm630993.htm) and summed up [here](https://wayback.archive-it.org/7993/20190423023017/https://www.fda.gov/AnimalVeterinary/ResourcesforYou/AnimalHealthLiteracy/ucm616279.htm) that indicate these diets can cause canine dilated cardiomyopathy (DCM).

To summarize:
* The FDA is cautioning against feeding dogs food that contains legumes, pulses (seeds of legumes), and/or (sweet) potatoes as main ingredients in the food
* Main ingredients are considered to be listed in a food's ingredient list before the first vitamin or mineral ingredient.
* Common legumes include peas, beans, lentils, chickpeas, soybeans and peanuts. Pulses are dry edible seeds of certain legume plants. Examples include dried beans, dried peas, chickpeas and lentils.
* Rice is a grain, not a legume. The current reports do not suggest there is any link between diets with rice and DCM in dogs.
* Grain-free diets are not necessarily specifically implicated, but recently the proportion of legumes and/or pulses has increased significantly in these diets.

This project scrapes info from Chewy.com, checks the ingredients of each food to see if they fit these guidelines, and saves the results to a MySQL database.

# Configuration
* To configure database access, database details should be entered in the scraperdb.cnf configuration file. 
* To configure proxy cycling using a Proxybonanza account, API details should be entered in the session_builder/api_data.json file.
