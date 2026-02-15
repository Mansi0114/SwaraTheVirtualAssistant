import ctypes
import time

# Windows virtual key codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

# Press a key
def _press(key, times=1):
    for _ in range(times):
        ctypes.windll.user32.keybd_event(key, 0, 0, 0)
        time.sleep(0.05)

def increase_volume(amount=5):
    steps = int(amount / 2)
    _press(VK_VOLUME_UP, steps)
    return f"Volume increased by {amount}%."

def decrease_volume(amount=5):
    steps = int(amount / 2)
    _press(VK_VOLUME_DOWN, steps)
    return f"Volume decreased by {amount}%."

def mute_volume():
    _press(VK_VOLUME_MUTE)
    return "Volume muted."

def unmute_volume():
    _press(VK_VOLUME_MUTE)
    return "Volume unmuted."

def set_volume(level):
    """
    Approximates volume percentage.
    """
    try:
        # Reset to 0%
        for _ in range(50):
            _press(VK_VOLUME_DOWN)

        # Raise to desired %
        steps = int(level / 2)
        for _ in range(steps):
            _press(VK_VOLUME_UP)

        return f"Volume set to {level}%."

    except Exception as e:
        return f"Set volume failed: {e}"
