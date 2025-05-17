#app/__init__.py 

from flask import Flask, request, g
import time
import logging
from .scheduler import init_scheduler 

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Register blueprints
from app.events.routes import events_bp
app.register_blueprint(events_bp)

init_scheduler(app)
