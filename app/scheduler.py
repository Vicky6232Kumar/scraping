#schedular.py

from flask import Flask
from flask_apscheduler import APScheduler
import logging
from app.cache import update_cache

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "UTC"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()

@scheduler.task('interval', id='regular_cache_update', hours=3, misfire_grace_time=900)
def scheduled_job():
    with app.app_context():
        update_cache()

def init_scheduler(app):
    logger.info("Running initial cache update")
    with app.app_context():
        update_cache()

    scheduler.start()
    logger.info("Scheduler started")
