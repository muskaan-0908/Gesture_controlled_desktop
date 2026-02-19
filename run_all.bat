@echo off
echo Starting Gesture Control Hub...

cd backend

start "Gesture Backend API" python -m uvicorn main:app --reload

timeout /t 3 /nobreak >nul

start "Gesture Detector" python run_detector.py

start http://127.0.0.1:8000

echo System started successfully!
echo Close the "Gesture Backend API" and "Gesture Detector" windows to stop.
pause
