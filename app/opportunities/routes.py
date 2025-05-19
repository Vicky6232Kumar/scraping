# app/opportunities/routes.py
from flask import Blueprint, jsonify
from app.cache import cache

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('/api/opportunities/<opp_type>')
def get_opportunities(opp_type):
    try:
        if opp_type not in cache["opportunities"]:
            return jsonify({"error": f"Opportunity type '{opp_type}' not found."}), 404
        return jsonify({
            "data": cache["opportunities"][opp_type],
            "last_updated": cache["last_updated"]
        })
    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500