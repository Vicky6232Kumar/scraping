#schedular.py

from flask import Flask
from flask_apscheduler import APScheduler
import logging
import os
from app.cache import update_cache

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Asia/Kolkata"
    
logger = logging.getLogger(__name__)

scheduler = APScheduler()

def init_scheduler(app):
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Initialize scheduler with app
        scheduler.init_app(app)
        
        # Schedule daily job at 4 AM IST
        @scheduler.task(
            "cron", 
            id="daily_cache_update", 
            hour=4, 
            minute=0, 
            timezone="Asia/Kolkata",  # Explicit timezone
            misfire_grace_time=3600   # Allow 1-hour grace period
        )
        def daily_cache_update():
            logger.info("🔄 [Production] Running scheduled cache update at 4 AM IST")
            with app.app_context():
                update_cache()
        
        # Initial cache update on server start
        # logger.info("🚀 [Production] Starting initial cache update")
        # with app.app_context():
        #     update_cache()
        
        # Start scheduler
        scheduler.start()
        logger.info("⏰ [Production] Scheduler started")
