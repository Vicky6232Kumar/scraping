# app/opportunities/routes.py
from flask import Blueprint, jsonify
from app import cache

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('/api/opportunities')
def get_opportunities():
    return jsonify({
        "data": cache["opportunities"],
        "last_updated": cache["last_updated"]
    })
