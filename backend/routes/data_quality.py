from flask import Blueprint, jsonify
from backend.services.aggregation_service import AggregationService

data_quality_bp = Blueprint("data_quality", __name__)

@data_quality_bp.route("/api/data-quality", methods=["GET"])
def get_data_quality():
    report = AggregationService.get_data_quality()
    return jsonify(report), 200

@data_quality_bp.route("/api/data-quality/benchmarks", methods=["GET"])
def get_benchmarks():
    """Member 1: Index Performance Benchmark Report"""
    benchmarks = AggregationService.get_index_benchmarks()
    return jsonify(benchmarks), 200
