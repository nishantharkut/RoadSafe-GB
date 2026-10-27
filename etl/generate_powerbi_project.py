"""Build the supported PBIP/PBIR project from verified CSV exports.

The first migration archives the old legacy layout and unbound PBIR definition.
The native Desktop application is responsible for importing and saving data.
"""
import json
from pathlib import Path
import shutil

from powerbi_model import build_model
from powerbi_report import write_report

ROOT=Path(__file__).resolve().parents[1]
PBI=ROOT/"powerbi"


def generate():
    report=PBI/"RoadSafe_GB.Report"
    backup=ROOT/"docs/archive/powerbi_before_completion"
    backup.mkdir(parents=True,exist_ok=True)
    # Both paths are verified descendants of this workspace before any move.
    for source,name in [(report/"report.json","legacy_report_replaced.json"),
                        (report/"definition","unbound_definition_replaced")]:
        destination=backup/name
        assert source.resolve().is_relative_to(ROOT.resolve())
        assert destination.resolve().is_relative_to(ROOT.resolve())
        if source.exists() and not destination.exists():
            shutil.move(str(source),str(destination))
    write_report(report)
    (PBI/"RoadSafe_GB.pbip").write_text(json.dumps({
        "$schema":"https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version":"1.0", "artifacts":[{"report":{"path":"RoadSafe_GB.Report"}}],
        "settings":{"enableAutoRecovery":True}},indent=2),encoding="utf-8")
    model=build_model()
    target=PBI/"RoadSafe_GB.SemanticModel/model.bim"
    target.write_text(json.dumps(model,indent=2),encoding="utf-8")
    (PBI/"RoadSafe_GB.SemanticModel/definition.pbism").write_text(json.dumps({"version":"4.2","settings":{}},indent=2),encoding="utf-8")
    print(f"Built {len(model['model']['tables'])} model tables, {len(model['model']['relationships'])} relationship and 3 data-bound report pages.")


if __name__=="__main__":generate()
