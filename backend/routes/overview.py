from flask import Blueprint, request, jsonify
from backend.services.aggregation_service import AggregationService

overview_bp = Blueprint("overview", __name__)

@overview_bp.route("/api/overview", methods=["GET"])
def get_overview():
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
    
    data = AggregationService.get_overview(match_filter)
    data["filters_applied"] = {
        "year": year,
        "severity": severity or "all",
        "weather": weather or "all",
        "urban_rural": urban_rural or "all"
    }
    return jsonify(data), 200
