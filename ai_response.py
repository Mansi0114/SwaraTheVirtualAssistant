# ========================= ai_response.py ========================= #
import os, requests
from dotenv import load_dotenv

load_dotenv()

# ---------------- INTERVIEW STATE ---------------- #
INTERVIEW_MODE_ACTIVE = False

def set_interview_mode(state: bool):
    global INTERVIEW_MODE_ACTIVE
    INTERVIEW_MODE_ACTIVE = state

def is_interview_mode():
    return INTERVIEW_MODE_ACTIVE

# ---------------- PROMPT STYLES (NO MARKDOWN) ---------------- #
GENERAL_MODE_STYLE = """
You are SWARA, a friendly AI desktop assistant.
Respond in plain text only.
Do not use markdown, bullets, stars, hashes, or special formatting.
Give short, clear sentences.
"""

INTERVIEWER_STYLE = """
You are a professional interviewer.
Ask ONLY one interview question at a time.
Use plain text only.
No explanations.
"""

FEEDBACK_STYLE = """
You are an HR interviewer.
Give feedback in plain text only.

Use exactly this format:

Summary:
<one short paragraph>

Strengths:
<one short paragraph>

Weaknesses:
<one short paragraph>

Recommendation:
<one word: Hire / Consider / Not Ready>

Score:
<number>/10
"""

# ---------------- API KEYS ---------------- #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------- MAIN AI ENTRY ---------------- #
def ai_reply(prompt, *, mode="general", max_tokens=120):
    # HARD BLOCK GENERAL AI DURING INTERVIEW
    if INTERVIEW_MODE_ACTIVE and mode == "general":
        return None

    if mode == "question":
        prompt = INTERVIEWER_STYLE + "\n" + prompt
    elif mode == "feedback":
        prompt = FEEDBACK_STYLE + "\n" + prompt
    else:
        prompt = GENERAL_MODE_STYLE + "\n" + prompt

    try:
        return _reply_openai(prompt, max_tokens)
    except:
        try:
            return _reply_gemini(prompt, max_tokens)
        except:
            return None

# ---------------- OPENAI ---------------- #
def _reply_openai(prompt, max_tokens):
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OpenAI API key")

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens
        },
        timeout=15
    )
    return r.json()["choices"][0]["message"]["content"].strip()

# ---------------- GEMINI ---------------- #
def _reply_gemini(prompt, max_tokens):
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing Gemini API key")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    )

    r = requests.post(
        url,
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens}
        },
        timeout=15
    )
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
# ================================================================= # do not make the gemini but if open ai fails gemni take the lead