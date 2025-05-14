from flask import Flask
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from .scraper.event_scraper import EventScraper
from .scraper.opportunity_scraper import OpportunityScraper
import threading
import time
import logging
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = "/usr/bin/google-chrome"  # Verify with 'which google-chrome'
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")

# Initialize cache
cache = {
    "events": [],
    "opportunities": [],
    "last_updated": 0
}

def get_chrome_driver():
    """Initialize Chrome driver with proper error handling"""
    try:
        service = Service(
            executable_path=ChromeDriverManager().install(),
            log_path=os.devnull  # Disable verbose logging
        )
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        logger.error(f"Driver initialization failed: {str(e)}")
        raise

def background_scraper():
    """Periodically update cache with fresh data"""
    while True:
        try:
            with get_chrome_driver() as driver:
                # Scrape events
                event_scraper = EventScraper(driver)
                events = event_scraper.scrape_events(app.config['EVENTS_URL'])
                
                # Scrape opportunities
                opp_scraper = OpportunityScraper()
                opportunities = opp_scraper.scrape_opportunities(app.config['OPPORTUNITIES_URL'])
                
                cache.update({
                    "events": events,
                    "opportunities": opportunities,
                    "last_updated": time.time()
                })
                logger.info("Cache updated successfully")
                
        except Exception as e:
            logger.error(f"Background scraping failed: {str(e)}")
        
        time.sleep(3600)  # Update hourly

# Start background thread
threading.Thread(target=background_scraper, daemon=True).start()

# Import blueprints after app creation
from app.events.routes import events_bp
from app.opportunities.routes import opportunities_bp

# Register blueprints
app.register_blueprint(events_bp)
app.register_blueprint(opportunities_bp)
