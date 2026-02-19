# Gesture Controlled Desktop System

## Overview

The Gesture Controlled Desktop System is a computer vision based application that allows users to control desktop functions using hand gestures captured through a webcam. The system combines real-time gesture recognition with a web-based dashboard that enables users to add, manage, and retrain custom gestures.

The objective of this project is to provide a more intuitive and accessible method of human-computer interaction by integrating machine learning, desktop automation, and a user-friendly interface.

---

## Key Features

- Real-time hand gesture detection using webcam input  
- Customizable gesture recording and management  
- Machine learning based gesture classification  
- One-click model retraining from the dashboard  
- Bootstrap-based web interface for user interaction  
- Desktop automation including media control and navigation shortcuts  

---

## Technology Stack

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
- Scikit-learn (K-Nearest Neighbors Classifier)

---

## Project Architecture

The system is divided into three main components:

1. Gesture Detector  
   Captures webcam input, extracts hand landmarks using MediaPipe, and predicts gestures using a trained machine learning model.

2. Backend API (FastAPI)  
   Handles communication between the frontend dashboard and the detector, manages recording requests, and controls model retraining.

3. Web Dashboard  
   Provides a user interface to add gestures, start recording, retrain the model, and monitor system status.

---

## Project Structure

Gesture_controlled_desktop/
│
├── backend/
│ ├── main.py
│ ├── run_detector.py
│ ├── actions.py
│ ├── retrain.py
│ └── dataset/
│
├── frontend/
│ ├── dashboard.html
│ ├── script.js
│ └── style.css
│
└── README.md


---

## Setup and Installation

### Clone the Repository

git clone https://github.com/muskaan-0908/Gesture_controlled_desktop.git
cd Gesture_controlled_desktop


### Install Dependencies

pip install fastapi uvicorn opencv-python mediapipe numpy scikit-learn joblib


---

## Running the Project

### Start the Backend Server

cd backend
python -m uvicorn main:app --reload


Backend will be available at:

http://127.0.0.1:8000


### Start the Gesture Detector

Open a new terminal:

cd backend
python run_detector.py


This will launch the webcam window.

### Start the Frontend Dashboard

Open another terminal:

cd frontend
python -m http.server 5500


Open the dashboard in your browser:

http://127.0.0.1:5500/dashboard.html


---

## Workflow

1. Open the dashboard interface.
2. Add a new gesture name and start recording.
3. Perform the gesture in front of the webcam.
4. Retrain the model using the dashboard.
5. Use gestures to control desktop actions in real time.

---

## Learning Outcomes

- Understanding of real-time computer vision pipelines
- Integration of machine learning models into interactive systems
- Backend API development using FastAPI
- Frontend and backend communication using REST APIs
- Designing user-focused interfaces for AI applications

---

## Author

Muskaan
