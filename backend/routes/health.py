from flask import Blueprint, jsonify
from backend.db import check_connection, get_db

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health_check():
    connected, message = check_connection()
    if not connected:
        return jsonify({
            "status": "ERROR",
            "database_connected": False,
            "message": message
        }), 503
        
    db = get_db()
    c_count = db.collisions.count_documents({})
    v_count = db.vehicles.count_documents({})
    cas_count = db.casualties.count_documents({})
    
    return jsonify({
        "status": "HEALTHY",
        "database_connected": True,
        "database": db.name,
        "collections": {
            "collisions": c_count,
            "vehicles": v_count,
            "casualties": cas_count
        }
    }), 200
