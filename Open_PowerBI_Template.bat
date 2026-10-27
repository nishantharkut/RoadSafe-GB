@echo off
echo ===================================================
echo Launching RoadSafe GB Template in Power BI Desktop
echo ===================================================

set "PBI_EXE=C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"

if exist "%~dp0powerbi\RoadSafe_GB.pbit" (
    if exist "%PBI_EXE%" (
        start "" "%PBI_EXE%" "%~dp0powerbi\RoadSafe_GB.pbit"
    ) else (
        start "" "%~dp0powerbi\RoadSafe_GB.pbit"
    )
) else (
    echo Error: Could not find RoadSafe_GB.pbit in powerbi\ directory.
    pause
)
exit /b 0
