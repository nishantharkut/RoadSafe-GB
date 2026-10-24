import os
import json
import openpyxl
from typing import Dict, Any

META_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metadata")
GUIDE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "dft-road-casualty-statistics-road-safety-open-dataset-data-guide-2025.xlsx")

def build_codebook_lookups() -> Dict[str, Any]:
    print(f"Loading codebook from: {GUIDE_PATH}")
    wb = openpyxl.load_workbook(GUIDE_PATH, read_only=True)
    sheet = wb["2024_code_list"]
    
    lookups = {
        "collision": {},
        "vehicle": {},
        "casualty": {}
    }
    
    for row in sheet.iter_rows(values_only=True):
        if not row or len(row) < 4:
            continue
        table, field, code, label = row[0], row[1], row[2], row[3]
        if not table or not field or code is None or label is None:
            continue
        table_str = str(table).strip().lower()
        if table_str not in lookups:
            continue
            
        field_str = str(field).strip()
        code_str = str(code).strip()
        label_str = str(label).strip()
        
        if field_str not in lookups[table_str]:
            lookups[table_str][field_str] = {}
            
        lookups[table_str][field_str][code_str] = label_str
        
    os.makedirs(META_DIR, exist_ok=True)
    out_path = os.path.join(META_DIR, "codebook_lookups.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(lookups, f, indent=2)
        
    print(f"Built codebook lookups with:")
    for t in lookups:
        print(f"  Table '{t}': {len(lookups[t])} coded fields")
    print(f"Saved lookups to: {out_path}")
    return lookups

if __name__ == "__main__":
    build_codebook_lookups()
