import pyautogui
import screen_brightness_control as sbc

def perform_action(action):
    try:
        if action == "pause":
            pyautogui.press("playpause") 
        
        elif action == "next_tab":
            pyautogui.hotkey("ctrl", "tab")
        
        elif action == "prev_tab":
            pyautogui.hotkey("ctrl", "shift", "tab")
        
        elif action == "volume_up":
            pyautogui.press("volumeup")
            
        elif action == "volume_down":
            pyautogui.press("volumedown")
            
        elif action == "scroll_up":
            pyautogui.scroll(300)
            
        elif action == "scroll_down":
            pyautogui.scroll(-300)

        elif action == "brightness_up":
            current = sbc.get_brightness()
            new_level = min(current[0] + 10, 100)
            sbc.set_brightness(new_level)
            
        elif action == "brightness_down":
            current = sbc.get_brightness()
            new_level = max(current[0] - 10, 0)
            sbc.set_brightness(new_level)
            
        elif action == "next_app":
            pyautogui.hotkey('alt', 'tab')
            
        print(f"Executed: {action}")
        
    except Exception as e:
        print(f"Error executing action {action}: {e}")
