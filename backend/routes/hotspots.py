from flask import Blueprint, request, jsonify
from backend.services.aggregation_service import AggregationService

hotspots_bp = Blueprint("hotspots", __name__)

@hotspots_bp.route("/api/hotspots", methods=["GET"])
def get_hotspots():
    year = request.args.get("year", "2025")
    severity = request.args.get("severity")
    min_count = int(request.args.get("min_count", 15))
    limit = int(request.args.get("limit", 400))
    
    match_filter = AggregationService.build_match_filter(
        year=year,
        severity=severity
    )
    
    hotspots = AggregationService.get_hotspots(
        match_filter=match_filter,
        min_count=min_count,
        limit=limit
    )
    
    return jsonify({
        "total_hotspots": len(hotspots),
        "min_count_threshold": min_count,
        "year": year,
        "severity": severity or "all",
        "hotspots": hotspots
    }), 200
