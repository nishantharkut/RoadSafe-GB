import os
import json
from typing import Dict, Any, List, Optional
from backend.db import get_db

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

DAY_ORDER = [
    "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"
]

class AggregationService:

    @staticmethod
    def build_match_filter(
        year: Optional[int] = None,
        severity: Optional[str] = None,
        weather: Optional[str] = None,
        light: Optional[str] = None,
        road_surface: Optional[str] = None,
        road_type: Optional[str] = None,
        urban_rural: Optional[str] = None,
        has_coords: Optional[bool] = None
    ) -> Dict[str, Any]:
        match = {}
        if year and year != "all":
            try:
                match["collision_year"] = int(year)
            except ValueError:
                pass
        if severity and severity.lower() != "all":
            match["severity"] = severity.capitalize()
        if weather and weather.lower() != "all":
            match["weather_conditions"] = weather
        if light and light.lower() != "all":
            match["light_conditions"] = light
        if road_surface and road_surface.lower() != "all":
            match["road_surface_conditions"] = road_surface
        if road_type and road_type.lower() != "all":
            match["road_type"] = road_type
        if urban_rural and urban_rural.lower() != "all":
            match["urban_rural"] = urban_rural
        if has_coords is not None:
            match["has_valid_coordinates"] = has_coords
        return match

    @staticmethod
    def get_overview(match_filter: Dict[str, Any]) -> Dict[str, Any]:
        db = get_db()
        
        pipeline = [
            {"$match": match_filter},
            {
                "$group": {
                    "_id": None,
                    "total_collisions": {"$sum": 1},
                    "total_casualties": {"$sum": "$number_of_casualties"},
                    "total_vehicles": {"$sum": "$number_of_vehicles"},
                    "fatal_count": {
                        "$sum": {"$cond": [{"$eq": ["$severity", "Fatal"]}, 1, 0]}
                    },
                    "serious_count": {
                        "$sum": {"$cond": [{"$eq": ["$severity", "Serious"]}, 1, 0]}
                    },
                    "slight_count": {
                        "$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}
                    }
                }
            }
        ]
        
        agg_result = list(db.collisions.aggregate(pipeline))
        if not agg_result:
            return {
                "total_collisions": 0,
                "total_casualties": 0,
                "total_vehicles": 0,
                "fatal_count": 0,
                "serious_count": 0,
                "slight_count": 0,
                "serious_fatal_share_pct": 0.0,
                "avg_casualties_per_collision": 0.0,
                "monthly_trend": [],
                "severity_composition": []
            }
            
        res = agg_result[0]
        tot = res["total_collisions"]
        ksi_count = res["fatal_count"] + res["serious_count"]
        ksi_share = round((ksi_count / tot * 100), 2) if tot > 0 else 0.0
        avg_cas = round((res["total_casualties"] / tot), 2) if tot > 0 else 0.0
        
        # Monthly breakdown
        monthly_pipe = [
            {"$match": match_filter},
            {"$match": {"month": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$month",
                    "month_name": {"$first": "$month_name"},
                    "count": {"$sum": 1},
                    "fatal": {"$sum": {"$cond": [{"$eq": ["$severity", "Fatal"]}, 1, 0]}},
                    "serious": {"$sum": {"$cond": [{"$eq": ["$severity", "Serious"]}, 1, 0]}},
                    "slight": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        monthly_raw = list(db.collisions.aggregate(monthly_pipe))
        monthly_dict = {m["_id"]: m for m in monthly_raw}
        
        monthly_trend = []
        for i in range(1, 13):
            item = monthly_dict.get(i, {
                "_id": i,
                "month_name": MONTH_ORDER[i - 1],
                "count": 0,
                "fatal": 0,
                "serious": 0,
                "slight": 0
            })
            monthly_trend.append({
                "month": item.get("month_name") or MONTH_ORDER[i - 1],
                "month_number": i,
                "count": item.get("count", 0),
                "fatal": item.get("fatal", 0),
                "serious": item.get("serious", 0),
                "slight": item.get("slight", 0)
            })
            
        severity_comp = [
            {"name": "Slight", "count": res["slight_count"], "color": "#0D9488"},
            {"name": "Serious", "count": res["serious_count"], "color": "#EA580C"},
            {"name": "Fatal", "count": res["fatal_count"], "color": "#DC2626"}
        ]
        
        return {
            "total_collisions": tot,
            "total_casualties": res["total_casualties"],
            "total_vehicles": res["total_vehicles"],
            "fatal_count": res["fatal_count"],
            "serious_count": res["serious_count"],
            "slight_count": res["slight_count"],
            "serious_fatal_share_pct": ksi_share,
            "avg_casualties_per_collision": avg_cas,
            "monthly_trend": monthly_trend,
            "severity_composition": severity_comp
        }

    @staticmethod
    def get_trends(match_filter: Dict[str, Any]) -> Dict[str, Any]:
        db = get_db()
        
        # 1. Hourly distribution (0 to 23)
        hourly_pipe = [
            {"$match": match_filter},
            {"$match": {"hour": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$hour",
                    "total": {"$sum": 1},
                    "fatal_serious": {"$sum": {"$cond": ["$is_fatal_or_serious", 1, 0]}},
                    "slight": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        hourly_raw = {h["_id"]: h for h in db.collisions.aggregate(hourly_pipe)}
        hourly = []
        for h in range(24):
            rec = hourly_raw.get(h, {"_id": h, "total": 0, "fatal_serious": 0, "slight": 0})
            tot = rec["total"]
            share = round((rec["fatal_serious"] / tot * 100), 1) if tot > 0 else 0.0
            hourly.append({
                "hour": f"{h:02d}:00",
                "hour_number": h,
                "total": tot,
                "fatal_serious": rec["fatal_serious"],
                "slight": rec["slight"],
                "serious_fatal_share_pct": share
            })
            
        # 2. Weekday distribution (Sunday to Saturday)
        weekday_pipe = [
            {"$match": match_filter},
            {"$match": {"day_of_week": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$day_of_week",
                    "day_name": {"$first": "$day_of_week_name"},
                    "total": {"$sum": 1},
                    "fatal_serious": {"$sum": {"$cond": ["$is_fatal_or_serious", 1, 0]}},
                    "slight": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        weekday_raw = {w["_id"]: w for w in db.collisions.aggregate(weekday_pipe)}
        weekday = []
        for d in range(1, 8):
            rec = weekday_raw.get(d, {"_id": d, "day_name": DAY_ORDER[d - 1], "total": 0, "fatal_serious": 0, "slight": 0})
            tot = rec["total"]
            share = round((rec["fatal_serious"] / tot * 100), 1) if tot > 0 else 0.0
            weekday.append({
                "day_number": d,
                "day": rec.get("day_name") or DAY_ORDER[d - 1],
                "total": tot,
                "fatal_serious": rec["fatal_serious"],
                "slight": rec["slight"],
                "serious_fatal_share_pct": share
            })
            
        # 3. Monthly distribution
        monthly_pipe = [
            {"$match": match_filter},
            {"$match": {"month": {"$ne": None}}},
            {
                "$group": {
                    "_id": "$month",
                    "month_name": {"$first": "$month_name"},
                    "total": {"$sum": 1},
                    "fatal_serious": {"$sum": {"$cond": ["$is_fatal_or_serious", 1, 0]}},
                    "slight": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        monthly_raw = {m["_id"]: m for m in db.collisions.aggregate(monthly_pipe)}
        monthly = []
        for m in range(1, 13):
            rec = monthly_raw.get(m, {"_id": m, "month_name": MONTH_ORDER[m - 1], "total": 0, "fatal_serious": 0, "slight": 0})
            tot = rec["total"]
            share = round((rec["fatal_serious"] / tot * 100), 1) if tot > 0 else 0.0
            monthly.append({
                "month_number": m,
                "month": rec.get("month_name") or MONTH_ORDER[m - 1],
                "total": tot,
                "fatal_serious": rec["fatal_serious"],
                "slight": rec["slight"],
                "serious_fatal_share_pct": share
            })
            
        return {
            "hourly": hourly,
            "weekday": weekday,
            "monthly": monthly
        }

    @staticmethod
    def get_hotspots(
        match_filter: Dict[str, Any],
        min_count: int = 15,
        limit: int = 400
    ) -> List[Dict[str, Any]]:
        db = get_db()
        
        # Spatial grid grouping (grid_cell is lat_lon rounded to 0.1 deg ~11km)
        spatial_filter = dict(match_filter)
        spatial_filter["has_valid_coordinates"] = True
        spatial_filter["grid_cell"] = {"$ne": None}
        
        pipeline = [
            {"$match": spatial_filter},
            {
                "$group": {
                    "_id": "$grid_cell",
                    "count": {"$sum": 1},
                    "fatal_count": {"$sum": {"$cond": [{"$eq": ["$severity", "Fatal"]}, 1, 0]}},
                    "serious_count": {"$sum": {"$cond": [{"$eq": ["$severity", "Serious"]}, 1, 0]}},
                    "slight_count": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}},
                    "total_casualties": {"$sum": "$number_of_casualties"},
                    "avg_lat": {"$avg": "$latitude"},
                    "avg_lon": {"$avg": "$longitude"}
                }
            },
            {"$match": {"count": {"$gte": min_count}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        results = list(db.collisions.aggregate(pipeline))
        hotspots = []
        for r in results:
            tot = r["count"]
            ksi = r["fatal_count"] + r["serious_count"]
            share = round((ksi / tot * 100), 1) if tot > 0 else 0.0
            hotspots.append({
                "grid_id": r["_id"],
                "count": tot,
                "fatal_count": r["fatal_count"],
                "serious_count": r["serious_count"],
                "slight_count": r["slight_count"],
                "total_casualties": r["total_casualties"],
                "serious_fatal_share_pct": share,
                "latitude": round(r["avg_lat"], 5),
                "longitude": round(r["avg_lon"], 5)
            })
        return hotspots

    @staticmethod
    def get_severity_analysis(match_filter: Dict[str, Any], field: str) -> List[Dict[str, Any]]:
        db = get_db()
        allowed_fields = [
            "weather_conditions",
            "light_conditions",
            "road_surface_conditions",
            "road_type",
            "speed_limit",
            "urban_rural"
        ]
        if field not in allowed_fields:
            field = "weather_conditions"
            
        pipeline = [
            {"$match": match_filter},
            {"$match": {field: {"$ne": None, "$ne": ""}}},
            {
                "$group": {
                    "_id": f"${field}",
                    "total": {"$sum": 1},
                    "fatal": {"$sum": {"$cond": [{"$eq": ["$severity", "Fatal"]}, 1, 0]}},
                    "serious": {"$sum": {"$cond": [{"$eq": ["$severity", "Serious"]}, 1, 0]}},
                    "slight": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}}
                }
            },
            {"$sort": {"total": -1}}
        ]
        
        raw = list(db.collisions.aggregate(pipeline))
        results = []
        for item in raw:
            tot = item["total"]
            ksi = item["fatal"] + item["serious"]
            share = round((ksi / tot * 100), 2) if tot > 0 else 0.0
            name_val = str(item["_id"])
            if field == "speed_limit":
                name_val = f"{name_val} mph"
            results.append({
                "category": name_val,
                "total": tot,
                "fatal": item["fatal"],
                "serious": item["serious"],
                "slight": item["slight"],
                "serious_fatal_share_pct": share
            })
        return results

    @staticmethod
    def get_records(
        match_filter: Dict[str, Any],
        page: int = 1,
        page_size: int = 25,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        db = get_db()
        query = dict(match_filter)
        
        if search and search.strip():
            term = search.strip()
            query["$or"] = [
                {"collision_index": {"$regex": term, "$options": "i"}},
                {"collision_ref_no": {"$regex": term, "$options": "i"}},
                {"first_road_number": {"$regex": term, "$options": "i"}}
            ]
            
        total_count = db.collisions.count_documents(query)
        page = max(1, page)
        page_size = min(max(10, page_size), 100)
        skip = (page - 1) * page_size
        
        cursor = db.collisions.find(
            query,
            {
                "_id": 0,
                "collision_index": 1,
                "collision_year": 1,
                "collision_ref_no": 1,
                "date": 1,
                "time": 1,
                "severity": 1,
                "number_of_vehicles": 1,
                "number_of_casualties": 1,
                "speed_limit": 1,
                "road_type": 1,
                "weather_conditions": 1,
                "light_conditions": 1,
                "road_surface_conditions": 1,
                "urban_rural": 1,
                "first_road_number": 1,
                "latitude": 1,
                "longitude": 1
            }
        ).sort("date", -1).skip(skip).limit(page_size)
        
        records = list(cursor)
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
        
        return {
            "records": records,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }

    @staticmethod
    def get_collision_detail(collision_index: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        coll = db.collisions.find_one({"collision_index": collision_index}, {"_id": 0})
        if not coll:
            return None
            
        # Multi-collection joins (aggregate children to avoid multiplication)
        vehicles = list(db.vehicles.find({"collision_index": collision_index}, {"_id": 0}))
        casualties = list(db.casualties.find({"collision_index": collision_index}, {"_id": 0}))
        
        coll["vehicles"] = vehicles
        coll["casualties"] = casualties
        return coll

    @staticmethod
    def get_data_quality() -> Dict[str, Any]:
        db = get_db()
        tot_c = db.collisions.count_documents({})
        c24 = db.collisions.count_documents({"collision_year": 2024})
        c25 = db.collisions.count_documents({"collision_year": 2025})
        tot_v = db.vehicles.count_documents({})
        tot_cas = db.casualties.count_documents({})
        valid_coords = db.collisions.count_documents({"has_valid_coordinates": True})
        invalid_coords = tot_c - valid_coords
        
        missing_times = db.collisions.count_documents({"time": None})
        missing_speeds = db.collisions.count_documents({"speed_limit": None})
        
        return {
            "total_collisions": tot_c,
            "collisions_2024": c24,
            "collisions_2025": c25,
            "total_vehicles": tot_v,
            "total_casualties": tot_cas,
            "valid_coordinates": valid_coords,
            "invalid_coordinates": invalid_coords,
            "coordinate_completeness_pct": round((valid_coords / tot_c * 100), 2) if tot_c > 0 else 0.0,
            "missing_time_count": missing_times,
            "missing_speed_limit_count": missing_speeds,
            "database_name": "roadsafe",
            "publisher": "UK Department for Transport (DfT)",
            "licence": "UK Open Government Licence (OGL v3.0)",
            "indexes": {
                "collisions": list(db.collisions.index_information().keys()),
                "vehicles": list(db.vehicles.index_information().keys()),
                "casualties": list(db.casualties.index_information().keys())
            }
        }

    @staticmethod
    def get_index_benchmarks() -> Dict[str, Any]:
        """Member 1: Returns cached execution plan benchmark report"""
        json_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "metadata", "index_benchmarks.json"
        )
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"error": "Benchmark report not generated. Run etl/benchmark_indexes.py first."}

    @staticmethod
    def get_combinatorial_risk(match_filter: Dict[str, Any], min_count: int = 20) -> List[Dict[str, Any]]:
        """
        Member 2: Combinatorial Pattern Mining across co-occurring environmental risk factors
        Calculates Severe Share % and Relative Risk Odds Ratio against national baseline
        """
        db = get_db()
        
        # Calculate baseline severe share for current match_filter
        tot_all = db.collisions.count_documents(match_filter)
        if tot_all == 0:
            return []
            
        severe_all_filter = dict(match_filter)
        severe_all_filter["is_fatal_or_serious"] = 1
        sev_all = db.collisions.count_documents(severe_all_filter)
        baseline_severe_pct = (sev_all / tot_all * 100) if tot_all > 0 else 25.54

        pipeline = [
            {"$match": match_filter},
            {"$match": {
                "speed_limit": {"$ne": None},
                "light_conditions": {"$ne": None, "$ne": "Data missing or out of range"},
                "weather_conditions": {"$ne": None, "$ne": "Data missing or out of range"},
                "urban_rural": {"$ne": None, "$ne": "Unallocated"}
            }},
            {
                "$group": {
                    "_id": {
                        "speed_limit": "$speed_limit",
                        "light_conditions": "$light_conditions",
                        "weather_conditions": "$weather_conditions",
                        "urban_rural": "$urban_rural"
                    },
                    "total": {"$sum": 1},
                    "fatal": {"$sum": {"$cond": [{"$eq": ["$severity", "Fatal"]}, 1, 0]}},
                    "serious": {"$sum": {"$cond": [{"$eq": ["$severity", "Serious"]}, 1, 0]}},
                    "slight": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}},
                    "total_casualties": {"$sum": "$number_of_casualties"}
                }
            },
            {"$match": {"total": {"$gte": min_count}}},
            {"$sort": {"total": -1}},
            {"$limit": 50}
        ]

        raw = list(db.collisions.aggregate(pipeline))
        combinations = []
        for r in raw:
            tot = r["total"]
            fatal_serious = r["fatal"] + r["serious"]
            share = round((fatal_serious / tot * 100), 2) if tot > 0 else 0.0
            avg_cas = round((r["total_casualties"] / tot), 2) if tot > 0 else 0.0
            
            # Relative Risk multiplier compared to baseline
            rr = round(share / baseline_severe_pct, 2) if baseline_severe_pct > 0 else 1.0
            
            # Odds Ratio = (Sev / Slight) / (Baseline_Sev / Baseline_Slight)
            odds_comb = (fatal_serious / max(r["slight"], 1))
            odds_base = (sev_all / max(tot_all - sev_all, 1))
            odds_ratio = round(odds_comb / odds_base, 2) if odds_base > 0 else 1.0

            combinations.append({
                "speed_limit": f"{r['_id']['speed_limit']} mph",
                "speed_raw": r["_id"]["speed_limit"],
                "light_conditions": r["_id"]["light_conditions"],
                "weather_conditions": r["_id"]["weather_conditions"],
                "urban_rural": r["_id"]["urban_rural"],
                "total_collisions": tot,
                "fatal_count": r["fatal"],
                "serious_count": r["serious"],
                "slight_count": r["slight"],
                "serious_fatal_share_pct": share,
                "avg_casualties_per_collision": avg_cas,
                "relative_risk": rr,
                "odds_ratio": odds_ratio,
                "risk_tier": "Critical Risk" if rr >= 1.5 else ("Elevated Risk" if rr >= 1.15 else "Baseline / Lower Risk")
            })

        # Sort by severe share % descending
        combinations.sort(key=lambda x: x["serious_fatal_share_pct"], reverse=True)
        return combinations

    @staticmethod
    def compare_risk_scenarios(scenario_a: Dict[str, Any], scenario_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Member 3: Side-by-Side Risk Scenario Evaluation
        Calculates and compares risk metrics between Scenario A and Scenario B
        """
        db = get_db()

        def evaluate_scenario(params: Dict[str, Any]) -> Dict[str, Any]:
            query: Dict[str, Any] = {}
            if params.get("speed_limit"):
                query["speed_limit"] = int(params["speed_limit"])
            if params.get("light_conditions"):
                query["light_conditions"] = params["light_conditions"]
            if params.get("weather_conditions"):
                query["weather_conditions"] = params["weather_conditions"]
            if params.get("urban_rural"):
                query["urban_rural"] = params["urban_rural"]
            if params.get("road_surface_conditions"):
                query["road_surface_conditions"] = params["road_surface_conditions"]

            tot = db.collisions.count_documents(query)
            fatal = db.collisions.count_documents({**query, "severity": "Fatal"})
            serious = db.collisions.count_documents({**query, "severity": "Serious"})
            slight = db.collisions.count_documents({**query, "severity": "Slight"})
            
            # Aggregate casualties
            cas_pipeline = [
                {"$match": query},
                {"$group": {"_id": None, "tot_cas": {"$sum": "$number_of_casualties"}}}
            ]
            cas_res = list(db.collisions.aggregate(cas_pipeline))
            tot_cas = cas_res[0]["tot_cas"] if cas_res else 0

            ksi = fatal + serious
            share = round((ksi / tot * 100), 2) if tot > 0 else 0.0
            avg_cas = round((tot_cas / tot), 2) if tot > 0 else 0.0

            return {
                "parameters": params,
                "total_collisions": tot,
                "fatal_count": fatal,
                "serious_count": serious,
                "slight_count": slight,
                "serious_fatal_share_pct": share,
                "total_casualties": tot_cas,
                "avg_casualties_per_collision": avg_cas
            }

        res_a = evaluate_scenario(scenario_a)
        res_b = evaluate_scenario(scenario_b)

        share_a = res_a["serious_fatal_share_pct"]
        share_b = res_b["serious_fatal_share_pct"]

        relative_risk_diff = round(share_b - share_a, 2)
        relative_risk_multiplier = round(share_b / max(share_a, 0.01), 2)

        return {
            "scenario_a": res_a,
            "scenario_b": res_b,
            "comparison": {
                "severe_share_diff_pct": relative_risk_diff,
                "risk_multiplier": relative_risk_multiplier,
                "higher_risk_scenario": "Scenario B" if share_b > share_a else ("Scenario A" if share_a > share_b else "Equal Risk")
            }
        }
