# app/cache.py

import time
import gc
import logging
from app.scraper.event_scaper import EventScraper

logger = logging.getLogger(__name__)

# Links configuration
links = {
    "events": {
        "india": "https://www.conferencealerts.in/india",
        "ai": "https://www.conferencealerts.in/ai"
    },
    "opportunities": {
        "iitr": "https://iitr.ac.in/Careers/Project%20Jobs.html",
        "iitkgp": "https://www.iitk.ac.in/dord/scientific-and-research-staff"
    }
}

# Cache store
cache = {
    "events": {
        "ai": [],
        "india": []
    },
    "opportunities": {
        "iitr": [],
        "iitkgp": []
    },
    "last_updated": 0
}

def update_cache():
    try:
        event_scraper = EventScraper()
        for event_type, url in links["events"].items():
            try:
                events = event_scraper.scrape_conferences(url)
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
