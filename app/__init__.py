from flask import Flask, request, g
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from .scraper.event_scraper import EventScraper
# from .scraper.opportunity_scraper import OpportunityScraper
import time
import logging
from flask_apscheduler import APScheduler

class Config:
    SCHEDULER_API_ENABLED = True

# Initialize Flask app
app = Flask(__name__)
app.config.from_object('config.Config')

@app.before_request
def log_request_info():
    g.start_time = time.time()
    app.logger.info(f"Request: {request.remote_addr} {request.method} {request.path}")

@app.after_request
def log_response_info(response):
    duration = time.time() - g.start_time if hasattr(g, 'start_time') else -1
    app.logger.info(
        f"Response: {request.remote_addr} {request.method} {request.path} "
        f"Status: {response.status_code} Duration: {duration:.3f}s"
    )
    return response


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Links configuration
links = {
    "events": {
        "ai": "https://www.conferencealerts.in/ai",
        "india": "https://www.conferencealerts.in/india"
    },
    "opportunities": {
        "iitr": "https://iitr.ac.in/Careers/Project%20Jobs.html",
        "iitkgp": "https://www.iitk.ac.in/dord/scientific-and-research-staff"
    }
}

# Initialize cache structure
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

def get_chrome_driver():
    """Initialize Chrome driver with proper error handling"""
    try:
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service('/usr/local/bin/chromedriver')
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        logger.error(f"Driver initialization failed: {str(e)}")
        raise

def update_cache():
    """Periodically update cache with fresh data"""
    driver = None
    try:
        driver = get_chrome_driver()

        event_scraper = EventScraper(driver)
        # opportunity_scraper = OpportunityScraper()

        # Update events
        for event_type, url in links["events"].items():
            try:
                events = event_scraper.scrape_conferences(url, driver)
                cache["events"][event_type] = events
                logger.info(f"Successfully updated {event_type} events")
            except Exception as e:
                logger.error(f"Failed to update {event_type} events: {str(e)}")

        # Update opportunities
        # for opp_type, url in links["opportunities"].items():
        #     try:
        #         opportunities = opportunity_scraper.scrape_opportunities(url, driver)
        #         cache["opportunities"][opp_type] = opportunities
        #         logger.info(f"Successfully updated {opp_type} opportunities")
        #     except Exception as e:
        #         logger.error(f"Failed to update {opp_type} opportunities: {str(e)}")
            
        cache["last_updated"] = time.time()
        logger.info("Cache fully updated")
                
    except Exception as e:
        logger.error(f"Background scraping failed: {str(e)}")
    finally:
        if driver:
            driver.quit()


# Initialize APScheduler
scheduler = APScheduler()
scheduler.init_app(app)

# Schedule the job to run every 3 hours
@scheduler.task('interval', id='update_cache_job', hours=3, misfire_grace_time=900)
def scheduled_cache_update():
    with scheduler.app.app_context():
        update_cache()

scheduler.start()

# Immediate initial update
with app.app_context():
    update_cache()

# Import blueprints after app creation
from app.events.routes import events_bp

# from app.opportunities.routes import opportunities_bp
# from app.opportunities.routes import opportunities_bp

# Register blueprints
app.register_blueprint(events_bp)
# app.register_blueprint(opportunities_bp)
