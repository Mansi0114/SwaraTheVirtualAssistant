# =====================================================
# IMPORTS
# =====================================================
import os
import webbrowser
import pyautogui
import subprocess
import time
import re
import requests
import threading
import winsound
import psutil
import shutil

from .memory_db import set_memory, get_memory, clear_memory

from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from swara_core.volume_control import (
    increase_volume, decrease_volume, mute_volume, set_volume
)
from swara_core.email_service import send_email, compose_email_draft



# =====================================================
# GLOBAL STATES
# =====================================================
ACTIVE_REMINDER = {"active": False}
ACTIVE_ALARMS = []

# =====================================================
# MAIN COMMAND ROUTER
# =====================================================
def perform_task(command, stop_event=None):
    cmd = command.lower().strip()
    print(f"[TASK] Processing command: '{cmd}'")

    # ---------------- STOP HANDLING ----------------
    if stop_event and stop_event.is_set():
        stop_event.clear()

    if cmd in ["stop", "exit", "cancel"]:
        if stop_event:
            stop_event.set()
        return "Stopped."
    if "who made you" in cmd or "who created you" in cmd:
        return "I was built by Mansi Kulkarni."
        # ---------------- SQLITE MEMORY: STORE NAME ----------------
    if cmd.startswith("my name is"):
        name = cmd.replace("my name is", "").strip()
        if name:
            set_memory("name", name)
            return f"Okay, I will remember your name is {name}"

    # ---------------- SQLITE MEMORY: READ NAME ----------------
    if cmd in ["what is my name", "tell me my name"]:
        name = get_memory("name")
        if name:
            return f"Your name is {name}"
        return "I don't know your name yet."

    # ---------------- SQLITE MEMORY: CLEAR ----------------
    if cmd in ["forget everything", "clear memory"]:
        clear_memory()
        return "I have forgotten everything."

    
    # ---------------- TIME & DATE ----------------
    if "time" in cmd:
        return f"The time is {datetime.now().strftime('%I:%M %p')}."

    if "date" in cmd or "today" in cmd:
        return f"Today's date is {datetime.now().strftime('%A, %d %B %Y')}."

    # ---------------- CUT / COPY / PASTE ----------------
    if "select all" in cmd:
        pyautogui.hotkey("ctrl", "a")
        return "Selected all."

    if "copy" in cmd:
        pyautogui.hotkey("ctrl", "c")
        return "Copied."

    if "cut" in cmd:
        pyautogui.hotkey("ctrl", "x")
        return "Cut."

    if "paste" in cmd:
        pyautogui.hotkey("ctrl", "v")
        return "Pasted."

    # ---------------- BATTERY ----------------
    if "battery" in cmd:
        return _get_battery_status()

    # ---------------- ALARM ----------------
    if "set alarm" in cmd or ("alarm" in cmd and "at" in cmd):
        return _handle_alarm(cmd)

    if "cancel alarm" in cmd or "delete alarm" in cmd or "stop alarm" in cmd:
        ACTIVE_ALARMS.clear()
        return "🔕 All alarms cancelled."

    # ---------------- SHOW ALARMS ----------------
    if (
       "show alarm" in cmd
        or "show alarms" in cmd
        or "list alarm" in cmd
        or "list alarms" in cmd
    ):
       if  not ACTIVE_ALARMS:
           return "No alarms are set."
       return "\n".join(
         f"{i}. {t.strftime('%I:%M %p')}"
         for i, t in enumerate(ACTIVE_ALARMS, 1)
    )


    # ---------------- REMINDER ----------------
    if "remind me" in cmd or "set reminder" in cmd:
        return _handle_reminder(cmd)

    if "cancel reminder" in cmd or "delete reminder" in cmd:
        ACTIVE_REMINDER["active"] = False
        return "⏰ Reminder cancelled."

    # ---------------- MATH ----------------
    if any(op in cmd for op in [
        "add", "subtract", "multiply", "divide",
        "plus", "minus", "times", "divided by",
        "+", "-", "*", "/"
    ]) and "calculator" not in cmd:
        result = _perform_calculation(cmd)
        if result:
            return result

    # ---------------- NOTEPAD ----------------
    if "open notepad" in cmd:
        subprocess.Popen("notepad")
        return "Opening Notepad."

    if "close notepad" in cmd:
        os.system("taskkill /IM notepad.exe /F 2>nul")
        return "Closing Notepad."

    if ("write" in cmd or "type" in cmd) and "notepad" in cmd:
        text = _extract_after_keywords(cmd, ["write", "type"])
        subprocess.Popen("notepad")
        time.sleep(1)
        if text:
            pyautogui.write(text, interval=0.03)
            return f"Typing '{text}' in Notepad."
# -------------------------------------------------
# CAMERA
# -------------------------------------------------
    if "open camera" in cmd:
        subprocess.Popen("start microsoft.windows.camera:", shell=True)
        return "Opening camera."

    if "take photo" in cmd or "take picture" in cmd or "click photo" in cmd:
        return _take_photo()

    # ---------------- WINDOW ----------------
    # ---------------- WINDOW ----------------
    if "minimize window" in cmd or "minimise window" in cmd:
        pyautogui.hotkey("win", "down")
        return "Window minimized."


    if "maximize window" in cmd:
        pyautogui.hotkey("win", "up")
        return "Window maximized."

    if "restore window" in cmd:
        pyautogui.hotkey("win", "up")
        return "Window restored."

    # ---------------- YOUTUBE ----------------
    # ---------------- YOUTUBE ----------------
    
    if "search" in cmd and "youtube" in cmd: 
        query = cmd.replace("search", "").replace("on youtube", "").strip() 
        return _youtube_search(query)
    if cmd.startswith("play "):
        query = cmd.replace("play", "", 1).strip()
        if query:
          return _youtube_play_first(query)

    
    
    if "open youtube" in cmd:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    # ---------------- SCREENSHOT ----------------
    if "screenshot" in cmd:
        pyautogui.screenshot("screenshot.png")
        return "Screenshot saved."

    # ---------------- VOLUME ----------------
    if "volume" in cmd:
        if "increase" in cmd or "up" in cmd:
            return increase_volume(5)
        if "decrease" in cmd or "down" in cmd:
            return decrease_volume(5)
        if "mute" in cmd:
            return mute_volume()
        m = re.search(r"\d{1,3}", cmd)
        if m:
            return set_volume(int(m.group()))

    # ---------------- BRIGHTNESS ----------------
    if "brightness" in cmd:
        return _handle_brightness(cmd)

    # ---------------- POWER ----------------
    if "lock screen" in cmd:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return "Locking screen."
    if "sleep" in cmd:
        os.system("powershell -command \"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState('Suspend', $false, $false)\"")
        return "Putting system to sleep."
    if "screen off" in cmd:
          os.system(
            'powershell -command "Add-Type -TypeDefinition \'using System; using System.Runtime.InteropServices; '
            'public class ScreenControl { '
            '[DllImport(\\"user32.dll\\")] public static extern int SendMessage(int hWnd, int hMsg, int wParam, int lParam); '
            '}\' ; '
            '[ScreenControl]::SendMessage(-1, 0x0112, 0xF170, 2)"'
          )
          return "Turning screen off."

    if "cancel shutdown" in cmd:
        os.system("shutdown /a")
        return "Shutdown cancelled."
    if "restart" in cmd:
        os.system("shutdown /r /t 0")
        return "Restarting."


    if "shutdown" in cmd:
        os.system("shutdown /s /t 30")
        return "Shutting down in 30 seconds."

    
    # ---------------- UNIVERSAL OPEN ----------------
    # ---------------- UNIVERSAL OPEN ----------------
    if cmd.startswith("open "):
        name = cmd.replace("open", "", 1).strip().lower()

    # 1️⃣ try system apps first
        app = _open_system_app(name)
        if app:
           return app

    # 2️⃣ known website overrides
        KNOWN_WEBSITES = {
            "youtube": "https://www.youtube.com",
            "twitter": "https://x.com",
            "linkedin": "https://www.linkedin.com",
            "github": "https://github.com",

            "openai": "https://www.openai.com",
            "chatgpt": "https://chat.openai.com",
            "chat gpt": "https://chat.openai.com",
            "openai chat": "https://chat.openai.com",

            "gemini": "https://gemini.google.com",
            "google gemini": "https://gemini.google.com",
        }

        if name in KNOWN_WEBSITES:
           webbrowser.open(KNOWN_WEBSITES[name])
           return f"Opening {name}."

    # 3️⃣ generic website fallback (IMPROVED)
        clean_name = name.replace(" ", "")

        if clean_name.startswith(("http://", "https://")):
           webbrowser.open(clean_name)
           return f"Opening {name}."

        if "." in clean_name:
           webbrowser.open("https://" + clean_name)
           return f"Opening {name}."

        webbrowser.open(f"https://{clean_name}.com")
        return f"Opening {name}."

# ✅ THIS IS REQUIRED AND CORRECT
# 
    if "search" in cmd:
        query = cmd.replace("search", "").strip()
        webbrowser.open(
            f"https://www.google.com/search?q={query.replace(' ', '+')}"
        )
        return f"Searching Google for '{query}'."

    return None
# =====================================================
# SYSTEM APPS
# =====================================================
def _open_system_app(name):
    name = name.lower()

    exe_apps = {
        "calculator": "calc.exe",
        "notepad": "notepad",
        "cmd": "cmd",
        "explorer": "explorer",
        "control panel": "control",
        "vs code": "code",
        "vscode": "code",
        "task manager": "taskmgr",
        "wordpad": "wordpad",
    }

    office_apps = {
        "word": "start winword",
        "excel": "start excel",
        "powerpoint": "start powerpnt",
        "outlook": "start outlook",
    }

    # ---- Windows system apps ----
    if "camera" in name:
        subprocess.Popen("start microsoft.windows.camera:", shell=True)
        return "Opening Camera."

    if "settings" in name:
        subprocess.Popen("start ms-settings:", shell=True)
        return "Opening Settings."

    if "store" in name:
        subprocess.Popen("start ms-windows-store:", shell=True)
        return "Opening Microsoft Store."
    if name == "outlook":
       subprocess.Popen("start outlookmail:", shell=True)
       return "Opening Outlook."

    # ---- Browsers (Windows-safe) ----
    if name == "chrome":
        subprocess.Popen("start chrome", shell=True)
        return "Opening Chrome."

    if name == "edge":
        subprocess.Popen("start msedge", shell=True)
        return "Opening Edge."

    if name == "firefox":
        subprocess.Popen("start firefox", shell=True)
        return "Opening Firefox."
    if name in ["paint", "mspaint"]:
        subprocess.Popen("mspaint")
        return "Opening Paint."
    if name == "cmd":
        subprocess.Popen("cmd")
        return "Opening Command Prompt."
    # ---- Office apps ----
    for key, cmd in office_apps.items():
        if key in name:
            subprocess.Popen(cmd, shell=True)
            return f"Opening {key.title()}."
        

    # ---- Other apps ----
    for key, exe in exe_apps.items():
        if key in name:
            subprocess.Popen(exe)
            return f"Opening {key.title()}."

    return None


# =====================================================
# SUPPORT
# =====================================================
def _extract_after_keywords(cmd, keywords):
    for key in keywords:
        if key in cmd:
            return cmd.split(key, 1)[1].replace("notepad", "").strip()
    return None


# =====================================================
# BRIGHTNESS
# =====================================================
def _handle_brightness(cmd):
    try:
        import screen_brightness_control as sbc
    except ImportError:
        return "Install brightness module: pip install screen_brightness_control"

    if "increase" in cmd:
        sbc.set_brightness(min(100, sbc.get_brightness()[0] + 20))
        return "Brightness increased."

    if "decrease" in cmd:
        sbc.set_brightness(max(0, sbc.get_brightness()[0] - 20))
        return "Brightness decreased."

    m = re.search(r"\d{1,3}", cmd)
    if m:
        sbc.set_brightness(int(m.group()))
        return f"Brightness set to {m.group()}%."

    return "Brightness command not recognized."


# =====================================================
# YOUTUBE
# =====================================================
def _youtube_search(query):
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Searching YouTube for '{query}'."

def _youtube_play_first(query):
    if not query:
        return "What should I play on YouTube?"

    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    html = requests.get(search_url, headers=headers, timeout=10).text

    # robust regex for watch URLs
    match = re.search(r"\/watch\?v=([a-zA-Z0-9_-]{11})", html)

    if match:
        video_url = "https://www.youtube.com/watch?v=" + match.group(1)
        webbrowser.open(video_url)
        return f"🎵 Playing '{query}' on YouTube."

    return "Could not find a playable video."


# =====================================================
# MATH
# =====================================================
def _perform_calculation(cmd):
    clean = (
        cmd.replace("plus", "+")
           .replace("minus", "-")
           .replace("add", "+")
           .replace("subtract", "-")
           .replace("multiply", "*")
           .replace("times", "*")
           .replace("divided by", "/")
           .replace("divide", "/")
    )

    nums = re.findall(r"\d+\.?\d*", clean)
    if len(nums) < 2:
        return None

    a, b = float(nums[0]), float(nums[1])

    if "+" in clean:
        return f"{a} + {b} = {a + b}"
    if "-" in clean:
        return f"{a} - {b} = {a - b}"
    if "*" in clean:
        return f"{a} * {b} = {a * b}"
    if "/" in clean:
        if b == 0:
            return "Cannot divide by zero."
        return f"{a} / {b} = {a / b}"


# =====================================================
# REMINDER
# =====================================================
def _handle_reminder(cmd):
    match = re.search(r"(\d+)", cmd)
    if not match:
        return "Specify reminder time."

    value = int(match.group(1))
    if "second" in cmd:
        seconds = value
    elif "minute" in cmd:
        seconds = value * 60
    elif "hour" in cmd:
        seconds = value * 3600
    else:
        return "Use seconds, minutes, or hours."

    ACTIVE_REMINDER["active"] = True
    threading.Thread(target=_reminder_timer, args=(seconds,), daemon=True).start()
    return f"⏰ Reminder set for {value}."


def _reminder_timer(seconds):
    time.sleep(seconds)
    if ACTIVE_REMINDER["active"]:
        winsound.Beep(1000, 1200)
    ACTIVE_REMINDER["active"] = False


# =====================================================
# ALARM
# =====================================================
def _handle_alarm(cmd):
    match = re.search(r"(\d{1,2})(:(\d{2}))?\s*(am|pm)?", cmd)
    if not match:
        return "Say alarm time like 6:30 am."

    hour = int(match.group(1))
    minute = int(match.group(3) or 0)
    period = match.group(4) or "am"

    if period == "pm" and hour != 12:
        hour += 12
    if period == "am" and hour == 12:
        hour = 0

    now = datetime.now()
    alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if alarm_time <= now:
        alarm_time += timedelta(days=1)

    ACTIVE_ALARMS.append(alarm_time)
    threading.Thread(target=_alarm_timer, args=(alarm_time,), daemon=True).start()

    return f"🔔 Alarm set for {alarm_time.strftime('%I:%M %p')}."
def _show_alarms():
    if not ACTIVE_ALARMS:
        return "⏰ No alarms are set."

    lines = []
    for i, alarm in enumerate(ACTIVE_ALARMS, start=1):
        lines.append(f"{i}. {alarm.strftime('%I:%M %p')}")

    return "⏰ Your alarms:\n" + "\n".join(lines)


# =====================================================
# BATTERY
# =====================================================
def _get_battery_status():
    battery = psutil.sensors_battery()
    if not battery:
        return "Battery info unavailable."
    status = "charging" if battery.power_plugged else "not charging"
    return f"Battery is {battery.percent}% and {status}."
def _take_photo():
    try:
        import cv2
        from datetime import datetime

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            return "Camera not available."

        time.sleep(1)
        ret, frame = cam.read()
        cam.release()

        if not ret:
            return "Failed to capture image."

        # Create folder if not exists
        folder = "camera_photos"
        os.makedirs(folder, exist_ok=True)

        filename = datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
        path = os.path.join(folder, filename)

        cv2.imwrite(path, frame)
        return f"📸 Photo saved in {path}"

    except ImportError:
        return "Camera module missing. Install opencv-python."
    except Exception as e:
        return f"Camera error: {e}"
