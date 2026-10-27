"""Semantic model for RoadSafe's verified CSV exports, with explicit grains."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "powerbi/exports"
INTEGER = set("collision_year hour day_of_week month collision_severity is_fatal_or_serious number_of_vehicles number_of_casualties speed_limit year month_number day_of_month is_weekend total_collisions fatal_count serious_count slight_count total_casualties total_vehicles count".split())
DOUBLE = set("latitude longitude serious_fatal_share_pct avg_age_of_driver avg_age_of_vehicle".split())
BASE_MEASURES = [
    ("Total Collisions", "COALESCE(COUNTROWS(fact_collisions), 0)", "#,0"),
    ("Total Casualties", "SUM(fact_collisions[number_of_casualties])", "#,0"),
    ("Total Vehicles", "SUM(fact_collisions[number_of_vehicles])", "#,0"),
    ("Fatal Collisions", 'CALCULATE([Total Collisions], KEEPFILTERS(fact_collisions[severity] = "Fatal"))', "#,0"),
    ("Serious Collisions", 'CALCULATE([Total Collisions], KEEPFILTERS(fact_collisions[severity] = "Serious"))', "#,0"),
    ("Slight Collisions", 'CALCULATE([Total Collisions], KEEPFILTERS(fact_collisions[severity] = "Slight"))', "#,0"),
    ("Severe Collisions", "[Fatal Collisions] + [Serious Collisions]", "#,0"),
    ("Severe Share", "DIVIDE([Severe Collisions], [Total Collisions])", "0.00%"),
    ("Casualties per Collision", "DIVIDE([Total Casualties], [Total Collisions])", "0.00"),
    ("Rural Collisions", 'CALCULATE([Total Collisions], fact_collisions[urban_rural] = "Rural")', "#,0"),
    ("Rural Severe Share", 'CALCULATE([Severe Share], fact_collisions[urban_rural] = "Rural")', "0.00%"),
    ("Weekend Severe Share", "CALCULATE([Severe Share], dim_calendar[is_weekend] = 1)", "0.00%"),
    ("Weekday Severe Share", "CALCULATE([Severe Share], dim_calendar[is_weekend] = 0)", "0.00%"),
    ("Weekend Difference pp", "VAR WeekendShare = [Weekend Severe Share] VAR WeekdayShare = [Weekday Severe Share] RETURN IF(NOT ISBLANK(WeekendShare) && NOT ISBLANK(WeekdayShare), (WeekendShare - WeekdayShare) * 100)", '0.00" pp"'),
    ("Active Grid Cells", 'CALCULATE(DISTINCTCOUNT(fact_collisions[grid_cell]), fact_collisions[grid_cell] <> BLANK())', "#,0"),
]


def build_model():
    tables = []
    for name in ["fact_collisions", "dim_calendar", "agg_hotspots_grid", "agg_severity_conditions", "agg_vehicle_types", "agg_vehicle_casualty_matrix"]:
        path = EXPORTS / f"{name}.csv"
        with path.open(encoding="utf-8-sig", newline="") as stream:
            headers = next(csv.reader(stream))
        columns, conversions = [], []
        for header in headers:
            dtype, mtype = ("int64", "Int64.Type") if header in INTEGER else (("double", "type number") if header in DOUBLE else (("dateTime", "type date") if header == "date" else ("string", "type text")))
            column = {"name": header, "dataType": dtype, "sourceColumn": header, "summarizeBy": "none"}
            if header == "date":
                column["formatString"] = "dd MMM yyyy"
                if name == "dim_calendar": column["isKey"] = True
            if dtype == "int64": column["formatString"] = "0" if header in ("year","collision_year","month","month_number","day_of_week","day_of_month","hour","speed_limit") else "#,0"
            if name == "fact_collisions" and header == "month_name": column["sortByColumn"] = "month"
            if name == "fact_collisions" and header == "day_of_week_name": column["sortByColumn"] = "day_of_week"
            if name == "dim_calendar" and header == "month_name": column["sortByColumn"] = "month_number"
            if name == "dim_calendar" and header == "weekday_name": column["sortByColumn"] = "day_of_week"
            columns.append(column)
            conversions.append('{"' + header + '", ' + mtype + '}')
        expression = ["let", f'    RawCsv = Csv.Document(File.Contents("{path.as_posix()}"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
                      '    Headers = Table.PromoteHeaders(RawCsv, [PromoteAllScalars=true]),',
                      '    Nulls = Table.ReplaceValue(Headers, "", null, Replacer.ReplaceValue, Table.ColumnNames(Headers)),',
                      '    Typed = Table.TransformColumnTypes(Nulls, {' + ", ".join(conversions) + '}, "en-GB")',
                      "in", "    Typed"]
        table = {"name": name, "columns": columns, "partitions": [{"name": name, "mode": "import", "source": {"type": "m", "expression": expression}}]}
        if name in ("agg_severity_conditions", "agg_vehicle_types", "agg_vehicle_casualty_matrix"):
            table["isHidden"] = True
        if name == "fact_collisions":
            table["columns"].append({"type":"calculated", "name":"month_short", "dataType":"string", "expression":"LEFT(fact_collisions[month_name], 3)", "sortByColumn":"month"})
            table["measures"] = [{"name": n, "expression": e, "formatString": f, "displayFolder": "Collision measures"} for n,e,f in BASE_MEASURES]
        if name == "agg_hotspots_grid":
            table["measures"] = [
                {"name":"Grid Collisions", "expression":"CALCULATE(SUM(agg_hotspots_grid[total_collisions]), TREATAS(VALUES(dim_calendar[year]), agg_hotspots_grid[collision_year]))", "formatString":"#,0"},
                {"name":"Grid Severe Share", "expression":"DIVIDE(CALCULATE(SUM(agg_hotspots_grid[fatal_count]) + SUM(agg_hotspots_grid[serious_count]), TREATAS(VALUES(dim_calendar[year]), agg_hotspots_grid[collision_year])), [Grid Collisions])", "formatString":"0.00%"},
                {"name":"Grid Longitude", "expression":"CALCULATE(AVERAGE(agg_hotspots_grid[longitude]), TREATAS(VALUES(dim_calendar[year]), agg_hotspots_grid[collision_year]))", "formatString":"0.00"},
                {"name":"Grid Latitude", "expression":"CALCULATE(AVERAGE(agg_hotspots_grid[latitude]), TREATAS(VALUES(dim_calendar[year]), agg_hotspots_grid[collision_year]))", "formatString":"0.00"},
            ]
        tables.append(table)
    return {"name":"RoadSafe_GB_Model", "compatibilityLevel":1606, "model":{
        "culture":"en-GB", "defaultPowerBIDataSourceVersion":"powerBI_V3", "sourceQueryCulture":"en-GB",
        "tables":tables, "relationships":[{"name":"Calendar_Collisions", "fromTable":"fact_collisions", "fromColumn":"date", "toTable":"dim_calendar", "toColumn":"date", "fromCardinality":"many", "toCardinality":"one", "crossFilteringBehavior":"oneDirection", "isActive":True}],
        "annotations":[{"name":"__PBI_TimeIntelligenceEnabled", "value":"0"}, {"name":"PBI_QueryOrder", "value":'["dim_calendar","fact_collisions","agg_hotspots_grid","agg_severity_conditions","agg_vehicle_types","agg_vehicle_casualty_matrix"]'}]}}
