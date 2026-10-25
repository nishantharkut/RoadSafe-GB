import os
import csv
import json
import openpyxl
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
META_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metadata")

GB_BOUNDS = {
    "min_lat": 49.8,
    "max_lat": 60.9,
    "min_lon": -8.6,
    "max_lon": 1.8
}

def inspect_csv(file_path: str, is_collision: bool = False) -> Dict[str, Any]:
    print(f"\nInspecting: {os.path.basename(file_path)}")
    total_rows = 0
    header: List[str] = []
    
    # Track coordinates if collision
    valid_gb_coords = 0
    missing_or_invalid_coords = 0
    out_of_bounds_coords = 0
    null_island_coords = 0
    min_lat, max_lat = float('inf'), float('-inf')
    min_lon, max_lon = float('inf'), float('-inf')
    
    severity_counts = {}
    year_counts = {}
    
    with open(file_path, "r", encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        
        for row in reader:
            total_rows += 1
            
            if is_collision:
                # Check year
                yr = row.get("collision_year")
                if yr:
                    year_counts[yr] = year_counts.get(yr, 0) + 1
                    
                # Check severity
                sev = row.get("accident_severity")
                if sev:
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1
                    
                # Check coordinates
                lat_raw = row.get("latitude")
                lon_raw = row.get("longitude")
                
                try:
                    if not lat_raw or not lon_raw or lat_raw.strip() == "" or lon_raw.strip() == "":
                        missing_or_invalid_coords += 1
                        continue
                        
                    lat = float(lat_raw)
                    lon = float(lon_raw)
                    
                    if (lat == 0.0 and lon == 0.0) or (lat == -1.0 and lon == -1.0):
                        null_island_coords += 1
                        missing_or_invalid_coords += 1
                        continue
                        
                    min_lat = min(min_lat, lat)
                    max_lat = max(max_lat, lat)
                    min_lon = min(min_lon, lon)
                    max_lon = max(max_lon, lon)
                    
                    if GB_BOUNDS["min_lat"] <= lat <= GB_BOUNDS["max_lat"] and GB_BOUNDS["min_lon"] <= lon <= GB_BOUNDS["max_lon"]:
                        valid_gb_coords += 1
                    else:
                        out_of_bounds_coords += 1
                except ValueError:
                    missing_or_invalid_coords += 1

    print(f"  Total records: {total_rows:,}")
    print(f"  Total columns: {len(header)}")
    print(f"  First 8 columns: {header[:8]}")
    
    res = {
        "file": os.path.basename(file_path),
        "total_rows": total_rows,
        "column_count": len(header),
        "columns": header
    }
    
    if is_collision:
        print(f"  Year breakdown: {year_counts}")
        print(f"  Severity breakdown: {severity_counts}")
        print(f"  Valid GB coordinates: {valid_gb_coords:,} ({(valid_gb_coords/total_rows)*100:.2f}%)")
        print(f"  Missing/Invalid coords: {missing_or_invalid_coords:,}")
        print(f"  Observed Latitude range: [{min_lat:.4f}, {max_lat:.4f}]")
        print(f"  Observed Longitude range: [{min_lon:.4f}, {max_lon:.4f}]")
        res["years"] = year_counts
        res["severity"] = severity_counts
        res["valid_gb_coords"] = valid_gb_coords
        res["missing_coords"] = missing_or_invalid_coords
        res["lat_range"] = [min_lat, max_lat] if min_lat != float('inf') else None
        res["lon_range"] = [min_lon, max_lon] if min_lon != float('inf') else None
        
    return res

def inspect_codebook(xlsx_path: str) -> Dict[str, Any]:
    print(f"\nInspecting Codebook: {os.path.basename(xlsx_path)}")
    wb = openpyxl.load_workbook(xlsx_path, read_only=True)
    sheets = wb.sheetnames
    print(f"  Worksheet tabs: {sheets}")
    return {"file": os.path.basename(xlsx_path), "sheets": sheets}

def main():
    os.makedirs(META_DIR, exist_ok=True)
    summary = {}
    
    # Inspect CSVs
    c24 = os.path.join(DATA_DIR, "dft-road-casualty-statistics-collision-2024.csv")
    if os.path.exists(c24):
        summary["collisions_2024"] = inspect_csv(c24, is_collision=True)
        
    c25 = os.path.join(DATA_DIR, "dft-road-casualty-statistics-collision-2025.csv")
    if os.path.exists(c25):
        summary["collisions_2025"] = inspect_csv(c25, is_collision=True)
        
    v25 = os.path.join(DATA_DIR, "dft-road-casualty-statistics-vehicle-2025.csv")
    if os.path.exists(v25):
        summary["vehicles_2025"] = inspect_csv(v25, is_collision=False)
        
    cas25 = os.path.join(DATA_DIR, "dft-road-casualty-statistics-casualty-2025.csv")
    if os.path.exists(cas25):
        summary["casualties_2025"] = inspect_csv(cas25, is_collision=False)
        
    guide_path = os.path.join(DATA_DIR, "dft-road-casualty-statistics-road-safety-open-dataset-data-guide-2025.xlsx")
    if os.path.exists(guide_path):
        summary["codebook"] = inspect_codebook(guide_path)
        
    summary_path = os.path.join(META_DIR, "inspection_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nInspection summary written to: {summary_path}")

if __name__ == "__main__":
    main()
