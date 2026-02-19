from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from retrain import retrain_model
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
GESTURE_MAP = "gesture_map.json"

@app.get("/")
def home():
    return FileResponse(os.path.join(frontend_path, "dashboard.html"))

@app.get("/gestures")
def get_gestures():
    if os.path.exists(GESTURE_MAP):
        mapping = json.load(open(GESTURE_MAP))
        return mapping
    return {}

@app.post("/save_gesture")
def save_gesture(data: dict):
    name = data["name"]
    action = data["action"]

    if os.path.exists(GESTURE_MAP):
        mapping = json.load(open(GESTURE_MAP))
    else:
        mapping = {}

    mapping[name] = action
    json.dump(mapping, open(GESTURE_MAP, "w"))

    return {"message": "Gesture saved", "map": mapping}

@app.post("/delete_gesture")
def delete_gesture(data: dict):
    name = data["name"]
    if os.path.exists(GESTURE_MAP):
        mapping = json.load(open(GESTURE_MAP))
        if name in mapping:
            del mapping[name]
            json.dump(mapping, open(GESTURE_MAP, "w"))

    return {"message": "Gesture deleted"}

@app.post("/retrain")
def trigger_retrain():
    try:
        retrain_model()
        return {"status": "training complete"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/status")
def get_status():
    try:
        if os.path.exists("status.json"):
            try:
                with open("status.json", "r") as f:
                    return json.load(f)
            except:
                return {"recording": False, "model_loaded": False}
        return {"recording": False, "model_loaded": False}
    except:
        return {"recording": False, "model_loaded": False}

@app.post("/start_recording")
def start_recording(data: dict):
    try:
        cmd = {
            "action": "start",
            "name": data["name"]
        }
        with open("recording_cmd.json", "w") as f:
            json.dump(cmd, f)
            
        return {"status": "recording command sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not start recording: {str(e)}")

@app.post("/system/start")
def start_camera():
    try:
        with open("recording_cmd.json", "w") as f:
            json.dump({"action": "start_camera"}, f)
        return {"status": "camera start command sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/system/stop")
def stop_camera():
    try:
        with open("recording_cmd.json", "w") as f:
            json.dump({"action": "stop_camera"}, f)
        return {"status": "camera stop command sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/system/mode")
def set_mode(data: dict):
    try:
        with open("recording_cmd.json", "w") as f:
            json.dump({"action": "set_mode", "mode": data.get("mode", "passive")}, f)
        return {"status": f"mode set to {data.get('mode')}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory=frontend_path), name="static")
