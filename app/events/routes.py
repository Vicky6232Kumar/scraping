# app/events/routes.py
from flask import Blueprint, jsonify
from app.cache import cache


events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events/<event_type>')
def get_events(event_type):
    if event_type in cache["events"]:
        return jsonify({
            "data": cache["events"][event_type],
            "last_updated": cache["last_updated"]
        })
    return jsonify({"error": "Invalid event type"}), 404

@events_bp.route('/api/events/<event_type>/<id>')
def get_events_details(event_type, id):
    if event_type in cache["events"]:
        filtered = [item for item in cache["events"][event_type] if item.get("id") == id]
        return jsonify({
            "data": filtered,
            "last_updated": cache["last_updated"]
        })
    return jsonify({"error": "Invalid event type"}), 404