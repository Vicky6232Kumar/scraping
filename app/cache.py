# app/cache.py

import time
import gc
import logging
from app.scraper.event_scaper import EventScraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger(__name__)

# Links configuration
links = {
    "events": {
        "india": "https://www.conferencealerts.in/india",
        "ai": "https://www.conferencealerts.in/ai",
        "computer-science": "https://www.conferencealerts.in/computer-science",
        "cybersecurity": "https://www.conferencealerts.in/cybersecurity",
        "iot": "https://www.conferencealerts.in/iot",
        "natural-language-processing": "https://www.conferencealerts.in/natural-language-processing",
        "robotics": "https://www.conferencealerts.in/robotics",
        "software-engineering": "https://www.conferencealerts.in/software-engineering",
        "bioinformatics": "https://www.conferencealerts.in/bioinformatics",
        "biomedical-engineering": "https://www.conferencealerts.in/biomedical-engineering",
        "biotechnology": "https://www.conferencealerts.in/biotechnology",
        "nanotechnology": "https://www.conferencealerts.in/nanotechnology",
        "material-science": "https://www.conferencealerts.in/material-science",
        "civil-engineering": "https://www.conferencealerts.in/civil-engineering",
        "design": "https://www.conferencealerts.in/design",
        "industrial-engineering": "https://www.conferencealerts.in/industrial-engineering",
        "manufacturing": "https://www.conferencealerts.in/manufacturing",
        "mining": "https://www.conferencealerts.in/mining",
        "structural-engineering": "https://www.conferencealerts.in/structural-engineering",
        "marine-engineering": "https://www.conferencealerts.in/marine-engineering",
        "aeronautical": "https://www.conferencealerts.in/aeronautical",
        "electronics": "https://www.conferencealerts.in/electronics",
        "electrical": "https://www.conferencealerts.in/electrical",
        "engineering": "https://www.conferencealerts.in/engineering"
    },
    "opportunities": {
        "iitr": "https://iitr.ac.in/Careers/Project%20Jobs.html",
        "iitkgp": "https://www.iitk.ac.in/dord/scientific-and-research-staff",
    }
}

# Cache store
cache = {
    "events": {key: [] for key in links["events"]},
    # "opportunities": {key: [] for key in links["opportunities"]},
    "last_updated": 0
}

def get_chrome_options():

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36")
    return options

def update_cache():
    driver = None
    try:
        service = Service('/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
        event_scraper = EventScraper()
        for event_type, url in links["events"].items():
            try:
                events = event_scraper.scrape_conferences(url,driver)
                cache["events"][event_type] = events
                logger.info(f"Updated {event_type} events")
            except Exception as e:
                logger.error(f"Failed to update {event_type} events: {e}")
        cache["last_updated"] = time.time()
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
