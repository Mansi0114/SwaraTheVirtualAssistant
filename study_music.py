import webbrowser
import json
from urllib.parse import quote
from typing import List, Dict, Tuple
from swara_core.ai_response import ai_reply

# ============================================================
# DUMMY MUSIC PLAYER (for interface compatibility – NO VLC)
# ============================================================
class DummyMusicPlayer:
    def stop(self):
        return "Music stopped."

music_player = DummyMusicPlayer()


# ============================================================
# MUSIC HANDLER (YouTube Browser Based)
# ============================================================
def handle_music_command(command: str) -> str:
    cmd = command.lower()

    if cmd.startswith("play"):
        song = (
            cmd.replace("play", "")
               .replace("song", "")
               .replace("music", "")
               .strip()
        )

        if not song:
            return "Please tell me which song you want to play."

        url = f"https://www.youtube.com/results?search_query={quote(song)}"
        webbrowser.open(url)
        return f"🎵 Playing {song} on YouTube."

    if "stop" in cmd:
        return "Music stopped."

    return "Music command handled."


# ============================================================
# STUDY RESOURCES (STATIC FALLBACK)
# ============================================================
STUDY_RESOURCES = {
    "python": {
        "beginner": [
            "docs.python.org",
            "w3schools.com/python",
            "realpython.com"
        ],
        "advanced": [
            "refactoring.guru",
            "realpython.com/advanced"
        ]
    },
    "machine learning": {
        "beginner": [
            "developers.google.com/ml",
            "course.fast.ai"
        ],
        "advanced": [
            "deeplearningbook.org",
            "paperswithcode.com"
        ]
    }
}

# ============================================================
# AI STUDY PLAN
# ============================================================
def generate_study_plan(topic: str, level: str) -> str:
    prompt = f"""
    Create a SHORT, beginner-friendly study plan for {topic} ({level}).
    Use numbered steps.
    Do not exceed 8 points.
    """
    return ai_reply(prompt)


def _clean_ai_text(text: str, max_lines: int = 10) -> str:
    """
    Cleans and limits AI output for UI display
    """
    if not text:
        return "No study plan available."

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return "\n".join(lines[:max_lines])


# ============================================================
# MAIN STUDY HANDLER (USED BY interface.py)
# ============================================================
def handle_study_command(command: str) -> str:
    cmd = command.lower()

    level = "advanced" if "advanced" in cmd or "expert" in cmd else "beginner"

    topic = (
        cmd.replace("study", "")
           .replace("learn", "")
           .replace("resources for", "")
           .strip()
    )

    if not topic:
        return "Please say something like: study python"

    raw_plan = generate_study_plan(topic, level)
    study_plan = _clean_ai_text(raw_plan)

    response = [
        f"📘 {topic.capitalize()} – {level.capitalize()} Study Plan\n",
        study_plan,
        "\n🎥 Learn More:",
        f"• YouTube: https://www.youtube.com/results?search_query=learn+{quote(topic)}",
        "\n🌐 Useful Links:"
    ]

    for link in STUDY_RESOURCES.get(topic, {}).get(level, []):
        response.append(f"• {link}")

    response.append("\n💡 Tip: Say 'study python advanced' for next level.")

    return "\n".join(response)
