@echo off
title BhagvadMood Journal - Desktop Application
echo ==============================================================================
echo Launching BhagvadMood Journal (Desktop UI)...
echo ==============================================================================

if exist "Scripts\python.exe" (
    echo Using Virtual Environment Python...
    if exist "gui_desktop\Main.py" (
        Scripts\python.exe gui_desktop\Main.py
    ) else (
        Scripts\python.exe Main.py
    )
) else (
    echo Using System Python...
    if exist "gui_desktop\Main.py" (
        python gui_desktop\Main.py
    ) else (
        python Main.py
    )
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    pause
)
