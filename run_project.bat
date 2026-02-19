@echo off
echo Starting Gesture Control System...
cd backend
pip install fastapi uvicorn opencv-python mediapipe joblib scikit-learn pyautogui
start http://127.0.0.1:8000
python -m uvicorn main:app --reload
pause
