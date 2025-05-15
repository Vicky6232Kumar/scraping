# app/events/routes.py
from flask import Blueprint, jsonify
from app import cache


events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events/<event_type>')
def get_events(event_type):
    if event_type in cache["events"]:
        return jsonify({
            "data": cache["events"][event_type],
            "last_updated": cache["last_updated"]
        })
    return jsonify({"error": "Invalid event type"}), 404