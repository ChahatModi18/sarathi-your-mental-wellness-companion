@echo off
title BhagvadMood AI Microservice (FastAPI + Uvicorn)
echo ==============================================================================
echo Launching BhagvadMood FastAPI AI Microservice on http://127.0.0.1:8000...
echo Swagger Interactive API Documentation: http://127.0.0.1:8000/docs
echo ReDoc Documentation: http://127.0.0.1:8000/redoc
echo ==============================================================================

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python -c "import uvicorn, fastapi" >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Using System Python (FastAPI + Uvicorn detected)...
        python -m uvicorn backend.fastapi_app:app --host 127.0.0.1 --port 8000 --reload
        goto done
    )
)

if exist "Scripts\python.exe" (
    echo Using Virtual Environment Python...
    Scripts\python.exe -m uvicorn backend.fastapi_app:app --host 127.0.0.1 --port 8000 --reload
    goto done
)

python -m uvicorn backend.fastapi_app:app --host 127.0.0.1 --port 8000 --reload

:done
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] FastAPI server failed to start with code %ERRORLEVEL%.
    pause
)
