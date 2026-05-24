# 🎙️ Swara — AI-Powered Virtual Voice Assistant

> **Python · NLP · Speech Recognition · SQLite · Tkinter GUI · API Integration · Automation**


## 📌 What is Swara?

**Swara** is a fully-featured, voice-enabled AI virtual assistant built entirely in Python. It goes far beyond basic voice commands — Swara features a **custom Tkinter GUI**, **persistent SQLite memory**, a dedicated **Interview Preparation Mode**, **email automation**, **study music**, **volume control**, and **real-time AI responses** — all orchestrated through a clean modular architecture.

The name *Swara* (Sanskrit: स्वर) means **voice** or **musical note** — a fitting name for a voice-first intelligent assistant.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🎤 **Voice Recognition** | Captures and transcribes user speech in real-time using `speech_recognition` |
| 🧠 **NLP Command Processing** | Tokenization, intent classification, and keyword extraction to understand natural language |
| 🤖 **AI Response Engine** | `ai_response.py` — generates intelligent, context-aware replies to open-ended queries |
| 💬 **Voice Output** | Text-to-speech synthesis for natural spoken responses via `voice_output.py` |
| 🖥️ **Custom GUI** | Full Tkinter-based graphical interface (`interface.py`) with real-time interaction display |
| 🧠 **Persistent Memory** | SQLite-backed conversation memory (`memory_db.py`) — Swara remembers context across sessions |
| 📋 **Interview Prep Mode** | Dedicated interview simulation mode (`interview_mode.py`) with session logging (`interview_logger.py`) |
| ✅ **Task Manager** | Create, track, and manage tasks via voice commands (`tasks.py`) |
| 📧 **Email Automation** | Send emails hands-free using voice commands (`email_service.py`) |
| 🎵 **Study Music** | Play focus/study music on command (`study_music.py`) |
| 🔊 **Volume Control** | Adjust system volume through voice (`volume_control.py`) |
| ⚙️ **Command Manager** | Centralised command routing and dispatch layer (`command_manager.py`) |

---

## 🏗️ Project Architecture

SwaraTheVirtualAssistant/
│
├── main.py                  # Entry point — initialises DB and launches GUI
├── interface.py             # Tkinter GUI — main application window
├── command_manager.py       # Central command routing and dispatch
├── ai_response.py           # AI response generation engine
│
├── voice_input.py           # Speech-to-text (microphone capture)
├── voice_output.py          # Text-to-speech synthesis
│
├── memory_db.py             # SQLite persistent memory — init & CRUD
├── tasks.py                 # Task creation and management via voice
├── email_service.py         # Email automation module
├── study_music.py           # Study/focus music playback
├── volume_control.py        # System volume control
│
├── interview_mode.py        # Interview simulation and Q&A engine
├── interview_logger.py      # Session logger for interview practice
│
└── swara.png                # Application icon / branding asset

**Design pattern:** Modular, single-responsibility architecture. Each feature is isolated in its own module and routed through `command_manager.py`, making the codebase clean, testable, and easily extensible.

---

## ⚙️ How It Works

User speaks
↓
voice_input.py  →  Captures audio from microphone
↓
Speech-to-text  →  Converts audio to raw text
↓
command_manager.py  →  Tokenizes + classifies intent
↓
┌──────────────────────────────────────┐
│  Route to appropriate module:        │
│  tasks / email / music / interview   │
│  volume / AI response / memory       │
└──────────────────────────────────────┘
↓
voice_output.py  →  Speaks the response
↓
interface.py     →  Updates GUI display
↓
memory_db.py     →  Logs interaction to SQLite

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.8+ |
| NLP & Speech | `speech_recognition`, `pyttsx3`, tokenization, intent classification |
| GUI | `Tkinter` |
| Database | `SQLite3` (via `memory_db.py`) |
| Email | `smtplib` / SMTP automation |
| Audio | `pygame` / `playsound` for study music |
| System Control | `pycaw` / `osascript` for volume control |
| AI Response | Custom NLP pipeline + API integration |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A working microphone
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Mansi0114/SwaraTheVirtualAssistant.git
cd SwaraTheVirtualAssistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Swara
python main.py
```

### Try these voice commands
"Hey Swara, what's the time?"
"Open interview mode"
"Play study music"
"Send an email to [name]"
"Increase the volume"
"Remember that my meeting is at 3 PM"

---

## 🎯 Interview Mode — Highlight Feature

One of Swara's most unique features is the **Interview Preparation Mode**:

- Swara asks domain-specific interview questions (technical, HR, or aptitude)
- User responds via voice
- Responses are logged with timestamps via `interview_logger.py`
- Session summary is saved for review and improvement tracking

This feature makes Swara stand out as a **productivity + learning tool**, not just a basic command assistant.

---

## 📈 What Makes This Project Stand Out

- **Persistent memory via SQLite** — most student virtual assistant projects are stateless; Swara remembers
- **Modular architecture** — 13 dedicated Python modules, each with a single responsibility
- **Interview preparation integration** — a rare, practical feature combining NLP + education
- **Full GUI** — not just a terminal app; real application with Tkinter interface
- **Real automation** — email sending, volume control, task tracking are actual OS-level integrations

---

## 🔮 Future Enhancements

- [ ] Integrate OpenAI / Gemini API for more intelligent responses
- [ ] Add wake-word detection ("Hey Swara") for always-on listening
- [ ] Web dashboard for reviewing interview session logs
- [ ] Multi-language support (Hindi, Kannada)
- [ ] IoT device integration (smart home control)
- [ ] Mobile app version using Kivy or BeeWare
- [ ] Extend interview mode with AI-evaluated scoring

---

## 👩‍💻 Developer

**Mansi Kulkarni**
MCA Student | Bangalore Institute of Technology 

> Swara was independently designed and developed — from architecture and NLP pipeline design to GUI, database integration, and system-level automation.

---

## 📄 License

This project is licensed under the MIT License — feel free to use, modify, and build on it with attribution.

---

*"Swara doesn't just hear you — she understands, remembers, and acts."*
