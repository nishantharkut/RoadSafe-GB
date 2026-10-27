"""Data-bound native PBIR pages. No placeholder or instruction-only visuals."""
import json
from pathlib import Path

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
INK, TEAL, MUTED = "#233448", "#087E8B", "#526476"


def lit(value):
    if isinstance(value, bool): value = str(value).lower()
    elif isinstance(value, (int, float)): value = f"{value}D"
    else: value = "'" + str(value).replace("'", "''") + "'"
    return {"expr":{"Literal":{"Value":value}}}


def fill(color):
    return {"solid":{"color":lit(color)}}


def projection(table, field, kind="Column"):
    return {"field":{kind:{"Expression":{"SourceRef":{"Entity":table}},"Property":field}},
            "queryRef":f"{table}.{field}","nativeQueryRef":field}


def container(title=None):
    objects = {"background":[{"properties":{"show":lit(True),"color":fill("#FFFFFF"),"transparency":lit(0)}}],
               "border":[{"properties":{"show":lit(False)}}],
               "visualHeader":[{"properties":{"show":lit(False)}}],
               "padding":[{"properties":{k:lit(10) for k in ("left","right","top","bottom")}}]}
    if title:
        objects["title"]=[{"properties":{"show":lit(True),"text":lit(title),"fontSize":lit(14),"fontColor":fill(INK),"fontFamily":lit("Segoe UI Semibold"),"alignment":lit("left")}}]
    return objects


def visual(name, kind, box, roles=None, title=None, objects=None):
    x,y,w,h = box
    item={"$schema":SCHEMA+"visualContainer/2.9.0/schema.json","name":name,
          "position":{"x":x,"y":y,"z":1000+y,"width":w,"height":h,"tabOrder":1000+y},
          "visual":{"visualType":kind,"visualContainerObjects":container(title),"drillFilterOtherVisuals":True}}
    if roles:item["visual"]["query"]={"queryState":{key:{"projections":values} for key,values in roles.items()}}
    if objects:item["visual"]["objects"]=objects
    return item


def text(name, value, box, size=22, color=INK):
    v=visual(name,"textbox",box)
    v["visual"]["objects"]={"general":[{"properties":{"paragraphs":[{"textRuns":[{"value":value,"textStyle":{"fontFamily":"Segoe UI Semibold" if size>16 else "Segoe UI","fontSize":f"{size}pt","color":color}}]}]}}]}
    v["visual"]["visualContainerObjects"]["background"][0]["properties"]["show"]=lit(False)
    v["visual"]["visualContainerObjects"]["padding"][0]["properties"]={k:lit(0) for k in ("left","right","top","bottom")}
    return v


def card(name, measure, title, box):
    return visual(name,"card",box,{"Values":[projection("fact_collisions",measure,"Measure")]},title,
                  {"labels":[{"properties":{"fontSize":lit(30),"color":fill(TEAL),"labelDisplayUnits":lit(1),"labelPrecision":lit(2 if "Share" in measure or "pp" in measure else 0)}}],
                   "categoryLabels":[{"properties":{"show":lit(False)}}]})


def chart(name, kind, field, measure, title, box, series=None, table="fact_collisions"):
    roles={"Category":[projection(table,field)],"Y":[projection("fact_collisions",measure,"Measure")]}
    if series:roles["Series"]=[projection(table,series)]
    v=visual(name,kind,box,roles,title,{
        "categoryAxis":[{"properties":{"fontSize":lit(11),"showAxisTitle":lit(False),"maxMarginFactor":lit(45)}}],
        "valueAxis":[{"properties":{"fontSize":lit(11),"showAxisTitle":lit(False)}}],
        "dataPoint":[{"properties":{"defaultColor":fill(TEAL)}}]})
    if series:
        del v["visual"]["objects"]["dataPoint"]
    # Chronological/category order is defined by each model column's sortByColumn.
    if kind in ("lineChart","clusteredColumnChart"):
        v["visual"]["query"]["sortDefinition"]={"sort":[{"field":projection(table,field)["field"],"direction":"Ascending"}],"isDefaultSort":True}
    return v


def table(name, fields, title, box):
    return visual(name,"tableEx",box,{"Values":fields},title,{
        "columnHeaders":[{"properties":{"fontSize":lit(11),"autoSizeColumnWidth":lit(True),"columnAdjustment":lit("growToFit")}}],
        "values":[{"properties":{"fontSize":lit(11)}}],
        "grid":[{"properties":{"rowPadding":lit(3)}}]})


def page_header(title, subtitle):
    year=visual("YearFilter","slicer",(1060,12,196,96),{"Values":[projection("dim_calendar","year")]},None,
                {"data":[{"properties":{"mode":lit("Dropdown")}}],
                 "header":[{"properties":{"show":lit(True),"text":lit("YEAR"),"textSize":lit(12)}}],
                 "selection":[{"properties":{"singleSelect":lit(False),"selectAllCheckboxEnabled":lit(True)}}],
                 "items":[{"properties":{"textSize":lit(12)}}]})
    return [text("PageTitle",title,(24,14,1020,44),24),
            text("PageSubtitle",subtitle,(24,62,1010,34),12,MUTED),year,
            text("SourceNote","Source: UK DfT STATS19 | Police-reported injury collisions | Select a year or click a chart to filter",(24,756,1230,28),11,MUTED)]


def build_pages():
    overview=page_header("RoadSafe GB | Collision overview","2024-2025 collision records. Casualty and vehicle KPIs sum the counts recorded for each incident.")
    for i,(measure,title) in enumerate([("Total Collisions","Recorded collisions"),("Severe Share","Fatal or serious share"),("Total Casualties","Recorded casualties"),("Total Vehicles","Involved vehicles")]):
        overview.append(card(f"KPI{i}",measure,title,(24+312*i,120,296,112)))
    overview += [chart("MonthlyVolume","lineChart","month_short","Total Collisions","Monthly collisions by year",(24,250,792,270),series="collision_year"),
                 visual("SeverityMix","donutChart",(836,250,420,270),{"Category":[projection("fact_collisions","severity")],"Y":[projection("fact_collisions","Total Collisions","Measure")]},"Collision severity composition"),
                 chart("AreaVolume","clusteredBarChart","urban_rural","Total Collisions","Urban and rural collision volume",(24,540,600,195)),
                 table("AnnualSummary",[projection("dim_calendar","year")]+[projection("fact_collisions",m,"Measure") for m in ["Total Collisions","Severe Collisions","Severe Share"]],"Annual summary",(644,540,612,195))]
    temporal=page_header("RoadSafe GB | Time and place","Grid bubbles use groups with at least 5 collisions per year; the time charts include all collision records.")
    temporal += [chart("HourlyVolume","clusteredColumnChart","hour","Total Collisions","Collisions by hour of day",(24,120,680,250)),
                 chart("WeekdayVolume","clusteredColumnChart","day_of_week_name","Total Collisions","Collisions by day of week",(24,390,680,230)),
                 card("WeekendShare","Weekend Severe Share","Weekend severe share",(24,640,216,96)),
                 card("WeekdayShare","Weekday Severe Share","Weekday severe share",(256,640,216,96)),
                 card("WeekendDifference","Weekend Difference pp","Weekend difference",(488,640,216,96)),
                 visual("GridCoordinates","scatterChart",(724,120,532,616),{
                     "Category":[projection("agg_hotspots_grid","grid_id")],
                     "X":[projection("agg_hotspots_grid","Grid Longitude","Measure")],
                     "Y":[projection("agg_hotspots_grid","Grid Latitude","Measure")],
                     "Size":[projection("agg_hotspots_grid","Grid Collisions","Measure")],
                     "Tooltips":[projection("agg_hotspots_grid","Grid Severe Share","Measure")]},"Collision grid concentrations")]
    conditions=page_header("RoadSafe GB | Conditions and severity","Shares describe outcomes among recorded collisions. Posted speed limit is not the measured speed of an involved vehicle.")
    conditions += [chart("SpeedShare","clusteredColumnChart","speed_limit","Severe Share","Severe collision share by speed limit (mph)",(24,120,600,275)),
                   chart("LightingShare","clusteredBarChart","light_conditions","Severe Share","Severe share by lighting",(644,120,612,275)),
                   chart("WeatherShare","clusteredBarChart","weather_conditions","Severe Share","Severe share by weather",(24,415,600,315)),
                   table("SpeedEvidence",[projection("fact_collisions","speed_limit")]+[projection("fact_collisions",m,"Measure") for m in ["Total Collisions","Severe Collisions","Severe Share"]],"Speed-limit evidence | sample size and severity",(644,415,612,315))]
    return [("Section_Overview","1. Collision overview",overview),("Section_Geo","2. Time and place",temporal),("Section_Conditions","3. Conditions and severity",conditions)]


def write_report(directory):
    def write(path,data):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2),encoding="utf-8")
    write(directory/"definition.pbir",{"$schema":"https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json","version":"4.0","datasetReference":{"byPath":{"path":"../RoadSafe_GB.SemanticModel"}}})
    definition=directory/"definition"
    write(definition/"version.json",{"$schema":SCHEMA+"versionMetadata/1.0.0/schema.json","version":"2.0.0"})
    write(definition/"report.json",{"$schema":SCHEMA+"report/3.3.0/schema.json","themeCollection":{}})
    pages=build_pages()
    write(definition/"pages/pages.json",{"$schema":SCHEMA+"pagesMetadata/1.1.0/schema.json","pageOrder":[p[0] for p in pages],"activePageName":pages[0][0]})
    for name,title,visuals in pages:
        folder=definition/"pages"/name
        write(folder/"page.json",{"$schema":SCHEMA+"page/2.1.0/schema.json","name":name,"displayName":title,"displayOption":"FitToPage","width":1280,"height":800,
                                 "objects":{"background":[{"properties":{"color":fill("#F3F6F8"),"transparency":lit(0)}}]}})
        for v in visuals:write(folder/"visuals"/v["name"]/"visual.json",v)
