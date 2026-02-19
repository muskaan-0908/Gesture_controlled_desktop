import cv2
import time

print("--- CAMERA DIAGNOSTICS ---")

def test_camera(index, backend_name, backend_id):
    print(f"\nTesting Camera {index} with {backend_name}...")
    try:
        if backend_id is not None:
            cap = cv2.VideoCapture(index, backend_id)
        else:
            cap = cv2.VideoCapture(index)
            
        if not cap.isOpened():
            print(f"FAILED: Could not open camera {index}.")
            return False
            
        ret, frame = cap.read()
        if not ret:
            print(f"FAILED: Opened but could not read frame.")
            cap.release()
            return False
            
        print(f"SUCCESS: Camera {index} working! Resolution: {frame.shape[1]}x{frame.shape[0]}")
        cap.release()
        return True
    except Exception as e:
        print(f"ERROR: Exception while testing: {e}")
        return False

# Test cases
test_camera(0, "DSHOW", cv2.CAP_DSHOW)
test_camera(0, "DEFAULT", None)
test_camera(1, "DEFAULT", None)

print("\n--- END DIAGNOSTICS ---")
