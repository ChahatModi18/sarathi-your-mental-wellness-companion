@echo off
title BhagvadMood Journal - Web Application (Flask)
echo ==============================================================================
echo Launching BhagvadMood Web Platform on http://127.0.0.1:5000...
echo ==============================================================================

if exist "Scripts\python.exe" (
    echo Using Virtual Environment Python...
    if exist "backend\app.py" (
        Scripts\python.exe backend\app.py
    ) else (
        Scripts\python.exe app.py
    )
) else (
    echo Using System Python...
    if exist "backend\app.py" (
        python backend\app.py
    ) else (
        python app.py
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Web server failed to start or crashed with error %ERRORLEVEL%.
    pause
)
