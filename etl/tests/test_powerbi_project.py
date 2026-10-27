"""Regression checks for the failures that made the Power BI report empty."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PBI = ROOT / "powerbi"


def model():
    return json.loads((PBI / "RoadSafe_GB.SemanticModel/model.bim").read_text(encoding="utf-8-sig"))["model"]


def test_calendar_filters_collision_dates_through_active_relationship():
    relationships = model().get("relationships", [])
    assert any(r["fromTable"] == "fact_collisions" and r["fromColumn"] == "date"
               and r["toTable"] == "dim_calendar" and r["toColumn"] == "date"
               and r.get("isActive", True) for r in relationships)


def test_active_report_uses_supported_modern_format():
    binding = json.loads((PBI / "RoadSafe_GB.Report/definition.pbir").read_text())
    assert float(binding["version"]) >= 4
    assert not (PBI / "RoadSafe_GB.Report/report.json").exists(), "Legacy layout must not override the bound PBIR visuals"


def test_every_data_visual_is_bound_to_a_real_field_or_measure():
    tables = {t["name"]: t for t in model()["tables"]}
    definitions = list((PBI / "RoadSafe_GB.Report/definition/pages").glob("*/visuals/*/visual.json"))
    bound = 0
    for path in definitions:
        visual = json.loads(path.read_text())["visual"]
        if visual["visualType"] in ("textbox", "shape", "actionButton"):
            continue
        roles = visual.get("query", {}).get("queryState", {})
        assert roles, f"Empty visual: {path}"
        for role in roles.values():
            assert role.get("projections"), path
            for projection in role["projections"]:
                expression = projection["field"]
                if "Aggregation" in expression:
                    expression = expression["Aggregation"]["Expression"]
                kind = "Measure" if "Measure" in expression else "Column"
                field = expression[kind]
                table = tables[field["Expression"]["SourceRef"]["Entity"]]
                assert field["Property"] in {v["name"] for v in table["measures" if kind == "Measure" else "columns"]}
        bound += 1
    assert bound >= 15, "All three report pages need populated analytical visuals"


def test_csv_import_paths_and_header_types_are_explicit():
    for table in model()["tables"]:
        for partition in table["partitions"]:
            expression = "\n".join(partition["source"]["expression"])
            match = re.search(r'File\.Contents\("([^"]+)"\)', expression)
            assert match and Path(match.group(1)).is_file()
            assert "\\\\" not in match.group(1), "M strings do not use Python-style backslash escaping"
            assert "Table.TransformColumnTypes" in expression
