from flask import Flask, request, g
import time
import logging
import os
import gc
from flask_apscheduler import APScheduler
from .scraper.event_scaper import EventScraper
class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "UTC"

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Middleware for request/response logging
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

# Links configuration
links = {
    "events": {
        # "ai": "https://www.conferencealerts.in/ai",
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

def update_cache():
    """Periodically update cache with fresh data"""
    try:

        event_scraper = EventScraper()

        # Update events
        for event_type, url in links["events"].items():
            try:
                events = event_scraper.scrape_conferences(url)
                cache["events"][event_type] = events
                logger.info(f"Successfully updated {event_type} events")
                del events
            except Exception as e:
                logger.error(f"Failed to update {event_type} events: {str(e)}")
            
        cache["last_updated"] = time.time()
        logger.info("Cache fully updated")
                
    except Exception as e:
        logger.error(f"Background scraping failed: {str(e)}")
    finally:
        gc.collect()


# Initialize APScheduler
scheduler = APScheduler()
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    # Initialize scheduler in main process only
    scheduler.init_app(app)

    # Run initial cache update immediately
    logger.info("Starting initial cache update")
    with app.app_context():
        update_cache()
        
    # Schedule regular updates
    @scheduler.task('interval', id='regular_cache_update', hours=3, misfire_grace_time=900)
    def regular_cache_update():
        with app.app_context():
            update_cache()
    
    scheduler.start()


# Import blueprints after app creation
from app.events.routes import events_bp

# Register blueprints
app.register_blueprint(events_bp)
