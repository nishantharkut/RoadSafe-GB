from flask import Blueprint, request, jsonify
from backend.services.aggregation_service import AggregationService

trends_bp = Blueprint("trends", __name__)

@trends_bp.route("/api/trends", methods=["GET"])
def get_trends():
    year = request.args.get("year", "2025")
    severity = request.args.get("severity")
    weather = request.args.get("weather")
    urban_rural = request.args.get("urban_rural")
    
    match_filter = AggregationService.build_match_filter(
        year=year,
        severity=severity,
        weather=weather,
        urban_rural=urban_rural
    )
    
    data = AggregationService.get_trends(match_filter)
    data["filters_applied"] = {
        "year": year,
        "severity": severity or "all"
    }
    return jsonify(data), 200
