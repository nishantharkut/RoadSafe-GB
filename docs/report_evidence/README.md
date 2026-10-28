# Report evidence

Prepared on 28 October 2026 for Nishant Harkut, 2023IMG-040, IMG (Integrated B.Tech + MBA).

The report's maintained source is [BDM_Project_Report.tex](../BDM_Project_Report.tex). The PDF is compiled with MiKTeX. Word and Markdown are exported from the same source; the Word tables are native editable tables, and its equations are Office math. The previous documents, generators and figures are preserved in [the archive](../archive/report_before_revision/).

## Evidence files

- `verified_metrics.json`: calculations from the saved Power BI CSV exports, including input hashes, year counts, severity counts, combinations, rush-hour calculations and distinct grid identifiers.
- `index_benchmarks_verified.json`: a fresh, read-only MongoDB benchmark. It records five timing samples for each of three queries under each access path, the query predicates, returned row counts, examined keys/documents and actual winning plans. These timings differ from the earlier saved application benchmark.
- `live_api_observations.json`: responses from the running application during preparation, including its current incorrect combination ratios. It is evidence of observed application behaviour, not the source of the report's corrected ratios.
- `screenshot_manifest.json`: hashes of actual web and desktop captures, plus the source coordinates of the two cropped screenshots. Cropping removes surrounding interface space without changing displayed values. Charts and the architecture diagram are generated figures and are labelled accordingly.
- `powerbi_live_validation.json`: live DAX results from the completed imported model, including totals for both years, each year individually, grid totals and a Slight-severity selection.
- `powerbi_slicer_validation.json`: values observed after actual 2024, 2025 and all-year selections in the Desktop interface.
- `powerbi_schema_validation.json`: Microsoft's report validator output, with zero errors and warnings.
- `powerbi_captures/` and `powerbi_capture_crops.json`: original captures of the three populated Desktop pages and the coordinates used to crop away the editor's empty filter pane.

## Checks performed

- The live database contained 202,452 collisions, 183,948 vehicles and 127,883 casualties.
- The collision export contained no duplicate collision identifiers. Its counts and severity totals matched the live Overview response.
- `.venv\Scripts\python.exe -m pytest backend/tests/test_api.py -q`: **10 passed**.
- `npm run build` in `frontend`: completed successfully, with Vite's existing large-bundle warning.
- The LaTeX output was rendered and visually inspected, with no overfull boxes or undefined-reference warnings in the final compilation log.
- The Word document was opened in a separate Microsoft Word automation instance, its contents field updated, and its rendered PDF inspected.
- Four Power BI regression checks pass. The live imported model and actual year slicer match the source CSV totals. The populated PBIP was reopened without another refresh, and a native PBIX with data was saved.
- An independent code review caught an empty-denominator comparison edge case. The live validation was extended to fail on the original Monday-only result, then passed after the weekend-difference measure was guarded against missing weekday or weekend groups. The corrected measure is saved in the PBIX, PBIT, BIM and generator.

## Implementation findings reflected in the report

1. The original five web images all showed Overview because the application switches tabs through React state rather than URL routes. Fresh captures use the actual tab controls.
2. The combination endpoint compares a Boolean field to numeric `1`. The live database stores Booleans: querying `true` finds 51,713 severe collisions; querying `1` finds none. The report recalculates its ratios independently.
3. The scenario comparator queries both years regardless of the selected page year. Its screenshot and interpretation explicitly use both years.
4. Power BI was subsequently completed at the user's request: the conflicting legacy report was replaced by three bound PBIR pages, CSV paths corrected, the date relationship added, and 19 measures verified. The report now uses actual populated dashboards; the prior blank capture is archived.
5. The vehicle/casualty export contains collision-level co-occurrence pairs, not unique casualties. Its 240,830 pair count must not be used as a casualty total.
6. The forced spatial index benchmark uses unbounded index bounds and is slower than the collection scan. The report preserves this negative result.

The web application code remains unchanged. The Power BI model and report were repaired as explicitly requested. Original Power BI files are preserved in `docs/archive/powerbi_before_completion/`.

## Rebuild

Install the Python packages in `etl/requirements-report.txt`, plus Pandoc and MiKTeX, then run from the project root:

```powershell
.venv\Scripts\python.exe etl\generate_report_assets.py
.venv\Scripts\python.exe etl\generate_latex_report.py
```

The generator checks that the Word export contains seven tables and twelve figures and that the PDF contains the correct personal details. It writes the PDF to both `docs/BDM_Project_Report.pdf` and `output/pdf/BDM_Project_Report.pdf`. Screenshots and database timing samples are retained observations; rebuilding charts does not fabricate new captures or timing results.
