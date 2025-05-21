# app/cache.py

import time
import gc
import logging
import json
import os
from app.scraper.event_scaper import EventScraper
from app.scraper.opportunity_scraper import OpportunityScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sys

logger = logging.getLogger(__name__)

# Links configuration
links = {
    "events": {
        "india": "https://www.conferencealerts.in/india",
        "ai": "https://www.conferencealerts.in/ai",
        "computer-science": "https://www.conferencealerts.in/computer-science",
        # "cybersecurity": "https://www.conferencealerts.in/cybersecurity",
        # "iot": "https://www.conferencealerts.in/iot",
        # "natural-language-processing": "https://www.conferencealerts.in/natural-language-processing",
        # "robotics": "https://www.conferencealerts.in/robotics",
        # "software-engineering": "https://www.conferencealerts.in/software-engineering",
        # "bioinformatics": "https://www.conferencealerts.in/bioinformatics",
        # "biomedical-engineering": "https://www.conferencealerts.in/biomedical-engineering",
        # "biotechnology": "https://www.conferencealerts.in/biotechnology",
        # "nanotechnology": "https://www.conferencealerts.in/nanotechnology",
        # "material-science": "https://www.conferencealerts.in/material-science",
        # "civil-engineering": "https://www.conferencealerts.in/civil-engineering",
        # "design": "https://www.conferencealerts.in/design",
        # "industrial-engineering": "https://www.conferencealerts.in/industrial-engineering",
        # "manufacturing": "https://www.conferencealerts.in/manufacturing",
        # "mining": "https://www.conferencealerts.in/mining",
        # "structural-engineering": "https://www.conferencealerts.in/structural-engineering",
        # "marine-engineering": "https://www.conferencealerts.in/marine-engineering",
        # "aeronautical": "https://www.conferencealerts.in/aeronautical",
        # "electronics": "https://www.conferencealerts.in/electronics",
        # "electrical": "https://www.conferencealerts.in/electrical",
        # "engineering": "https://www.conferencealerts.in/engineering"
    },
    "opportunities": {
        "iitr": "https://iitr.ac.in/Careers/Project%20Jobs.html",
        "iitk": "https://www.iitk.ac.in/dord/scientific-and-research-staff",
        "iitb" : "https://acr.iitbombay.org/careers/iitbombay-career-centres-and-projects",
        # "iitd" : "https://ird.iitd.ac.in/vacancies",
        "iisc" : "https://iisc.ac.in/careers/contract-project-staff",
        "iitg" : "https://www.iitg.ac.in/iitg_reqr?ct=RzNJNURKa005enFYa3RJWWtvM2cvQT09",
        "iitkgp" : "https://erp.iitkgp.ac.in/SricWeb/temporaryJobs.htm",
        "iitm" : "https://facapp.iitm.ac.in/"

    }
}

# Cache store
cache = {
    "events": {key: [] for key in links["events"]},
    "opportunities": {key: [] for key in links["opportunities"]},
    "last_updated": 0
}

CACHE_FILE_PATH = "app/cache_store.json"
CACHE_UPDATE_INTERVAL_SECONDS = 3600

def get_chrome_options():
    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080") 
    options.add_argument("--log-level=3") 
    options.add_argument("--disable-extensions") 
    options.add_argument("--disable-crash-reporter") 
    return options

def save_cache_to_file():
    try:
        with open(CACHE_FILE_PATH, "w") as f:
            json.dump(cache, f)
        logger.info("✅ Cache saved to file")
    except Exception as e:
        logger.error(f"❌ Failed to write cache to file: {e}")

def load_cache_from_file():
    global cache
    if os.path.exists(CACHE_FILE_PATH):
        try:
            with open(CACHE_FILE_PATH, "r") as f:
                loaded_cache = json.load(f)
                if "last_updated" in loaded_cache:
                    cache = loaded_cache
                    logger.info("Approximate cache size in bytes: %d", sys.getsizeof(cache))
                    logger.info("📁 Cache loaded from file")
        except Exception as e:
            logger.error(f"❌ Failed to load cache from file: {e}")

def update_cache():
    global cache
    driver = None
    try:
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
        event_scraper = EventScraper()
        for event_type, url in links["events"].items():
            try:
                events = event_scraper.scrape_conferences(url,driver)
                cache["events"][event_type] = events
                logger.info(f"Updated {event_type} events")
            except Exception as e:
                logger.error(f"Failed to update {event_type} events: {e}")
        
        opportunities_scraper = OpportunityScraper()
        cache["opportunities"]["iitr"] = opportunities_scraper.scrape_opportunity_iitr(links["opportunities"]['iitr'], driver)
        cache["opportunities"]["iitk"] = opportunities_scraper.scrape_opportunity_iitk(links["opportunities"]['iitk'], driver)
        cache["opportunities"]["iitb"] = opportunities_scraper.scrape_opportunity_iitb(links['opportunities']['iitb'], driver)
        cache["opportunities"]["iisc"] = opportunities_scraper.scrape_opportunity_iisc(links["opportunities"]['iisc'], driver)
        cache["opportunities"]["iitg"] = opportunities_scraper.scrape_opportunity_iitg(links["opportunities"]['iitg'], driver)
        cache["opportunities"]["iitkgp"] = opportunities_scraper.scrape_opportunity_iitkgp(links["opportunities"]['iitkgp'], driver)
        cache["opportunities"]["iitm"] = opportunities_scraper.scrape_opportunity_iitm(links["opportunities"]['iitm'], driver)

        cache["last_updated"] = time.time()
        save_cache_to_file()
        logger.info("Approximate cache size in bytes:", sys.getsizeof(cache))

        logger.info("Cache fully updated")
    except Exception as e:
        logger.error(f"Background scraping failed: {e}")
    finally:
        gc.collect()
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Driver cleanup failed: {str(e)}")

def ensure_cache():
    """Load from file if cache is empty"""
    if cache["last_updated"] == 0:
        logger.info("📦 Empty cache detected, loading from file...")
        load_cache_from_file()
