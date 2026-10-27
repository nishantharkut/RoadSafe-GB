import os
import csv
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "roadsafe"

EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "powerbi", "exports")

def export_fact_collisions(db) -> int:
    print("\nExporting 'fact_collisions.csv'...")
    target_path = os.path.join(EXPORTS_DIR, "fact_collisions.csv")
    
    fields = [
        "collision_index",
        "collision_year",
        "date",
        "time",
        "hour",
        "day_of_week",
        "day_of_week_name",
        "month",
        "month_name",
        "severity",
        "collision_severity",
        "is_fatal_or_serious",
        "number_of_vehicles",
        "number_of_casualties",
        "speed_limit",
        "weather_conditions",
        "light_conditions",
        "road_surface_conditions",
        "road_type",
        "urban_rural",
        "latitude",
        "longitude",
        "grid_cell"
    ]
    
    count = 0
    with open(target_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        cursor = db.collisions.find(
            {},
            {
                "_id": 0,
                "collision_index": 1,
                "collision_year": 1,
                "date": 1,
                "time": 1,
                "hour": 1,
                "day_of_week": 1,
                "day_of_week_name": 1,
                "month": 1,
                "month_name": 1,
                "severity": 1,
                "collision_severity": 1,
                "is_fatal_or_serious": 1,
                "number_of_vehicles": 1,
                "number_of_casualties": 1,
                "speed_limit": 1,
                "weather_conditions": 1,
                "light_conditions": 1,
                "road_surface_conditions": 1,
                "road_type": 1,
                "urban_rural": 1,
                "latitude": 1,
                "longitude": 1,
                "grid_cell": 1
            }
        ).batch_size(10000)
        
        for doc in cursor:
            writer.writerow({
                "collision_index": doc.get("collision_index"),
                "collision_year": doc.get("collision_year"),
                "date": doc.get("date"),
                "time": doc.get("time") or "",
                "hour": doc.get("hour") if doc.get("hour") is not None else "",
                "day_of_week": doc.get("day_of_week") or "",
                "day_of_week_name": doc.get("day_of_week_name") or "",
                "month": doc.get("month") or "",
                "month_name": doc.get("month_name") or "",
                "severity": doc.get("severity") or "",
                "collision_severity": doc.get("collision_severity") or "",
                "is_fatal_or_serious": 1 if doc.get("is_fatal_or_serious") else 0,
                "number_of_vehicles": doc.get("number_of_vehicles") or 1,
                "number_of_casualties": doc.get("number_of_casualties") or 1,
                "speed_limit": doc.get("speed_limit") if doc.get("speed_limit") is not None else "",
                "weather_conditions": doc.get("weather_conditions") or "",
                "light_conditions": doc.get("light_conditions") or "",
                "road_surface_conditions": doc.get("road_surface_conditions") or "",
                "road_type": doc.get("road_type") or "",
                "urban_rural": doc.get("urban_rural") or "",
                "latitude": doc.get("latitude") if doc.get("latitude") is not None else "",
                "longitude": doc.get("longitude") if doc.get("longitude") is not None else "",
                "grid_cell": doc.get("grid_cell") or ""
            })
            count += 1
            if count % 50000 == 0:
                print(f"  Wrote {count:,} collision rows...")
                
    print(f"  Completed 'fact_collisions.csv': {count:,} records.")
    return count

def export_dim_calendar() -> int:
    print("\nExporting 'dim_calendar.csv'...")
    target_path = os.path.join(EXPORTS_DIR, "dim_calendar.csv")
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    fields = [
        "date",
        "year",
        "month_number",
        "month_name",
        "day_of_month",
        "day_of_week",
        "weekday_name",
        "is_weekend",
        "quarter",
        "year_month"
    ]
    
    count = 0
    curr = start_date
    with open(target_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        while curr <= end_date:
            dow = curr.isoweekday()  # 1 = Mon, 7 = Sun
            dow_name = curr.strftime("%A")
            writer.writerow({
                "date": curr.strftime("%Y-%m-%d"),
                "year": curr.year,
                "month_number": curr.month,
                "month_name": curr.strftime("%B"),
                "day_of_month": curr.day,
                "day_of_week": dow,
                "weekday_name": dow_name,
                "is_weekend": 1 if dow in (6, 7) else 0,
                "quarter": f"Q{(curr.month - 1) // 3 + 1}",
                "year_month": curr.strftime("%Y-%m")
            })
            count += 1
            curr += timedelta(days=1)
            
    print(f"  Completed 'dim_calendar.csv': {count:,} calendar dates.")
    return count

def export_agg_hotspots(db) -> int:
    print("\nExporting 'agg_hotspots_grid.csv'...")
    target_path = os.path.join(EXPORTS_DIR, "agg_hotspots_grid.csv")
    
    pipeline = [
        {"$match": {"has_valid_coordinates": True, "grid_cell": {"$ne": None}}},
        {
            "$group": {
                "_id": {
                    "grid_cell": "$grid_cell",
                    "collision_year": "$collision_year"
                },
                "total_collisions": {"$sum": 1},
                "fatal_count": {"$sum": {"$cond": [{"$eq": ["$severity", "Fatal"]}, 1, 0]}},
                "serious_count": {"$sum": {"$cond": [{"$eq": ["$severity", "Serious"]}, 1, 0]}},
                "slight_count": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}},
                "total_casualties": {"$sum": "$number_of_casualties"},
                "latitude": {"$avg": "$latitude"},
                "longitude": {"$avg": "$longitude"}
            }
        },
        {"$match": {"total_collisions": {"$gte": 5}}},
        {"$sort": {"total_collisions": -1}}
    ]
    
    fields = [
        "grid_id",
        "collision_year",
        "total_collisions",
        "fatal_count",
        "serious_count",
        "slight_count",
        "serious_fatal_share_pct",
        "total_casualties",
        "latitude",
        "longitude"
    ]
    
    count = 0
    with open(target_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for doc in db.collisions.aggregate(pipeline):
            tot = doc["total_collisions"]
            ksi = doc["fatal_count"] + doc["serious_count"]
            share = round((ksi / tot * 100), 2) if tot > 0 else 0.0
            writer.writerow({
                "grid_id": doc["_id"]["grid_cell"],
                "collision_year": doc["_id"]["collision_year"],
                "total_collisions": tot,
                "fatal_count": doc["fatal_count"],
                "serious_count": doc["serious_count"],
                "slight_count": doc["slight_count"],
                "serious_fatal_share_pct": share,
                "total_casualties": doc["total_casualties"],
                "latitude": round(doc["latitude"], 5),
                "longitude": round(doc["longitude"], 5)
            })
            count += 1
            
    print(f"  Completed 'agg_hotspots_grid.csv': {count:,} grid summaries.")
    return count

def export_agg_severity_conditions(db) -> int:
    print("\nExporting 'agg_severity_conditions.csv'...")
    target_path = os.path.join(EXPORTS_DIR, "agg_severity_conditions.csv")
    
    fields = [
        "factor_type",
        "factor_value",
        "collision_year",
        "total_collisions",
        "fatal_count",
        "serious_count",
        "slight_count",
        "serious_fatal_share_pct"
    ]
    
    factors = [
        ("Weather", "weather_conditions"),
        ("Lighting", "light_conditions"),
        ("Road Surface", "road_surface_conditions"),
        ("Road Type", "road_type"),
        ("Speed Limit", "speed_limit"),
        ("Urban Rural", "urban_rural")
    ]
    
    count = 0
    with open(target_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for factor_label, factor_col in factors:
            pipeline = [
                {"$match": {factor_col: {"$ne": None, "$ne": ""}}},
                {
                    "$group": {
                        "_id": {
                            "val": f"${factor_col}",
                            "year": "$collision_year"
                        },
                        "total": {"$sum": 1},
                        "fatal": {"$sum": {"$cond": [{"$eq": ["$severity", "Fatal"]}, 1, 0]}},
                        "serious": {"$sum": {"$cond": [{"$eq": ["$severity", "Serious"]}, 1, 0]}},
                        "slight": {"$sum": {"$cond": [{"$eq": ["$severity", "Slight"]}, 1, 0]}}
                    }
                },
                {"$sort": {"total": -1}}
            ]
            
            for doc in db.collisions.aggregate(pipeline):
                tot = doc["total"]
                ksi = doc["fatal"] + doc["serious"]
                share = round((ksi / tot * 100), 2) if tot > 0 else 0.0
                val_str = str(doc["_id"]["val"])
                if factor_col == "speed_limit":
                    val_str = f"{val_str} mph"
                writer.writerow({
                    "factor_type": factor_label,
                    "factor_value": val_str,
                    "collision_year": doc["_id"]["year"],
                    "total_collisions": tot,
                    "fatal_count": doc["fatal"],
                    "serious_count": doc["serious"],
                    "slight_count": doc["slight"],
                    "serious_fatal_share_pct": share
                })
                count += 1
                
    print(f"  Completed 'agg_severity_conditions.csv': {count:,} condition factor rows.")
    return count

def export_agg_vehicles(db) -> int:
    print("\nExporting 'agg_vehicle_types.csv'...")
    target_path = os.path.join(EXPORTS_DIR, "agg_vehicle_types.csv")
    
    # Pre-aggregate vehicles by type and year
    pipeline = [
        {
            "$group": {
                "_id": {
                    "vehicle_type": "$vehicle_type",
                    "collision_year": "$collision_year"
                },
                "total_vehicles": {"$sum": 1},
                "avg_age_of_driver": {"$avg": "$age_of_driver"},
                "avg_age_of_vehicle": {"$avg": "$age_of_vehicle"}
            }
        },
        {"$sort": {"total_vehicles": -1}}
    ]
    
    fields = [
        "vehicle_type",
        "collision_year",
        "total_vehicles",
        "avg_age_of_driver",
        "avg_age_of_vehicle"
    ]
    
    count = 0
    with open(target_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for doc in db.vehicles.aggregate(pipeline):
            writer.writerow({
                "vehicle_type": doc["_id"]["vehicle_type"],
                "collision_year": doc["_id"]["collision_year"],
                "total_vehicles": doc["total_vehicles"],
                "avg_age_of_driver": round(doc["avg_age_of_driver"], 1) if doc["avg_age_of_driver"] else "",
                "avg_age_of_vehicle": round(doc["avg_age_of_vehicle"], 1) if doc["avg_age_of_vehicle"] else ""
            })
            count += 1
            
    print(f"  Completed 'agg_vehicle_types.csv': {count:,} vehicle summary rows.")
    return count

def export_agg_vehicle_casualty_matrix(db) -> int:
    print("\nExporting 'agg_vehicle_casualty_matrix.csv' (Multi-Collection Join)...")
    target_path = os.path.join(EXPORTS_DIR, "agg_vehicle_casualty_matrix.csv")
    
    pipeline = [
        {
            "$lookup": {
                "from": "casualties",
                "localField": "collision_index",
                "foreignField": "collision_index",
                "as": "cas_list"
            }
        },
        {"$unwind": "$cas_list"},
        {
            "$group": {
                "_id": {
                    "vehicle_type": "$vehicle_type",
                    "casualty_class": "$cas_list.casualty_class",
                    "severity": "$cas_list.severity",
                    "collision_year": "$collision_year"
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}
    ]
    
    fields = [
        "vehicle_type",
        "casualty_class",
        "severity",
        "collision_year",
        "count"
    ]
    
    count = 0
    with open(target_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for doc in db.vehicles.aggregate(pipeline, allowDiskUse=True):
            writer.writerow({
                "vehicle_type": doc["_id"]["vehicle_type"],
                "casualty_class": doc["_id"]["casualty_class"],
                "severity": doc["_id"]["severity"],
                "collision_year": doc["_id"]["collision_year"],
                "count": doc["count"]
            })
            count += 1
            
    print(f"  Completed 'agg_vehicle_casualty_matrix.csv': {count:,} multi-collection relational matrix rows.")
    return count

def main():
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    print(f"Connecting to MongoDB at: {MONGO_URI}...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    
    start_time = time.time()
    
    # 1. Fact table
    c_count = export_fact_collisions(db)
    # 2. Calendar dimension
    d_count = export_dim_calendar()
    # 3. Aggregates
    h_count = export_agg_hotspots(db)
    s_count = export_agg_severity_conditions(db)
    v_count = export_agg_vehicles(db)
    vc_count = export_agg_vehicle_casualty_matrix(db)
    
    elapsed = time.time() - start_time
    print(f"\nAll Power BI CSV exports generated in {elapsed:.2f}s in: {EXPORTS_DIR}")

if __name__ == "__main__":
    main()
