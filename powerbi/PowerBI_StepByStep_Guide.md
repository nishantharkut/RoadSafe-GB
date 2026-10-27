# RoadSafe GB: using the completed Power BI report

Open **`RoadSafe_GB.pbix`** in Microsoft Power BI Desktop, or double-click **`Open_PowerBI.bat`** in the project root. The PBIX includes the imported data; you do not need to run MongoDB, Flask, React or a CSV refresh to view it.

## Pages

1. **Collision overview:** collision, severity, casualty and vehicle KPIs; monthly comparisons; severity composition; urban/rural volume; annual totals.
2. **Time and place:** hourly and weekday distributions; weekend/weekday severity comparison; geographic grid bubbles positioned by longitude and latitude.
3. **Conditions and severity:** severity shares by posted speed limit, lighting and weather, plus the counts behind the speed-limit percentages.

Use the **YEAR** dropdown on each page to select 2024, 2025 or both. Selected years have checked boxes; clear the selection to include all years. You can also click chart categories to filter other visuals, and click the selected category again to clear that selection. Year selections are local to each page.

## Expected totals

| Selection | Collisions | Fatal or serious | Severe share | Casualties | Vehicles |
|---|---:|---:|---:|---:|---:|
| Both years | 202,452 | 51,713 | 25.54% | 256,155 | 367,462 |
| 2024 | 100,927 | 25,069 | 24.84% | 128,272 | 183,514 |
| 2025 | 101,525 | 26,644 | 26.24% | 127,883 | 183,948 |

Counts may use Indian digit grouping in Desktop depending on your regional settings; `2,02,452` and `202,452` are the same value.

The geographic export retains grid/year groups with at least five collisions. Its total is 198,975 collisions, so its denominator differs from the headline collision count. The geographic chart is a plot of coordinates rather than a basemap; it needs no external map service.

The weekend difference is blank when the selected filters remove either the weekday or weekend comparison group. Geographic bubbles respond to the year selection; hourly and weekday chart selections filter the temporal panels rather than recomputing the pre-aggregated geographic export.

## Editing and refreshing

- **PBIX:** the main ready-to-open report, including data.
- **PBIP and its `.Report` / `.SemanticModel` folders:** the editable project, also saved with a populated local cache.
- **PBIT:** a native template exported from the completed report. It contains definitions but requires a data refresh when creating a new report.

CSV sources are under `powerbi/exports/`. If you move them, update the `File.Contents` paths in Power Query before refreshing. The model uses one active relationship from `fact_collisions[date]` to `dim_calendar[date]`. Spatial measures explicitly apply selected calendar years with `TREATAS`.

Three supporting aggregate tables are hidden because the visible report does not use them. In particular, the collision-level vehicle/casualty cross-product is not a unique-casualty source and is excluded from all casualty KPIs.

## Verification and regeneration

The project has four regression checks, passes Microsoft's report validator with zero errors and warnings, and was tested in Desktop through live DAX queries and actual year-slicer selections. The PBIP was closed and reopened to confirm that its imported data persists.

```powershell
.venv\Scripts\python.exe -m pytest etl/tests/test_powerbi_project.py -q
powershell -NoProfile -ExecutionPolicy Bypass -File etl/verify_powerbi.ps1
```

The live check requires the report to be open in Desktop. Its results, expected totals, schema-validation output and original page captures are stored under `docs/report_evidence/`.

`etl/generate_powerbi_project.py` rebuilds the PBIP definitions from the saved CSV exports. It does not generate a populated PBIX or native PBIT; after regenerating definitions, open the project in Desktop, refresh when needed, verify and save. Preserve the current working PBIX before replacing it.
