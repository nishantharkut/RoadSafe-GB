param([int]$Port = 0)
$ErrorActionPreference = 'Stop'
$reportRoot = Split-Path -Parent $PSScriptRoot
[void][System.Reflection.Assembly]::LoadFrom('C:/Program Files/Microsoft Power BI Desktop/bin/Microsoft.PowerBI.AdomdClient.dll')
if (-not $Port) {
    $reportDesktop = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'PBIDesktop.exe' -and $_.CommandLine -like '*RoadSafe_GB*' } | Select-Object -First 1
    if (-not $reportDesktop) { throw 'Open RoadSafe_GB in Power BI Desktop before running live validation.' }
    $reportEngine = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'msmdsrv.exe' -and $_.ParentProcessId -eq $reportDesktop.ProcessId } | Select-Object -First 1
    if (-not $reportEngine -or $reportEngine.CommandLine -notmatch '-s\s+"([^"]+)"') { throw 'Could not locate this report''s local Analysis Services workspace.' }
    $reportPortFile = Join-Path $Matches[1] 'msmdsrv.port.txt'
    $Port = [int]([regex]::Replace([System.IO.File]::ReadAllText($reportPortFile), '[^0-9]', ''))
}
$reportConnection = New-Object Microsoft.AnalysisServices.AdomdClient.AdomdConnection
$reportConnection.ConnectionString = "Data Source=localhost:$Port"
$reportConnection.Open()
function Invoke-ReportQuery([string]$Query) {
    $reportCommand = $reportConnection.CreateCommand()
    $reportCommand.CommandText = $Query
    $reportReader = $reportCommand.ExecuteReader()
    $reportRows = @()
    try {
        while ($reportReader.Read()) {
            $reportRow = [ordered]@{}
            for ($reportColumn = 0; $reportColumn -lt $reportReader.FieldCount; $reportColumn++) {
                $reportName = $reportReader.GetName($reportColumn)
                if ($reportName -match '\[([^\]]+)\]$') { $reportName = $Matches[1] }
                $reportRow[$reportName] = if ($reportReader.IsDBNull($reportColumn)) { $null } else { $reportReader.GetValue($reportColumn) }
            }
            $reportRows += [pscustomobject]$reportRow
        }
    } finally { $reportReader.Close() }
    return $reportRows
}
try {
    $reportTotals = @(Invoke-ReportQuery 'EVALUATE ROW("year", "all", "collisions", [Total Collisions], "severe", [Severe Collisions], "severe_share", [Severe Share], "casualties", [Total Casualties], "vehicles", [Total Vehicles], "grid_collisions", [Grid Collisions])')
    $reportYears = @(Invoke-ReportQuery 'EVALUATE SUMMARIZECOLUMNS(dim_calendar[year], "collisions", [Total Collisions], "severe", [Severe Collisions], "severe_share", [Severe Share], "casualties", [Total Casualties], "vehicles", [Total Vehicles], "grid_collisions", [Grid Collisions]) ORDER BY dim_calendar[year]')
    $reportExpected = Get-Content (Join-Path $reportRoot 'docs/report_evidence/powerbi_expected_totals.json') -Raw | ConvertFrom-Json
    foreach ($expected in $reportExpected) {
        $actual = @($reportTotals + $reportYears | Where-Object { [string]$_.year -eq [string]$expected.year })
        if ($actual.Count -ne 1) { throw "Missing or duplicate result for year $($expected.year)." }
        foreach ($metric in @('collisions','severe','casualties','vehicles')) {
            if ($actual[0].$metric -ne $expected.$metric) { throw "$metric mismatch for $($expected.year): $($actual[0].$metric) != $($expected.$metric)" }
        }
        if ([math]::Abs($actual[0].severe_share - $expected.severe_share) -gt 0.0000000001) { throw "Severity share mismatch for $($expected.year)." }
    }
    # The saved spatial export deliberately retains grid/year groups with >=5
    # collisions, so its denominator differs from all coordinate-valid records.
    $reportGrid = Import-Csv (Join-Path $reportRoot 'powerbi/exports/agg_hotspots_grid.csv')
    $reportGridTotal = ($reportGrid | Measure-Object -Property total_collisions -Sum).Sum
    if ($reportTotals[0].grid_collisions -ne $reportGridTotal) { throw 'Spatial measure does not match the actual grid export.' }
    foreach ($yearRow in $reportYears) {
        $yearGridTotal = ($reportGrid | Where-Object { [int]$_.collision_year -eq [int]$yearRow.year } | Measure-Object -Property total_collisions -Sum).Sum
        if ($yearRow.grid_collisions -ne $yearGridTotal) { throw "Spatial year filter failed for $($yearRow.year)." }
    }
    $reportFiltered = @(Invoke-ReportQuery 'EVALUATE CALCULATETABLE(ROW("collisions", [Total Collisions], "severe", [Severe Collisions], "share", [Severe Share]), fact_collisions[severity] = "Slight")')
    if ($reportFiltered[0].collisions -ne 150739 -or $reportFiltered[0].severe -ne 0 -or $reportFiltered[0].share -ne 0) { throw 'Severity selection does not propagate correctly to the headline measures.' }
    $reportMonday = @(Invoke-ReportQuery 'EVALUATE CALCULATETABLE(ROW("weekend_share", [Weekend Severe Share], "weekday_share", [Weekday Severe Share], "gap", [Weekend Difference pp]), fact_collisions[day_of_week_name] = "Monday")')
    if ($null -ne $reportMonday[0].weekend_share -or $null -eq $reportMonday[0].weekday_share -or $null -ne $reportMonday[0].gap) { throw 'A Monday-only selection must not report a weekend comparison without weekend observations.' }
    $reportResult = [ordered]@{ captured_at = (Get-Date).ToUniversalTime().ToString('o'); source = 'Live Power BI Desktop Analysis Services model'; totals = $reportTotals; years = $reportYears; slight_filter = $reportFiltered; monday_only = $reportMonday; result = 'passed' }
    $reportResult | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $reportRoot 'docs/report_evidence/powerbi_live_validation.json') -Encoding UTF8
    $reportResult | ConvertTo-Json -Depth 8
} finally { $reportConnection.Close() }
