import os
import sys
import time
import hashlib
import json
import urllib.request
from typing import Dict, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
META_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metadata")

DOWNLOADS = {
    "collisions_2024": {
        "filename": "dft-road-casualty-statistics-collision-2024.csv",
        "url": "https://data.dft.gov.uk/road-accidents-safety-data/dft-road-casualty-statistics-collision-2024.csv",
        "description": "2024 Final Police-Reported Road Collisions"
    },
    "collisions_2025": {
        "filename": "dft-road-casualty-statistics-collision-2025.csv",
        "url": "https://data.dft.gov.uk/road-accidents-safety-data/dft-road-casualty-statistics-collision-2025.csv",
        "description": "2025 Final Police-Reported Road Collisions"
    },
    "vehicles_2025": {
        "filename": "dft-road-casualty-statistics-vehicle-2025.csv",
        "url": "https://data.dft.gov.uk/road-accidents-safety-data/dft-road-casualty-statistics-vehicle-2025.csv",
        "description": "2025 Vehicles Involved in Collisions"
    },
    "casualties_2025": {
        "filename": "dft-road-casualty-statistics-casualty-2025.csv",
        "url": "https://data.dft.gov.uk/road-accidents-safety-data/dft-road-casualty-statistics-casualty-2025.csv",
        "description": "2025 Casualties from Collisions"
    },
    "data_guide_2025": {
        "filename": "dft-road-casualty-statistics-road-safety-open-dataset-data-guide-2025.xlsx",
        "url": "https://assets.publishing.service.gov.uk/media/6ab2a71d997a4b2950cced58/dft-road-casualty-statistics-road-safety-open-dataset-data-guide-2025.xlsx",
        "description": "2025 Official DfT STATS19 Codebook and Variable Guide"
    }
}

def download_file(key: str, info: Dict[str, Any]) -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    target_path = os.path.join(DATA_DIR, info["filename"])
    url = info["url"]
    
    print(f"\n[{key}] Downloading: {info['filename']}")
    print(f"       From: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RoadSafeGB-ETL/1.0"
    }
    
    req = urllib.request.Request(url, headers=headers)
    start_time = time.time()
    
    # Stream download with hash computation
    sha256 = hashlib.sha256()
    bytes_downloaded = 0
    
    with urllib.request.urlopen(req, timeout=60) as response, open(target_path, "wb") as out_file:
        content_length = response.headers.get("Content-Length")
        total_size = int(content_length) if content_length else None
        
        chunk_size = 1024 * 1024  # 1MB chunks
        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            sha256.update(chunk)
            bytes_downloaded += len(chunk)
            
            if total_size:
                pct = (bytes_downloaded / total_size) * 100
                sys.stdout.write(f"\r       Progress: {bytes_downloaded / (1024*1024):.2f} MB / {total_size / (1024*1024):.2f} MB ({pct:.1f}%)")
            else:
                sys.stdout.write(f"\r       Downloaded: {bytes_downloaded / (1024*1024):.2f} MB")
            sys.stdout.flush()
    
    elapsed = time.time() - start_time
    digest = sha256.hexdigest()
    print(f"\n       Completed in {elapsed:.2f}s | Size: {bytes_downloaded:,} bytes | SHA-256: {digest[:16]}...")
    
    return {
        "key": key,
        "filename": info["filename"],
        "url": url,
        "description": info["description"],
        "local_path": target_path,
        "size_bytes": bytes_downloaded,
        "sha256": digest,
        "download_duration_seconds": round(elapsed, 2),
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def main():
    os.makedirs(META_DIR, exist_ok=True)
    manifest = {
        "publisher": "UK Department for Transport (DfT)",
        "licence": "UK Open Government Licence (OGL v3.0)",
        "download_session": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": {}
    }
    
    for key, info in DOWNLOADS.items():
        try:
            result = download_file(key, info)
            manifest["files"][key] = result
        except Exception as e:
            print(f"ERROR downloading {key}: {e}")
            raise
            
    manifest_path = os.path.join(META_DIR, "download_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest successfully written to: {manifest_path}")

if __name__ == "__main__":
    main()
