"""Recalculate report findings from the saved exports and draw labelled figures.

Run with the project virtual environment. This script never changes source data,
the database, application code, or the Power BI model.
"""
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
EVIDENCE = ROOT / "docs" / "report_evidence"
TEAL, SLATE, ORANGE = "#087e8b", "#233448", "#c66b25"


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def summarize(rows):
    severe = sum(row["severity"] in ("Fatal", "Serious") for row in rows)
    return {"collisions": len(rows), "severe": severe,
            "severe_share_pct": 100 * severe / len(rows) if rows else None}


def save_figure(fig, name):
    fig.savefig(FIG / f"{name}.png", dpi=240, bbox_inches="tight", facecolor="white")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)
    crops = {
        "report_web_records_detail.png": ("verified_web_records.png", (112, 130, 1328, 570)),
        "report_web_inspector_detail.png": ("verified_web_inspector.png", (272, 152, 1168, 872)),
    }
    for target, (source, bounds) in crops.items():
        Image.open(FIG / source).crop(bounds).save(FIG / target)
    rows = read_csv(ROOT / "powerbi/exports/fact_collisions.csv")
    baseline = summarize(rows)
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[key] for key in
                     ("speed_limit", "light_conditions", "weather_conditions", "urban_rural"))].append(row)
    combinations = []
    base_p = baseline["severe"] / baseline["collisions"]
    for conditions, subset in groups.items():
        if len(subset) < 100:
            continue
        result = summarize(subset)
        p = result["severe"] / result["collisions"]
        result.update(conditions=conditions, share_ratio=p / base_p,
                      odds_ratio=(p / (1 - p)) / (base_p / (1 - base_p)) if p < 1 else None)
        combinations.append(result)
    combinations.sort(key=lambda result: result["severe_share_pct"], reverse=True)
    weekday = [row for row in rows if row["day_of_week_name"] not in ("Saturday", "Sunday")]
    weekend = [row for row in rows if row["day_of_week_name"] in ("Saturday", "Sunday")]
    rush = [row for row in weekday if row["hour"] in ("8", "17", "18")]
    yearly = {year: summarize([row for row in rows if row["collision_year"] == year])
              for year in ("2024", "2025")}
    speed = {value: summarize([row for row in rows if row["speed_limit"] == value])
             for value in ("20", "30", "40", "50", "60", "70")}
    grid_ids = {row["grid_cell"] for row in rows if row["grid_cell"]}
    hourly = Counter(int(row["hour"]) for row in rows if row["hour"])
    exports = {}
    for path in sorted((ROOT / "powerbi/exports").glob("*.csv")):
        rr = read_csv(path)
        exports[path.name] = {"rows": len(rr), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    metrics = {"baseline": baseline, "yearly": yearly,
               "severity_counts": dict(Counter(row["severity"] for row in rows)),
               "speed_limits": speed, "weekday": summarize(weekday), "weekend": summarize(weekend),
               "rush_hours": {"hours": [8, 17, 18], "weekday_collisions": len(rush),
                              "weekday_share_pct": 100 * len(rush) / len(weekday)},
               "hourly": dict(sorted(hourly.items())), "combinations_minimum_support_100": combinations,
               "unique_grid_cells": len(grid_ids),
               "duplicate_collision_ids": len(rows) - len({row["collision_index"] for row in rows}),
               "total_casualties_in_collision_records": sum(int(row["number_of_casualties"]) for row in rows),
               "total_vehicles_in_collision_records": sum(int(row["number_of_vehicles"]) for row in rows),
               "exports": exports}
    (EVIDENCE / "verified_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": SLATE, "text.color": SLATE,
                         "axes.titleweight": "bold", "axes.titlepad": 14})
    fig, ax = plt.subplots(figsize=(10, 3.5), layout="constrained")
    values = [speed[str(limit)]["severe_share_pct"] for limit in (20, 30, 40, 50, 60, 70)]
    bars = ax.bar([f"{limit} mph" for limit in (20, 30, 40, 50, 60, 70)], values,
                  color=[TEAL, TEAL, TEAL, TEAL, ORANGE, TEAL], width=.58)
    ax.axhline(baseline["severe_share_pct"], color=SLATE, linestyle="--", linewidth=1)
    ax.text(5.35, baseline["severe_share_pct"] + .8, "All collisions: 25.54%", ha="right", fontsize=10)
    ax.bar_label(bars, labels=[f"{v:.2f}%" for v in values], padding=5, fontsize=11)
    ax.set(ylim=(0, 44), ylabel="Fatal or serious collisions (%)",
           title="Severe collision share by posted speed limit | 2024-2025")
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=.16)
    save_figure(fig, "report_speed_severity")

    fig, ax = plt.subplots(figsize=(10, 3.1), layout="constrained")
    ax.bar(range(24), [hourly[h] for h in range(24)],
           color=[ORANGE if h in (8, 17, 18) else TEAL for h in range(24)], width=.74)
    ax.set(xticks=range(0, 24, 2), xlabel="Hour of day", ylabel="Recorded collisions",
           title="Hourly collision volume | 2024-2025")
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=.16)
    save_figure(fig, "report_hourly_distribution")

    fig, ax = plt.subplots(figsize=(10, 4.1))
    ax.set(xlim=(0, 10), ylim=(0, 4.1)); ax.axis("off")
    boxes = [(0.1, 2.85, 2.7, .9, "DfT STATS19 CSV files", "Collisions: 2024-2025\nVehicles and casualties: 2025"),
             (3.55, 2.85, 2.7, .9, "Python ETL", "Clean codes and dates\nValidate coordinates; derive grid"),
             (7.0, 2.85, 2.7, .9, "MongoDB", "3 collections; 514,283 documents\nUnique, compound and spatial indexes"),
             (3.55, 1.3, 2.7, .9, "Flask API + React", "Aggregations, map and scenarios\nRecord-level inspection"),
             (7.0, 1.3, 2.7, .9, "CSV exports + Power BI", "6 tables; active calendar relationship\n3 populated analytical report pages")]
    for x,y,w,h,title,body in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.08,rounding_size=0.04",
                                   facecolor="#f3f7f8",edgecolor="#b6c9ce",linewidth=1))
        ax.text(x+.1,y+h-.19,title,fontsize=11,fontweight="bold",va="top")
        ax.text(x+.1,y+.38,body,fontsize=8.4,va="center",linespacing=1.6)
    for start,end in [((2.9,3.3),(3.4,3.3)),((6.35,3.3),(6.85,3.3)),
                      ((8.35,2.7),(8.35,2.35)),((7.0,2.85),(6.0,2.25))]:
        ax.annotate("",xy=end,xytext=start,arrowprops={"arrowstyle":"->","color":TEAL,"lw":1.8})
    ax.text(.1,.45,"Architecture diagram drawn from the repository; not an application screenshot.",fontsize=9,color="#5c6d7e")
    fig.tight_layout(pad=.2)
    save_figure(fig, "report_system_architecture")

    manifest = []
    for path in sorted(FIG.glob("verified*.png")):
        manifest.append({"file":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
                         "kind":"native desktop capture" if "powerbi" in path.name else "live web application capture"})
    for target, (source, bounds) in crops.items():
        manifest.append({"file": target, "source": source, "crop_pixels": bounds,
                         "sha256": hashlib.sha256((FIG / target).read_bytes()).hexdigest(),
                         "kind": "crop of an unmodified live screenshot"})
    pbi_crops = EVIDENCE / "powerbi_capture_crops.json"
    if pbi_crops.exists():
        for item in json.loads(pbi_crops.read_text(encoding="utf-8")):
            for capture in manifest:
                if capture["file"] == item["file"]:
                    capture.update(source=item["source"],crop_pixels=item["crop_pixels"],
                                   kind="crop of native Power BI Desktop report capture")
    (EVIDENCE / "screenshot_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps({"baseline":baseline,"years":yearly,"rush":metrics["rush_hours"],
                      "unique_grid_cells":len(grid_ids),"screenshots":len(manifest)},indent=2))


if __name__ == "__main__":
    main()
