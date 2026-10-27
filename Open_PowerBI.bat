@echo off
echo ===================================================
echo Launching RoadSafe GB in Microsoft Power BI Desktop
echo ===================================================

set "PBI_EXE=C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"

if exist "%~dp0powerbi\RoadSafe_GB.pbix" (
    if exist "%PBI_EXE%" (
        start "" "%PBI_EXE%" "%~dp0powerbi\RoadSafe_GB.pbix"
    ) else (
        start "" "%~dp0powerbi\RoadSafe_GB.pbix"
    )
) else if exist "%~dp0powerbi\RoadSafe_GB.pbip" (
    if exist "%PBI_EXE%" (
        start "" "%PBI_EXE%" "%~dp0powerbi\RoadSafe_GB.pbip"
    ) else (
        start "" "%~dp0powerbi\RoadSafe_GB.pbip"
    )
) else (
    echo Error: Could not find RoadSafe_GB.pbix or RoadSafe_GB.pbip in powerbi\ directory.
    pause
)
exit /b 0
