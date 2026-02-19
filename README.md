# Gesture Controlled Desktop System

## Overview

Gesture Controlled Desktop System is a real-time computer vision application that allows users to control desktop actions using hand gestures captured through a webcam. The system combines MediaPipe-based hand tracking with a Random Forest machine learning model to recognize gestures and trigger desktop automation tasks.

The project focuses on creating a customizable and user-friendly interaction system where users can record their own gestures, retrain the model, and control applications without traditional input devices.

---

## Features

- Real-time hand landmark detection using MediaPipe
- Gesture classification using Random Forest
- Custom gesture recording through a web dashboard
- One-click retraining workflow
- Bootstrap-based user interface
- FastAPI backend for communication
- Desktop automation using gesture recognition
- Modular architecture separating UI, backend, and detector

---

## Tech Stack

### Frontend
- HTML
- Bootstrap
- JavaScript

### Backend
- Python
- FastAPI

### Computer Vision and Machine Learning
- OpenCV
- MediaPipe
- Scikit-learn (Random Forest Classifier)

### Automation
- PyAutoGUI

---

## Project Architecture

The system consists of three main components:

### Gesture Detector
Captures webcam frames, extracts hand landmarks using MediaPipe, and predicts gestures using a trained Random Forest model.

### Backend Server (FastAPI)
Handles API requests from the dashboard, manages gesture recording signals, and coordinates retraining.

### Web Dashboard
Allows users to:
- Add custom gestures
- Start recording
- Retrain the model
- Monitor system status

---

## Project Structure

Gesture_controlled_desktop/
│
├── backend/
│ ├── main.py
│ ├── run_detector.py
│ ├── gesture_model.py
│ ├── retrain.py
│ ├── actions.py
│ └── recording.json
│
├── frontend/
│ ├── dashboard.html
│ ├── script.js
│ └── style.css
│
└── README.md


---

## Installation

Clone the repository:

git clone https://github.com/muskaan-0908/Gesture_controlled_desktop.git
cd Gesture_controlled_desktop


Install required libraries:

pip install fastapi uvicorn opencv-python mediapipe numpy scikit-learn pyautogui joblib


---

## Running the Project

### Start Backend Server

cd backend
python -m uvicorn main:app --reload


Backend runs at:

http://127.0.0.1:8000


---

### Start Gesture Detector

Open a new terminal:

cd backend
python run_detector.py


This opens the webcam window and begins gesture monitoring.

---

### Start Frontend Dashboard

Open another terminal:

cd frontend
python -m http.server 5500


Open in browser:

http://127.0.0.1:5500/dashboard.html


---

## Workflow

1. Open the dashboard interface.
2. Enter a gesture name and start recording.
3. Perform the gesture in front of the webcam.
4. Retrain the Random Forest model.
5. Use gestures to control desktop actions.

---

## Concepts Demonstrated

- Real-time computer vision processing
- Gesture-based human-computer interaction
- Random Forest machine learning classification
- API communication between frontend and backend
- Modular system design

---

## Author

Muskaan
