from flask import Blueprint, request, jsonify
from backend.services.aggregation_service import AggregationService

severity_bp = Blueprint("severity", __name__)

@severity_bp.route("/api/severity-analysis", methods=["GET"])
def get_severity_analysis():
    year = request.args.get("year", "2025")
    field = request.args.get("field", "weather_conditions")
    
    match_filter = AggregationService.build_match_filter(year=year)
    results = AggregationService.get_severity_analysis(match_filter, field=field)
    
    return jsonify({
        "field": field,
        "year": year,
        "categories": results
    }), 200

@severity_bp.route("/api/severity/combinations", methods=["GET"])
def get_severity_combinations():
    """Member 2: Combinatorial Risk & Odds Ratio Pattern Mining"""
    year = request.args.get("year", "2025")
    min_count = int(request.args.get("min_count", 25))
    
    match_filter = AggregationService.build_match_filter(year=year)
    combinations = AggregationService.get_combinatorial_risk(match_filter, min_count=min_count)
    
    return jsonify({
        "year": year,
        "total_combinations_mined": len(combinations),
        "combinations": combinations
    }), 200

@severity_bp.route("/api/severity/compare", methods=["POST"])
def compare_scenarios():
    """Member 3: Side-by-Side Risk Scenario Evaluation"""
    data = request.get_json() or {}
    scenario_a = data.get("scenario_a", {
        "speed_limit": 30,
        "light_conditions": "Daylight",
        "weather_conditions": "Fine no high winds",
        "urban_rural": "Urban"
    })
    scenario_b = data.get("scenario_b", {
        "speed_limit": 60,
        "light_conditions": "Darkness - no lighting",
        "weather_conditions": "Raining no high winds",
        "urban_rural": "Rural"
    })
    
    result = AggregationService.compare_risk_scenarios(scenario_a, scenario_b)
    return jsonify(result), 200
