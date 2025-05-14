# app/events/routes.py
from flask import Blueprint, jsonify
from app import cache

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events')
def get_events():
    return jsonify({
        "data": cache["events"],
        "last_updated": cache["last_updated"]
    })
