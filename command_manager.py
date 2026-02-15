# ====================== command_manager.py ====================== #
import threading
from swara_core.ai_response import set_interview_mode

_current_thread = None
_current_stop_event = None
_lock = threading.Lock()

def start_command(target, *args, **kwargs):
    """
    Start a new background command (like interview or automation)
    Safely stops the currently running command before starting a new one.
    """

    global _current_thread, _current_stop_event

    with _lock:
        # Stop current command if active
        if _current_stop_event is not None:
            _current_stop_event.set()

        stop_event = threading.Event()
        kwargs["stop_event"] = stop_event     # Pass to interview
        _current_stop_event = stop_event

        thread = threading.Thread(
            target=target, args=args, kwargs=kwargs, daemon=True
        )
        _current_thread = thread
        thread.start()


def interrupt_current():
    """
    Request the currently running command to stop (e.g. interview).
    """
    global _current_stop_event, _current_thread
    with _lock:
        if _current_stop_event is not None:
            _current_stop_event.set()
        set_interview_mode(False)  # RETURN CONTROL BACK TO GENERAL MODE