from flask import Blueprint, request, jsonify
from backend.services.aggregation_service import AggregationService

collisions_bp = Blueprint("collisions", __name__)

@collisions_bp.route("/api/collisions", methods=["GET"])
def list_collisions():
    year = request.args.get("year", "2025")
    severity = request.args.get("severity")
    weather = request.args.get("weather")
    urban_rural = request.args.get("urban_rural")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 25))
    search = request.args.get("search")
    
    match_filter = AggregationService.build_match_filter(
        year=year,
        severity=severity,
        weather=weather,
        urban_rural=urban_rural
    )
    
    result = AggregationService.get_records(
        match_filter=match_filter,
        page=page,
        page_size=page_size,
        search=search
    )
    return jsonify(result), 200

@collisions_bp.route("/api/collisions/<string:collision_index>", methods=["GET"])
def get_collision_detail(collision_index: str):
    record = AggregationService.get_collision_detail(collision_index)
    if not record:
        return jsonify({"error": "Collision record not found", "collision_index": collision_index}), 404
    return jsonify(record), 200
