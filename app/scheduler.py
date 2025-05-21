#schedular.py

from flask import Flask
from flask_apscheduler import APScheduler
import logging
import os
from app.cache import update_cache, ensure_cache

class Config:
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "Asia/Kolkata"
    
logger = logging.getLogger(__name__)

scheduler = APScheduler()

def init_scheduler(app):
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Initialize scheduler with app
        scheduler.init_app(app)

        #🔄 Schedule ensure_cache every 2 minutes
        @scheduler.task(
            "cron",
            id="ensure_cache_every_2min_limited_hours",
            minute="*/2",  # every minute
            hour="0-3,8-23",  # 00:00 to 03:59 AND 09:00 to 23:59
            timezone="Asia/Kolkata",
            misfire_grace_time=300
        )
        def run_ensure_cache():
            logger.info("⏱️ [Scheduled] Running ensure_cache() every 2 minutes during active hours")
            with app.app_context():
                ensure_cache()


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
