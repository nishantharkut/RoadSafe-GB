import os
import csv
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pymongo import MongoClient, ASCENDING, GEOSPHERE

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "roadsafe"

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
META_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metadata")

GB_BOUNDS = {
    "min_lat": 49.8,
    "max_lat": 60.9,
    "min_lon": -8.6,
    "max_lon": 1.8
}

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

def load_codebook() -> Dict[str, Any]:
    path = os.path.join(META_DIR, "codebook_lookups.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"collision": {}, "vehicle": {}, "casualty": {}}

def parse_int(val: Any) -> Optional[int]:
    if val is None or str(val).strip() in ("", "-1", "null", "None"):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None

def parse_float(val: Any) -> Optional[float]:
    if val is None or str(val).strip() in ("", "-1", "null", "None"):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def clean_collision_row(row: Dict[str, str], lookups: Dict[str, Any]) -> Dict[str, Any]:
    c_look = lookups.get("collision", {})
    
    idx = row["collision_index"].strip()
    year = parse_int(row.get("collision_year")) or 2025
    ref_no = row.get("collision_ref_no", "").strip()
    
    sev_code = parse_int(row.get("collision_severity")) or 3
    sev_label = c_look.get("collision_severity", {}).get(str(sev_code), "Slight" if sev_code == 3 else ("Serious" if sev_code == 2 else "Fatal"))
    
    raw_date = row.get("date", "").strip()
    date_iso = None
    month_num = None
    month_name = None
    day_num = None
    
    if raw_date:
        try:
            if "/" in raw_date:
                dt = datetime.strptime(raw_date, "%d/%m/%Y")
            else:
                dt = datetime.strptime(raw_date, "%Y-%m-%d")
            date_iso = dt.strftime("%Y-%m-%d")
            month_num = dt.month
            month_name = MONTH_NAMES[dt.month]
            day_num = dt.day
        except Exception:
            date_iso = raw_date
            
    dow_code = parse_int(row.get("day_of_week"))
    dow_name = c_look.get("day_of_week", {}).get(str(dow_code), "Unknown")
    
    raw_time = row.get("time", "").strip()
    hour = None
    if raw_time and ":" in raw_time:
        try:
            hour = int(raw_time.split(":")[0])
        except ValueError:
            hour = None
            
    num_vehicles = parse_int(row.get("number_of_vehicles")) or 1
    num_casualties = parse_int(row.get("number_of_casualties")) or 1
    
    speed_limit = parse_int(row.get("speed_limit"))
    if speed_limit in (-1, 99):
        speed_limit = None
        
    weather_code = str(row.get("weather_conditions", "-1")).strip()
    weather_label = c_look.get("weather_conditions", {}).get(weather_code, "Unknown")
    
    light_code = str(row.get("light_conditions", "-1")).strip()
    light_label = c_look.get("light_conditions", {}).get(light_code, "Unknown")
    
    surface_code = str(row.get("road_surface_conditions", "-1")).strip()
    surface_label = c_look.get("road_surface_conditions", {}).get(surface_code, "Unknown")
    
    road_type_code = str(row.get("road_type", "-1")).strip()
    road_type_label = c_look.get("road_type", {}).get(road_type_code, "Unknown")
    
    urban_rural_code = str(row.get("urban_or_rural_area", "-1")).strip()
    urban_rural_label = "Urban" if urban_rural_code == "1" else ("Rural" if urban_rural_code == "2" else "Unallocated")
    
    lat = parse_float(row.get("latitude"))
    lon = parse_float(row.get("longitude"))
    
    has_valid_coords = False
    location = None
    grid_cell = None
    
    if lat is not None and lon is not None:
        if not ((lat == 0.0 and lon == 0.0) or (lat == -1.0 and lon == -1.0)):
            if GB_BOUNDS["min_lat"] <= lat <= GB_BOUNDS["max_lat"] and GB_BOUNDS["min_lon"] <= lon <= GB_BOUNDS["max_lon"]:
                has_valid_coords = True
                location = {
                    "type": "Point",
                    "coordinates": [round(lon, 6), round(lat, 6)]
                }
                grid_cell = f"{round(lat, 1)}_{round(lon, 1)}"

    return {
        "_id": idx,
        "collision_index": idx,
        "collision_year": year,
        "collision_ref_no": ref_no,
        "date": date_iso,
        "month": month_num,
        "month_name": month_name,
        "day": day_num,
        "time": raw_time if raw_time else None,
        "hour": hour,
        "day_of_week": dow_code,
        "day_of_week_name": dow_name,
        "collision_severity": sev_code,
        "severity": sev_label,
        "is_fatal_or_serious": (sev_code in (1, 2)),
        "number_of_vehicles": num_vehicles,
        "number_of_casualties": num_casualties,
        "speed_limit": speed_limit,
        "weather_code": weather_code,
        "weather_conditions": weather_label,
        "light_code": light_code,
        "light_conditions": light_label,
        "road_surface_code": surface_code,
        "road_surface_conditions": surface_label,
        "road_type_code": road_type_code,
        "road_type": road_type_label,
        "urban_rural": urban_rural_label,
        "local_authority_district": row.get("local_authority_district", "").strip(),
        "first_road_class": parse_int(row.get("first_road_class")),
        "first_road_number": row.get("first_road_number", "").strip(),
        "has_valid_coordinates": has_valid_coords,
        "latitude": round(lat, 6) if has_valid_coords else None,
        "longitude": round(lon, 6) if has_valid_coords else None,
        "location": location,
        "grid_cell": grid_cell
    }

def clean_vehicle_row(row: Dict[str, str], lookups: Dict[str, Any]) -> Dict[str, Any]:
    v_look = lookups.get("vehicle", {})
    idx = row["collision_index"].strip()
    ref = parse_int(row.get("vehicle_reference")) or 1
    veh_id = f"{idx}_{ref}"
    
    v_type_code = str(row.get("vehicle_type", "-1")).strip()
    v_type_label = v_look.get("vehicle_type", {}).get(v_type_code, "Unknown")
    
    age_driver = parse_int(row.get("age_of_driver"))
    if age_driver in (-1, 0): age_driver = None
    
    sex_code = str(row.get("sex_of_driver", "-1")).strip()
    sex_label = "Male" if sex_code == "1" else ("Female" if sex_code == "2" else "Unknown")
    
    age_veh = parse_int(row.get("age_of_vehicle"))
    if age_veh in (-1, 0): age_veh = None
    
    engine_cc = parse_int(row.get("engine_capacity_cc"))
    if engine_cc in (-1, 0): engine_cc = None
    
    return {
        "_id": veh_id,
        "vehicle_id": veh_id,
        "collision_index": idx,
        "collision_year": parse_int(row.get("collision_year")) or 2025,
        "vehicle_reference": ref,
        "vehicle_type_code": v_type_code,
        "vehicle_type": v_type_label,
        "age_of_driver": age_driver,
        "sex_of_driver": sex_label,
        "age_of_vehicle": age_veh,
        "engine_capacity_cc": engine_cc,
        "generic_make_model": row.get("generic_make_model", "").strip() or None
    }

def clean_casualty_row(row: Dict[str, str], lookups: Dict[str, Any]) -> Dict[str, Any]:
    idx = row["collision_index"].strip()
    cas_ref = parse_int(row.get("casualty_reference")) or 1
    veh_ref = parse_int(row.get("vehicle_reference")) or 1
    cas_id = f"{idx}_{cas_ref}"
    
    sev_code = parse_int(row.get("casualty_severity")) or 3
    sev_label = "Fatal" if sev_code == 1 else ("Serious" if sev_code == 2 else "Slight")
    
    class_code = str(row.get("casualty_class", "-1")).strip()
    class_label = "Driver or rider" if class_code == "1" else ("Passenger" if class_code == "2" else ("Pedestrian" if class_code == "3" else "Unknown"))
    
    sex_code = str(row.get("sex_of_casualty", "-1")).strip()
    sex_label = "Male" if sex_code == "1" else ("Female" if sex_code == "2" else "Unknown")
    
    age_cas = parse_int(row.get("age_of_casualty"))
    if age_cas in (-1, 0): age_cas = None
    
    return {
        "_id": cas_id,
        "casualty_id": cas_id,
        "collision_index": idx,
        "collision_year": parse_int(row.get("collision_year")) or 2025,
        "vehicle_reference": veh_ref,
        "casualty_reference": cas_ref,
        "casualty_severity": sev_code,
        "severity": sev_label,
        "casualty_class": class_label,
        "sex_of_casualty": sex_label,
        "age_of_casualty": age_cas
    }

def bulk_insert_file(file_path: str, collection, cleaner_func, lookups: Dict[str, Any], batch_size: int = 10000):
    print(f"\nStreaming {os.path.basename(file_path)} -> '{collection.name}'...")
    start_time = time.time()
    total_processed = 0
    batch = []
    
    with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doc = cleaner_func(row, lookups)
            batch.append(doc)
            total_processed += 1
            
            if len(batch) >= batch_size:
                collection.insert_many(batch, ordered=False)
                print(f"  Inserted {total_processed:,} records...")
                batch = []
                
        if batch:
            collection.insert_many(batch, ordered=False)
            print(f"  Inserted {total_processed:,} records...")
            
    elapsed = time.time() - start_time
    print(f"  Completed in {elapsed:.2f}s ({total_processed / elapsed:.0f} rec/s)")
    return {
        "file": os.path.basename(file_path),
        "total_records": total_processed,
        "seconds": round(elapsed, 2)
    }

def main():
    print(f"Connecting to MongoDB at: {MONGO_URI}...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("MongoDB connection verified!")
    
    db = client[DB_NAME]
    lookups = load_codebook()
    
    print("\nDropping previous collections for fresh load...")
    db.collisions.drop()
    db.vehicles.drop()
    db.casualties.drop()
    
    # 1. Collisions 2024 & 2025
    c24_path = os.path.join(DATA_DIR, "dft-road-casualty-statistics-collision-2024.csv")
    if os.path.exists(c24_path):
        bulk_insert_file(c24_path, db.collisions, clean_collision_row, lookups)
        
    c25_path = os.path.join(DATA_DIR, "dft-road-casualty-statistics-collision-2025.csv")
    if os.path.exists(c25_path):
        bulk_insert_file(c25_path, db.collisions, clean_collision_row, lookups)
        
    # 2. Vehicles 2025
    v25_path = os.path.join(DATA_DIR, "dft-road-casualty-statistics-vehicle-2025.csv")
    if os.path.exists(v25_path):
        bulk_insert_file(v25_path, db.vehicles, clean_vehicle_row, lookups)
        
    # 3. Casualties 2025
    cas25_path = os.path.join(DATA_DIR, "dft-road-casualty-statistics-casualty-2025.csv")
    if os.path.exists(cas25_path):
        bulk_insert_file(cas25_path, db.casualties, clean_casualty_row, lookups)
        
    # Create Indexes
    print("\nCreating production indexes...")
    idx_start = time.time()
    
    db.collisions.create_index([("collision_index", ASCENDING)], unique=True)
    db.collisions.create_index([("collision_year", ASCENDING), ("collision_severity", ASCENDING)])
    db.collisions.create_index([("date", ASCENDING), ("collision_severity", ASCENDING)])
    db.collisions.create_index([("grid_cell", ASCENDING), ("collision_year", ASCENDING)])
    db.collisions.create_index([("has_valid_coordinates", ASCENDING)])
    db.collisions.create_index([("location", GEOSPHERE)], partialFilterExpression={"location": {"$type": "object"}})
    
    db.vehicles.create_index([("vehicle_id", ASCENDING)], unique=True)
    db.vehicles.create_index([("collision_index", ASCENDING)])
    db.vehicles.create_index([("collision_year", ASCENDING), ("vehicle_type", ASCENDING)])
    
    db.casualties.create_index([("casualty_id", ASCENDING)], unique=True)
    db.casualties.create_index([("collision_index", ASCENDING)])
    db.casualties.create_index([("collision_year", ASCENDING), ("casualty_severity", ASCENDING)])
    
    print(f"All indexes created in {time.time() - idx_start:.2f}s!")
    
    # Audit counts
    c_tot = db.collisions.count_documents({})
    c_24 = db.collisions.count_documents({"collision_year": 2024})
    c_25 = db.collisions.count_documents({"collision_year": 2025})
    v_tot = db.vehicles.count_documents({})
    cas_tot = db.casualties.count_documents({})
    v_coords = db.collisions.count_documents({"has_valid_coordinates": True})
    
    print("\n=== IMPORT AUDIT RESULTS ===")
    print(f"  Collisions Total: {c_tot:,} (2024: {c_24:,}, 2025: {c_25:,})")
    print(f"  Valid GB Coordinates: {v_coords:,} ({(v_coords/c_tot)*100:.2f}%)")
    print(f"  Vehicles Total: {v_tot:,}")
    print(f"  Casualties Total: {cas_tot:,}")
    
    report = {
        "status": "SUCCESS",
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {
            "collisions_total": c_tot,
            "collisions_2024": c_24,
            "collisions_2025": c_25,
            "valid_coordinates": v_coords,
            "vehicles_total": v_tot,
            "casualties_total": cas_tot
        }
    }
    with open(os.path.join(META_DIR, "import_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("Report written to data/metadata/import_report.json")

if __name__ == "__main__":
    main()
