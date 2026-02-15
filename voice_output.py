from gtts import gTTS
import os
import threading
import tempfile
import time

# ================== GLOBALS ================== #
_speech_lock = threading.RLock()
_current_thread = None
_stop_playback = threading.Event()

# ================== INIT AUDIO (ONCE) ================== #
try:
    import pygame
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=22050, size=-16, channels=2)
except Exception as e:
    print("[Audio Init Error]", e)


# ================== STOP SPEECH ================== #
def stop_speech():
    """
    Immediately stop any playing or pending speech.
    Safe to call multiple times.
    """
    _stop_playback.set()
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
    except Exception:
        pass


# ================== PUBLIC SPEAK API ================== #
def speak(text: str, interrupt: bool = True):
    """
    Speak the given text asynchronously.

    :param text: Text to speak
    :param interrupt: If True, stops current speech immediately
    """
    global _current_thread

    if not text or not isinstance(text, str):
        return

    with _speech_lock:
        if interrupt:
            stop_speech()

        _stop_playback.clear()

        _current_thread = threading.Thread(
            target=_play_speech,
            args=(text,),
            daemon=True
        )
        _current_thread.start()


# ================== INTERNAL PLAYBACK ================== #
def _play_speech(text: str):
    file_path = None

    try:
        # Early exit if interrupted before start
        if _stop_playback.is_set():
            return

        # Create temp file
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(
            temp_dir, f"swara_{int(time.time() * 1000)}.mp3"
        )

        # ------------------ TTS GENERATION (NETWORK) ------------------ #
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
        tts.save(file_path)

        # If interrupted during generation
        if _stop_playback.is_set():
            return

        # ------------------ PLAYBACK ------------------ #
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if _stop_playback.is_set():
                pygame.mixer.music.stop()
                break
            time.sleep(0.02)

    except Exception as e:
        print(f"[Speech Error] {e}")

    finally:
        _safe_remove(file_path)


# ================== SAFE FILE DELETE ================== #
def _safe_remove(path: str | None):
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
