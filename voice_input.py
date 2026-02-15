import speech_recognition as sr
import threading
import time

# =====================================================
# GLOBALS
# =====================================================
_listener_thread = None
_stop_listen_event = threading.Event()
_audio_lock = threading.Lock()

STOP_INTERVIEW_EVENT = threading.Event()
FAST_MODE = threading.Event()

# =====================================================
# RECOGNIZER
# =====================================================
_recognizer = sr.Recognizer()
_recognizer.energy_threshold = 300
_recognizer.dynamic_energy_threshold = True

INTERVIEW_PAUSE = 4.0
INTERVIEW_NON_SPEECH = 2.0

GENERAL_PAUSE = 2.0
GENERAL_NON_SPEECH = 0.8

_recognizer.pause_threshold = INTERVIEW_PAUSE
_recognizer.non_speaking_duration = INTERVIEW_NON_SPEECH


# =====================================================
# BLOCKING LISTEN (INTERVIEW)
# =====================================================
def listen(timeout=10, phrase_time_limit=None):
    with _audio_lock:
        try:
            _recognizer.pause_threshold = INTERVIEW_PAUSE
            _recognizer.non_speaking_duration = INTERVIEW_NON_SPEECH

            with sr.Microphone() as source:
                audio = _recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            return _recognizer.recognize_google(audio).lower().strip()

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return ""
        except Exception as e:
            print("[VOICE ERROR]", e)
            return ""


# =====================================================
# INTERVIEW LISTEN
# =====================================================
def interview_listen():
    parts = []
    silence = 0
    MAX_SILENCE = 1

    STOP_INTERVIEW_EVENT.clear()

    while not STOP_INTERVIEW_EVENT.is_set():
        text = listen(timeout=3, phrase_time_limit=5)

        if text:
            silence = 0

            if text in ["stop", "stop interview", "exit", "quit"]:
                STOP_INTERVIEW_EVENT.set()
                FAST_MODE.set()
                return "__STOP__"

            parts.append(text)
        else:
            silence += 1
            if silence >= MAX_SILENCE:
                break

    return " ".join(parts).strip()


# =====================================================
# BACKGROUND LISTENER (GENERAL MODE)
# =====================================================
def _listen_loop(callback):
    # Calibrate ONCE
    with sr.Microphone() as source:
        _recognizer.adjust_for_ambient_noise(source, duration=0.4)

    while not _stop_listen_event.is_set():
        try:
            with _audio_lock:
                _recognizer.pause_threshold = GENERAL_PAUSE
                _recognizer.non_speaking_duration = GENERAL_NON_SPEECH

                with sr.Microphone() as source:
                    audio = _recognizer.listen(
                        source,
                        timeout=2 if FAST_MODE.is_set() else 6,
                        phrase_time_limit=3 if FAST_MODE.is_set() else 8
                    )

            text = _recognizer.recognize_google(audio).lower().strip()

            # STOP = command, not mic kill
            if text in ["stop", "exit", "cancel"]:
                FAST_MODE.set()
                if callback:
                    callback("stop")
                continue

            if len(text.split()) < 2:
                continue

            FAST_MODE.clear()
            if callback:
                callback(text)

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            pass
        except Exception as e:
            print("[VOICE ERROR]", e)

        time.sleep(0.03)


# =====================================================
# START LISTENING
# =====================================================
def start_listening(callback):
    global _listener_thread

    stop_listening()
    _stop_listen_event.clear()
    FAST_MODE.clear()

    _listener_thread = threading.Thread(
        target=_listen_loop,
        args=(callback,),
        daemon=True
    )
    _listener_thread.start()


# =====================================================
# STOP LISTENING (GUI ONLY)
# =====================================================
def stop_listening():
    global _listener_thread
    _stop_listen_event.set()
    FAST_MODE.clear()
    _listener_thread = None
