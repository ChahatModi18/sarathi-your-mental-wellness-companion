@echo off
title BhagvadMood Journal - Desktop Application
cd /d "%~dp0"
echo ==============================================================================
echo Launching BhagvadMood Journal (Desktop UI)...
echo ==============================================================================

if exist "..\Scripts\python.exe" (
    echo Using Virtual Environment Python...
    ..\Scripts\python.exe Main.py
) else (
    echo Using System Python...
    python Main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application exited with error code %ERRORLEVEL%.
    pause
)

