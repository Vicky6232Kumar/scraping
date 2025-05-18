# app/events/routes.py

from flask import Blueprint, jsonify
from app.cache import cache

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events/<event_type>')
def get_events(event_type):
    try:
        if event_type not in cache["events"]:
            return jsonify({"error": f"Event type '{event_type}' not found."}), 404

        return jsonify({
            "data": cache["events"][event_type],
            "last_updated": cache.get("last_updated")
        })
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@events_bp.route('/api/events/<event_type>/<id>')
def get_events_details(event_type, id):
    try:
        if event_type not in cache["events"]:
            return jsonify({"error": f"Event type '{event_type}' not found."}), 404

        event_data = cache["events"][event_type]

        conferences = event_data.get("conferences", [])
        if not isinstance(conferences, list):
            return jsonify({"error": "Invalid data format for 'conferences'."}), 500

        filtered = [conf for conf in conferences if conf.get("id") == id]

        if not filtered:
            return jsonify({"error": f"No conference found with ID '{id}'."}), 404

        return jsonify({
            "data": filtered,
            "last_updated": cache.get("last_updated")
        })
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500