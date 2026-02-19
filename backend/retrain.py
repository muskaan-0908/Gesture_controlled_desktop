import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import json

def retrain_model():
    X = []
    y = []

    if not os.path.exists("dataset"):
        print("No dataset folder found.")
        return

    valid_gestures = set()
    if os.path.exists("gesture_map.json"):
        try:
            with open("gesture_map.json", "r") as f:
                 valid_gestures = set(json.load(f).keys())
        except:
             pass

    for gesture in os.listdir("dataset"):
        if gesture not in valid_gestures:
            print(f"Skipping {gesture} (not in map)")
            continue

        folder = f"dataset/{gesture}"

        for file in os.listdir(folder):
            try:
                data = np.load(f"{folder}/{file}")
                for sample in data:
                    X.append(sample)
                    y.append(gesture)
            except Exception as e:
                print(f"Error loading {file}: {e}")

    if not X:
        print("No data to train on.")
        return

    print(f"Training on {len(X)} samples...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X,y)

    joblib.dump(model,"model.pkl")
    print("Model saved")
