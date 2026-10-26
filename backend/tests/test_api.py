import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "HEALTHY"
    assert data["database_connected"] is True
    assert data["collections"]["collisions"] > 200000

def test_overview_endpoint(client):
    res = client.get("/api/overview?year=2025")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_collisions"] > 100000
    assert "fatal_count" in data
    assert "serious_count" in data
    assert "slight_count" in data
    assert "serious_fatal_share_pct" in data
    assert len(data["monthly_trend"]) == 12

def test_trends_endpoint(client):
    res = client.get("/api/trends?year=2025")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["hourly"]) == 24
    assert len(data["weekday"]) == 7
    assert len(data["monthly"]) == 12

def test_hotspots_endpoint(client):
    res = client.get("/api/hotspots?year=2025&min_count=20")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_hotspots"] > 0
    first = data["hotspots"][0]
    assert "latitude" in first
    assert "longitude" in first
    assert first["count"] >= 20

def test_severity_analysis_endpoint(client):
    res = client.get("/api/severity-analysis?year=2025&field=weather_conditions")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["categories"]) > 0
    first = data["categories"][0]
    assert "category" in first
    assert "total" in first
    assert "serious_fatal_share_pct" in first

def test_collisions_records_and_detail(client):
    # 1. Test records list
    res = client.get("/api/collisions?year=2025&page=1&page_size=10")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["records"]) == 10
    assert data["total_count"] > 100000
    
    # 2. Test detail for the first record
    first_id = data["records"][0]["collision_index"]
    detail_res = client.get(f"/api/collisions/{first_id}")
    assert detail_res.status_code == 200
    detail = detail_res.get_json()
    assert detail["collision_index"] == first_id
    assert "vehicles" in detail
    assert "casualties" in detail

def test_data_quality_endpoint(client):
    res = client.get("/api/data-quality")
    assert res.status_code == 200
    data = res.get_json()
    assert data["total_collisions"] > 200000
    assert data["coordinate_completeness_pct"] > 99.0

def test_index_benchmarks_endpoint(client):
    res = client.get("/api/data-quality/benchmarks")
    assert res.status_code == 200
    data = res.get_json()
    assert "benchmarks" in data
    assert len(data["benchmarks"]) >= 3
    # Check that compound index speedup exists
    compound = next((b for b in data["benchmarks"] if b["benchmark_id"] == "COMPOUND_YEAR_SEVERITY"), None)
    assert compound is not None
    assert compound["speedup_factor"] > 1.0

def test_severity_combinations_endpoint(client):
    res = client.get("/api/severity/combinations?year=2025&min_count=20")
    assert res.status_code == 200
    data = res.get_json()
    assert "combinations" in data
    assert len(data["combinations"]) > 0
    first = data["combinations"][0]
    assert "speed_limit" in first
    assert "relative_risk" in first
    assert "odds_ratio" in first
    assert "risk_tier" in first

def test_scenario_compare_endpoint(client):
    payload = {
        "scenario_a": {
            "speed_limit": 30,
            "light_conditions": "Daylight",
            "weather_conditions": "Fine no high winds",
            "urban_rural": "Urban"
        },
        "scenario_b": {
            "speed_limit": 60,
            "light_conditions": "Darkness - no lighting",
            "weather_conditions": "Raining no high winds",
            "urban_rural": "Rural"
        }
    }
    res = client.post("/api/severity/compare", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "scenario_a" in data
    assert "scenario_b" in data
    assert "comparison" in data
    assert "risk_multiplier" in data["comparison"]
    assert data["scenario_b"]["serious_fatal_share_pct"] > data["scenario_a"]["serious_fatal_share_pct"]
