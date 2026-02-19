import cv2
import mediapipe as mp
import numpy as np
import os
import joblib
import json
import time
import datetime
from actions import perform_action
from gesture_model import extract_landmarks
import logging
from collections import deque

logging.basicConfig(filename='detector_debug.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

RECORDING = False
CURRENT_GESTURE = None
GESTURE_MAP = {}
model = None
samples = []
action_log = deque(maxlen=5)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

def load_mapping():
    global GESTURE_MAP
    try:
        if os.path.exists("gesture_map.json"):
            with open("gesture_map.json", "r") as f:
                GESTURE_MAP = json.load(f)
            print(f"Mapping loaded: {len(GESTURE_MAP)} gestures")
    except Exception as e:
        print(f"Error loading mapping: {e}")

def load_model():
    global model
    try:
        if os.path.exists("model.pkl"):
            model = joblib.load("model.pkl")
            print("Model loaded")
        else:
            model = None
            print("Model file not found")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None

def start_detector():
    global RECORDING, CURRENT_GESTURE, samples
    
    print("Detector started... Waiting for command.")
    
    load_mapping()
    load_model()
    
    last_map_update = os.path.getmtime("gesture_map.json") if os.path.exists("gesture_map.json") else 0
    last_model_update = os.path.getmtime("model.pkl") if os.path.exists("model.pkl") else 0

    CAMERA_ON = False
    CONTROL_ACTIVE = False
    
    cap = None
    last_check_time = 0
    last_status_time = 0
    check_interval = 0.5
    
    REC_INTERVAL = 0.25
    REC_LIMIT = 60
    last_sample_time = 0

    history_x = deque(maxlen=10)
    last_swipe_time = 0
    SWIPE_COOLDOWN = 1.0
    SWIPE_THRESH = 0.3

    hands = mp_hands.Hands(max_num_hands=1)

    def open_camera():
        logging.info("Attempting to open Camera 0 (DSHOW)...")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            logging.info("Camera 0 (DSHOW) opened successfully.")
            return cap
        
        logging.info("Retrying Camera 0 (Default)...")
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            logging.info("Camera 0 (Default) opened successfully.")
            return cap

        logging.info("Attempting to open Camera 1...")
        cap = cv2.VideoCapture(1)
        if cap.isOpened():
            logging.info("Camera 1 opened successfully.")
            return cap
            
        logging.error("Failed to open any camera.")
        return None

    while True:
        current_time = time.time()
        if current_time - last_check_time > check_interval:
            last_check_time = current_time
            
            if os.path.exists("recording_cmd.json"):
                try:
                    with open("recording_cmd.json", "r") as f:
                        cmd = json.load(f)
                    os.remove("recording_cmd.json")
                    
                    action = cmd.get("action")
                    if action == "start_camera":
                        logging.info("Received command: START_CAMERA")
                        CAMERA_ON = True
                        if cap is None or not cap.isOpened():
                            cap = open_camera()
                            if cap is None:
                                logging.error("Could not open camera on START command.")
                                print("ERROR: Could not open any camera.")
                                CAMERA_ON = False
                            else:
                                print("Camera Started")
                        
                    elif action == "stop_camera":
                        logging.info("Received command: STOP_CAMERA")
                        CAMERA_ON = False
                        if cap is not None:
                            cap.release()
                            cap = None
                        cv2.destroyAllWindows()
                        print("Camera Stopped")
                        
                    elif action == "set_mode":
                        mode = cmd.get("mode")
                        CONTROL_ACTIVE = (mode == "control")
                        print(f"Control Mode: {CONTROL_ACTIVE}")
                        
                    elif action == "start":
                        if not CAMERA_ON:
                            print("Auto-starting camera for recording...")
                            CAMERA_ON = True
                            if cap is None or not cap.isOpened():
                                cap = open_camera()
                                time.sleep(1.0)
                                if cap is None or not cap.isOpened():
                                    print("ERROR: Camera failed to auto-start!")
                                    CAMERA_ON = False
                                else:
                                    print("Camera auto-started successfully.")
                        
                        if CAMERA_ON:
                            RECORDING = True
                            CURRENT_GESTURE = cmd.get("name")
                            print(f"Command received: Start recording {CURRENT_GESTURE}")
                        else:
                            print("Recording aborted due to camera failure.")

                except Exception as e:
                    print(f"Error reading command: {e}")

            if not CAMERA_ON:
                try:
                    status = {
                        "recording": False,
                        "current_gesture": None,
                        "confidence": 0.0,
                        "model_loaded": model is not None,
                        "camera_on": False,
                        "control_active": CONTROL_ACTIVE,
                        "last_update": str(datetime.datetime.now()),
                        "action_log": list(action_log)
                    }
                    with open("status.json", "w") as f:
                        json.dump(status, f)
                except:
                    pass
            
            try:
                if os.path.exists("gesture_map.json"):
                    mtime = os.path.getmtime("gesture_map.json")
                    if mtime > last_map_update:
                        load_mapping()
                        last_map_update = mtime
                        
                if os.path.exists("model.pkl"):
                    mtime = os.path.getmtime("model.pkl")
                    if mtime > last_model_update:
                        load_model()
                        last_model_update = mtime
            except:
                pass

        if CAMERA_ON and cap is not None:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame from camera.")
                time.sleep(0.1)
                continue

            lm = None
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.multi_hand_landmarks:
                 lm_list = []
                 for point in results.multi_hand_landmarks[0].landmark:
                     lm_list.extend([point.x, point.y])
                 lm = np.array(lm_list)

            if RECORDING and CURRENT_GESTURE:
                if lm is not None:
                    mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
                    
                    if not hasattr(start_detector, "rec_start_time"):
                        start_detector.rec_start_time = time.time()
                        start_detector.timestamps = []
                        last_sample_time = 0
                    
                    current_time = time.time()
                    if current_time - last_sample_time >= REC_INTERVAL:
                        samples.append(lm)
                        last_sample_time = current_time
                        start_detector.timestamps.append(current_time)
                        
                        cv2.circle(frame, (50, 50), 20, (0, 255, 0), -1) 

                    progress = len(samples) / REC_LIMIT
                    bar_width = 400
                    cv2.rectangle(frame, (50, 400), (50 + bar_width, 420), (50, 50, 50), -1)
                    cv2.rectangle(frame, (50, 400), (50 + int(bar_width * progress), 420), (0, 255, 0), -1)

                    cv2.putText(frame, f"RECORDING: {CURRENT_GESTURE} ({len(samples)}/{REC_LIMIT})", (50,380),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    if len(samples) >= REC_LIMIT:
                        path = f"dataset/{CURRENT_GESTURE}"
                        os.makedirs(path, exist_ok=True)
                        
                        sample_id = len([f for f in os.listdir(path) if f.endswith('.npy')])
                        np.save(f"{path}/sample_{sample_id}.npy", np.array(samples))
                        
                        duration = time.time() - start_detector.rec_start_time
                        meta = {
                            "gesture": CURRENT_GESTURE,
                            "frames": len(samples),
                            "duration_seconds": duration,
                            "timestamps": start_detector.timestamps,
                            "created_at": str(datetime.datetime.now())
                        }
                        with open(f"{path}/meta_{sample_id}.json", "w") as f:
                            json.dump(meta, f)

                        print(f"Recording Saved for {CURRENT_GESTURE} (Duration: {duration:.2f}s)")
                        
                        RECORDING = False
                        samples = []
                        if hasattr(start_detector, "rec_start_time"):
                            del start_detector.rec_start_time
                            del start_detector.timestamps
            
            elif model is not None and lm is not None:
                if results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
                    
                    wrist_x = results.multi_hand_landmarks[0].landmark[0].x
                    history_x.append(wrist_x)
                    
                    swipe_detected = False
                    if len(history_x) >= 10 and (time.time() - last_swipe_time > SWIPE_COOLDOWN):
                        delta = history_x[-1] - history_x[0]
                        
                        if delta < -SWIPE_THRESH:
                            print("Swipe Left -> Next Tab")
                            perform_action("next_tab")
                            action_log.append({
                                "name": "next_tab (Swipe)",
                                "time": str(datetime.datetime.now().strftime("%H:%M:%S")),
                                "timestamp": time.time()
                            })
                            last_swipe_time = time.time()
                            history_x.clear()
                            swipe_detected = True
                            cv2.putText(frame, "SWIPE LEFT", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                        elif delta > SWIPE_THRESH:
                            print("Swipe Right -> Prev Tab")
                            perform_action("prev_tab")
                            action_log.append({
                                "name": "prev_tab (Swipe)",
                                "time": str(datetime.datetime.now().strftime("%H:%M:%S")),
                                "timestamp": time.time()
                            })
                            last_swipe_time = time.time()
                            history_x.clear()
                            swipe_detected = True
                            cv2.putText(frame, "SWIPE RIGHT", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                        try:
                             status = {
                                "recording": RECORDING,
                                "current_gesture": "Swipe Left" if delta < 0 else "Swipe Right", 
                                "confidence": 1.0,
                                "model_loaded": True,
                                "camera_on": True,
                                "control_active": CONTROL_ACTIVE,
                                "last_update": str(datetime.datetime.now()),
                                "action_log": list(action_log)
                            }
                             with open("status.json", "w") as f:
                                json.dump(status, f)
                             last_status_time = time.time()
                        except:
                            pass

                    if swipe_detected:
                         cv2.imshow("CAMERA WINDOW", frame)
                         if cv2.waitKey(1) == 27: break
                         continue

                try:
                    gesture = model.predict([lm])[0]
                    probs = model.predict_proba([lm])[0]
                    confidence = max(probs)
                    
                    if gesture in GESTURE_MAP:
                        action = GESTURE_MAP.get(gesture)
                        
                        display_text = f"Gesture: {gesture} ({confidence:.2f})"
                        color = (0, 255, 255)
                        
                        try:
                            status = {
                                "recording": RECORDING,
                                "current_gesture": gesture if confidence > 0.6 else None, 
                                "confidence": float(confidence),
                                "model_loaded": True,
                                "camera_on": True,
                                "control_active": CONTROL_ACTIVE,
                                "last_update": str(datetime.datetime.now()),
                                "action_log": list(action_log)
                            }

                            if time.time() - last_status_time > 0.2: 
                                 with open("status.json", "w") as f:
                                    json.dump(status, f)
                                 last_status_time = time.time()
                        except:
                            pass
                        
                        if CONTROL_ACTIVE and action and not RECORDING and confidence > 0.7:
                            display_text += f" -> {action}"
                            color = (0, 255, 0)
                            perform_action(action)
                            action_log.append({
                                "name": action,
                                "time": str(datetime.datetime.now().strftime("%H:%M:%S")),
                                "timestamp": time.time()
                            })
                        elif not CONTROL_ACTIVE:
                            display_text += " (Passive)"
                        
                        cv2.putText(frame, display_text, (20,50),
                                    cv2.FONT_HERSHEY_SIMPLEX,1,color,2)
                    else:
                        pass

                except Exception as e:
                    pass

            cv2.imshow("CAMERA WINDOW", frame)
            if cv2.waitKey(1) == 27:
                break
        else:
            time.sleep(0.1)

    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    start_detector()
