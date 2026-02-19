Gesture Controlled Desktop System

This project is a gesture-based desktop control system that allows users to perform common computer actions using hand gestures captured through a webcam. The aim of the project is to create a more natural and customizable way to interact with a computer by combining computer vision, machine learning, and a web-based interface.

Features

Real-time hand gesture detection using a webcam

Machine learning based gesture recognition

Custom gesture recording and saving

One-click model retraining

Bootstrap-based web dashboard

Desktop automation such as media control and tab switching

Tech Stack

Frontend

HTML

Bootstrap

JavaScript

Backend

Python

FastAPI

Computer Vision and Machine Learning

OpenCV

MediaPipe

Scikit-learn (KNN Classifier)

Project Structure
Gesture_controlled_desktop/
│
├── backend/        # FastAPI server and detector logic
├── frontend/       # Dashboard UI
├── run_detector.py # Real-time gesture detection
└── README.md

How to Run the Project
Start Backend
cd backend
python -m uvicorn main:app --reload


Backend will run at:

http://127.0.0.1:8000

Start Gesture Detector

Open a new terminal:

cd backend
python run_detector.py


This will open the webcam window.

Start Frontend

Open another terminal:

cd frontend
python -m http.server 5500


Open the dashboard in browser:

http://127.0.0.1:5500/dashboard.html

How It Works

The webcam captures hand landmarks using MediaPipe.
A machine learning model identifies gestures from landmark data.
Recognized gestures trigger desktop actions such as pausing media or switching tabs.
Users can add new gestures through the dashboard and retrain the model when needed.

Learning Outcomes

Real-time computer vision integration

Machine learning model training and prediction

API communication between frontend and backend

Full-stack system development

Author

Muskaan
