# ====================== interview_mode.py ====================== #
import time
import threading

from swara_core.voice_input import listen, stop_listening, STOP_INTERVIEW_EVENT
from swara_core.voice_output import speak
from swara_core.ai_response import ai_reply, set_interview_mode
from swara_core.interview_logger import interview_logger


# ====================== CONSTANTS ====================== #
START_WORDS = {"start", "start interview", "begin interview"}
STOP_WORDS = {"stop", "end", "quit", "exit"}
NEXT_WORDS = {"next", "skip"}
YES_WORDS = {"yes", "yeah", "ok", "okay", "continue"}

QUESTIONS_PER_ROUND = 5
INTERVIEW_ACTIVE = threading.Event()
INTERVIEW_STARTED = False

asked_questions = set()


# ===============================================================
# WAIT FOR START
# ===============================================================
def wait_for_start_command(role, stop_event, gui_callback=None, gui_listener_controller=None):
    while not stop_event.is_set():
        text = safe_listen()
        if text and any(w in text.lower() for w in START_WORDS):
            start_interview(role, stop_event, gui_callback, gui_listener_controller)
            return


# ===============================================================
# MAIN INTERVIEW
# ===============================================================
def start_interview(role, stop_event, gui_callback=None, gui_listener_controller=None):
    global INTERVIEW_STARTED

    # 🔑 UI STOP SUPPORT (NO FLOW CHANGE)
    if stop_event.is_set():
        STOP_INTERVIEW_EVENT.set()
        return

    stop_event.clear()
    STOP_INTERVIEW_EVENT.clear()
    INTERVIEW_ACTIVE.set()
    INTERVIEW_STARTED = True
    asked_questions.clear()

    set_interview_mode(True)
    if gui_listener_controller:
        gui_listener_controller(False)

    speak(f"Starting {role} interview. Say next to skip, stop to end.")
    interview_logger.start_session(role)

    question_count = 1

    try:
        while INTERVIEW_ACTIVE.is_set():

            if STOP_INTERVIEW_EVENT.is_set() or stop_event.is_set():
                STOP_INTERVIEW_EVENT.set()
                return

            for _ in range(QUESTIONS_PER_ROUND):

                if STOP_INTERVIEW_EVENT.is_set() or stop_event.is_set():
                    STOP_INTERVIEW_EVENT.set()
                    return

                question = generate_question(role)
                if not question:
                    return

                if STOP_INTERVIEW_EVENT.is_set() or stop_event.is_set():
                    STOP_INTERVIEW_EVENT.set()
                    return

                if gui_callback:
                    gui_callback(f"\nQ{question_count}: {question}\n")

                speak(question)
                question_count += 1

                intent, answer = listen_with_intent()

                if intent == "STOP":
                    return

                if intent == "NEXT":
                    interview_logger.add_qa_pair(question, "(Skipped)")
                    if gui_callback:
                        gui_callback("You: (Skipped)\n")
                    continue

                interview_logger.add_qa_pair(question, answer or "(No answer)")
                if gui_callback:
                    gui_callback(f"You: {answer or '(No answer)'}\n")

                # ---------------- FOLLOW UP ----------------
                follow_up = generate_follow_up(answer)

                if STOP_INTERVIEW_EVENT.is_set() or stop_event.is_set():
                    STOP_INTERVIEW_EVENT.set()
                    return

                if follow_up:
                    if gui_callback:
                        gui_callback(f"Follow-up: {follow_up}\n")

                    speak(follow_up)

                    intent, follow_ans = listen_with_intent()

                    if intent == "STOP":
                        return

                    if intent == "NEXT":
                        interview_logger.add_qa_pair(follow_up, "(Skipped follow-up)")
                        if gui_callback:
                            gui_callback("You: (Skipped follow-up)\n")
                        continue

                    interview_logger.add_qa_pair(follow_up, follow_ans or "(No answer)")
                    if gui_callback:
                        gui_callback(f"You: {follow_ans or '(No answer)'}\n")

            # -------- CONTINUE / STOP --------
            if STOP_INTERVIEW_EVENT.is_set() or stop_event.is_set():
                STOP_INTERVIEW_EVENT.set()
                return

            speak("Do you want to continue or stop?")
            intent, reply = listen_with_intent()

            if intent == "STOP":
                speak("Stopping interview.")
                return

            if not (reply and any(w in reply.lower() for w in YES_WORDS)):
                speak("Continuing.")
                return

            speak("Please say continue or stop clearly.")

    finally:
        end_interview(role, gui_callback, gui_listener_controller)


# ===============================================================
# LISTENER
# ===============================================================
def listen_with_intent():
    parts = []
    start_time = time.time()
    last_voice = None

    MAX_IDLE = 1.6
    MAX_TOTAL = 12.0

    while time.time() - start_time < MAX_TOTAL:

        if STOP_INTERVIEW_EVENT.is_set():
            return "STOP", None

        text = safe_listen()

        if text:
            lower = text.lower()

            if any(w in lower for w in STOP_WORDS):
                STOP_INTERVIEW_EVENT.set()
                return "STOP", None

            if any(w in lower for w in NEXT_WORDS):
                return "NEXT", None

            parts.append(text)
            last_voice = time.time()

        else:
            if last_voice and time.time() - last_voice > MAX_IDLE:
                break

    return "ANSWER", " ".join(parts).strip() if parts else None


def safe_listen():
    try:
        return listen(timeout=0.4, phrase_time_limit=None)
    except Exception:
        return None


# ===============================================================
# QUESTION GENERATION (NO REPEAT)
# ===============================================================
def generate_question(role):
    for _ in range(3):
        q = ai_reply(
            f"""
Ask ONE interview question for a {role} role.
Do NOT repeat or rephrase any previous question.

Previous questions:
{list(asked_questions)}
""",
            mode="question",
            max_tokens=20
        )

        if STOP_INTERVIEW_EVENT.is_set():
            return None

        if not q:
            continue

        q = q.strip()

        if q not in asked_questions:
            asked_questions.add(q)
            return q

    return None


def generate_follow_up(answer):
    if not answer or len(answer.split()) < 2:
        return None

    return ai_reply(
        f"Short follow-up question (max 6 words).\nAnswer: {answer}",
        mode="question",
        max_tokens=12
    )


# ===============================================================
# END INTERVIEW
# ===============================================================
def end_interview(role, gui_callback, gui_listener_controller):
    global INTERVIEW_STARTED

    INTERVIEW_ACTIVE.clear()

    if INTERVIEW_STARTED:
        feedback = generate_feedback(role)
        if gui_callback:
            gui_callback("\n--- Interview Feedback ---\n")
            gui_callback(feedback + "\n")
        speak(feedback)

    interview_logger.end_session()
    interview_logger.export_to_csv()

    set_interview_mode(False)
    stop_listening()
    time.sleep(0.2)

    if gui_listener_controller:
        gui_listener_controller(True)

    INTERVIEW_STARTED = False


def generate_feedback(role):
    session = interview_logger.current_session
    if not session:
        return "Interview completed."

    qa_pairs = session.get("qa_pairs", [])

    transcript = "\n".join(
        f"Q: {qa['question']}\nA: {qa['answer']}"
        for qa in qa_pairs
    )

    prompt = f"""
Evaluate this {role} interview.

Transcript:
{transcript}

Give 3 short points:
Strength, Weakness, Improvement.
"""

    feedback = ai_reply(
        prompt,
        mode="feedback",
        max_tokens=40
    ) or "Interview completed."

    interview_logger.add_feedback(feedback)
    return feedback


# ===============================================================
# UI END INTERVIEW HANDLER (OPTIONAL)
# ===============================================================
def on_end_interview_clicked():
    STOP_INTERVIEW_EVENT.set()
    INTERVIEW_ACTIVE.clear()
    stop_listening()
