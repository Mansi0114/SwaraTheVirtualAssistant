import customtkinter as ctk
import threading
from threading import Thread, Lock
import queue
import os
import time
import subprocess
import pyautogui
import pyperclip

from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from swara_core.voice_input import listen, start_listening, stop_listening
from swara_core.voice_output import speak, stop_speech
from swara_core.ai_response import ai_reply
from swara_core.tasks import perform_task
from swara_core.interview_mode import start_interview
from swara_core.study_music import handle_music_command, handle_study_command, music_player
from swara_core import command_manager


class SwaraApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # State variables
        self.listening_active = False
        self.interview_active = False
        self.dictation_active = False
        self.music_playing = False

        self._command_lock = Lock()
        self._last_command_time = 0

        # Window setup
        self.title("Swara - Your AI Desktop Assistant")
        self.geometry("950x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=10, fill="x")

        try:
            swara_img = ctk.CTkImage(light_image=Image.open("gui/swara.png"), size=(80, 80))
            self.logo_label = ctk.CTkLabel(header_frame, image=swara_img, text="")
            self.logo_label.image = swara_img
            self.logo_label.pack(side="left", padx=10)
        except Exception:
            self.logo_label = ctk.CTkLabel(header_frame, text="🪄 Swara", font=("Arial", 26, "bold"))
            self.logo_label.pack(side="left", padx=10)

        self.title_label = ctk.CTkLabel(header_frame, text="Swara - AI Desktop Assistant", font=("Arial", 24, "bold"))
        self.title_label.pack(side="left", padx=10)

        self.status_label = ctk.CTkLabel(header_frame, text="Ready", text_color="green", font=("Arial", 12))
        self.status_label.pack(side="right", padx=20)

        # Chatbox
        self.chatbox = ctk.CTkTextbox(self, width=900, height=400, corner_radius=10)
        self.chatbox.pack(pady=10, padx=10)
        self.chatbox.insert("end", "Swara: Hello! I'm Swara, your AI Desktop Assistant.\n\n")

        # Input frame
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=8, padx=10, fill="x")

        self.entry = ctk.CTkEntry(input_frame, placeholder_text="Type your message...", width=500)
        self.entry.pack(side="left", padx=(0, 5), fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.user_input())

        self.send_btn = ctk.CTkButton(input_frame, text="Send 💬", command=self.user_input, width=80)
        self.send_btn.pack(side="left", padx=3)

        self.voice_btn = ctk.CTkButton(input_frame, text="🎤 Speak", command=self.voice_input, width=80)
        self.voice_btn.pack(side="left", padx=3)

        # Controls frame
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.pack(pady=5, padx=10, fill="x")

        self.listen_toggle_btn = ctk.CTkButton(self.controls_frame, text="🎙️ Listen OFF", command=self.toggle_listening, fg_color="gray")
        self.listen_toggle_btn.pack(side="left", padx=5)

        self.dictation_btn = ctk.CTkButton(self.controls_frame, text="🎤 Start Dictation", command=self.toggle_dictation, fg_color="gray")
        self.dictation_btn.pack(side="left", padx=5)

        self.stop_btn = ctk.CTkButton(self.controls_frame, text="⏹️ Stop", command=self.stop_current_action, fg_color="red", width=100)
        self.stop_btn.pack(side="right", padx=5)

        ctk.CTkLabel(self.controls_frame, text="Stop any running action", text_color="gray").pack(side="left", padx=10)

        # Interview controls
        interview_frame = ctk.CTkFrame(self, fg_color="transparent")
        interview_frame.pack(pady=8, padx=10, fill="x")

        ctk.CTkLabel(interview_frame, text="Interview Role:", font=("Arial", 12, "bold")).pack(side="left", padx=5)

        self.role_var = ctk.StringVar(value="Software Engineer")
        self.role_dropdown = ctk.CTkComboBox(
            interview_frame,
            values=[
                "Software Engineer", "Python Developer", "Web Developer", "Data Analyst",
                "Java Developer", "AI Engineer", "DevOps Engineer", "Frontend Developer",
                "Backend Developer", "QA Engineer", "Cloud Architect",
            ],
            variable=self.role_var,
            width=200,
        )
        self.role_dropdown.pack(side="left", padx=5)

        self.interview_btn = ctk.CTkButton(interview_frame, text="🎤 Start Interview", command=self.start_interview_mode, fg_color="#2ecc71")
        self.interview_btn.pack(side="left", padx=5)

        self.interview_stop_btn = ctk.CTkButton(interview_frame, text="⏹️ End Interview", command=self.stop_interview, fg_color="#e74c3c", state="disabled")
        self.interview_stop_btn.pack(side="left", padx=5)

        # Info area
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(pady=5, padx=10, fill="x")

        info_text = (
            "💡 Tips:\n"
            "• Say 'play [song]' or 'stop music' for music control\n"
            "• 'study [topic]' for learning resources\n"
            "• 'start interview' / 'stop interview' for interview mode\n"
            "• 'start dictation' / 'stop dictation' for dictation mode\n"
            "• 'open [website]' to open any website\n"
            "• 'stop' or 'exit' to stop any running action\n"
        )
        ctk.CTkLabel(info_frame, text=info_text, text_color="cyan", font=("Arial", 10), justify="left").pack(anchor="w")

        # Greet and start listening
        try:
            greeting = "Hello! I'm Swara, your AI Desktop Assistant. I'm ready to help!"
            self.chatbox.insert("end", f"Swara: {greeting}\n\n")
            self.chatbox.see("end")
            speak(greeting)
            self.toggle_listening()
        except Exception as e:
            print(f"Error starting listener: {e}")

    # ------------------ INPUT HANDLERS ------------------

    def user_input(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.chatbox.insert("end", f"You: {user_text}\n")
        self.entry.delete(0, "end")
        self.chatbox.see("end")
        command_manager.start_command(self._process_command_impl, user_text)

    def voice_input(self):
        Thread(target=self.listen_and_process, daemon=True).start()

    def listen_and_process(self):
        self.status_label.configure(text="Listening...", text_color="yellow")
        user_text = listen()
        self.status_label.configure(text="Ready", text_color="green")
        if user_text:
            self.chatbox.insert("end", f"You: {user_text}\n")
            self.chatbox.see("end")
            command_manager.start_command(self._process_command_impl, user_text)

    def handle_voice_command(self, text):
        # Called by start_listening callback when voice recognized
        if not text:
            return

        # If interview active, ignore any commands except STOP (handled elsewhere)
        if self.interview_active:
            # ignore any ambient voice while interview active
            return

        current_time = time.time()
        if current_time - self._last_command_time < 2.5:
            return

        if not self._command_lock.acquire(blocking=False):
            return

        try:
            self._last_command_time = current_time
            self.chatbox.insert("end", f"You: {text}\n")
            self.chatbox.see("end")
            command_manager.start_command(self._process_command_impl, text)
        except Exception as e:
            print(f"Voice command error: {e}")
        finally:
            try:
                self._command_lock.release()
            except Exception:
                pass

    # ------------------ MAIN COMMAND PROCESSOR ------------------

    def _process_command_impl(self, text, stop_event=None):
        cmd = text.lower().strip()

        # If interview is active, block all commands except stop
        if self.interview_active:
            if "stop" in cmd or "end interview" in cmd or "end" in cmd or "exit" in cmd:
                # allow stopping the interview
                self.stop_interview()
            # otherwise ignore any other command while interview in progress
            return

        # Mode controls
        if "start interview" in cmd:
            self.start_interview_mode()
            return

        if "stop interview" in cmd or "end interview" in cmd:
            self.stop_interview()
            return

        if "start dictation" in cmd and not self.dictation_active:
            self.toggle_dictation()
            return

        if ("stop dictation" in cmd or "end dictation" in cmd) and self.dictation_active:
            self.toggle_dictation()
            return

        # Music commands
        if any(keyword in cmd for keyword in ["pause", "resume", "stop music", "next", "previous"]) \
        or cmd.strip() in ["play music", "play song"]:

            try:
                response = handle_music_command(cmd)
                self.chatbox.insert("end", f"🎵 {response}\n\n")
                self.chatbox.see("end")
                speak(response)
                # mark playing state
                self.music_playing = "play" in cmd and "stop" not in cmd
            except Exception as e:
                print(f"Music command error: {e}")
            return

        # Study commands
        if any(keyword in cmd for keyword in ["study ", "learn ", "resources for"]):
            try:
                response = handle_study_command(cmd)
                self.chatbox.insert("end", f"📚 {response}\n\n")
                self.chatbox.see("end")
                speak("Here are your study resources!")
            except Exception as e:
                print(f"Study command error: {e}")
            return

        # Global STOP handling
        if "stop" in cmd or "exit" in cmd:
            stop_speech()
            if self.dictation_active:
                self.toggle_dictation()
                return
            if self.music_playing:
                try:
                    response = music_player.stop()
                    self.chatbox.insert("end", f"🎵 {response}\n\n")
                except Exception:
                    pass
                self.music_playing = False
            command_manager.interrupt_current()
            msg = "Stopped."
            self.chatbox.insert("end", f"Swara: {msg}\n\n")
            self.chatbox.see("end")
            return

        # All system / brightness / website / youtube / etc. handled via perform_task()
        try:
            action = perform_task(cmd, stop_event=stop_event)
            if action:
                self.chatbox.insert("end", f"Swara: {action}\n\n")
                self.chatbox.see("end")
                speak(action)
                return
        except Exception as e:
            print(f"perform_task error: {e}")

        # Fallback to AI chat
        try:
            response = ai_reply(cmd)
            if response:
                self.chatbox.insert("end", f"Swara: {response}\n\n")
                self.chatbox.see("end")
                speak(response)
        except Exception as e:
            print(f"ai_reply error: {e}")

    # ------------------ LISTENING MANAGEMENT ------------------

    def toggle_listening(self, enable=None):
        if enable is None:
            self.listening_active = not self.listening_active
        else:
            self.listening_active = enable

        if self.listening_active:
            # If dictation active, ensure we stop dictation first
            if self.dictation_active:
                self._stop_dictation()

            start_listening(self.handle_voice_command)
            self.listen_toggle_btn.configure(text="🎙️ Listen ON", fg_color="green")
            self.status_label.configure(text="Listening...", text_color="yellow")
            msg = "Voice listening is now active. I'm ready for your commands!"
        else:
            stop_listening()
            self.listen_toggle_btn.configure(text="🎙️ Listen OFF", fg_color="gray")
            self.status_label.configure(text="Ready", text_color="green")
            msg = "Voice listening is now off."

        # Log in chatbox
        try:
            self.chatbox.insert("end", f"Swara: {msg}\n\n")
            self.chatbox.see("end")
        except Exception:
            pass

    # ------------------ DICTATION ------------------

    def toggle_dictation(self):
        self.dictation_active = not self.dictation_active
        if self.dictation_active:
            self._start_dictation()
        else:
            self._stop_dictation()

    def _start_dictation(self):
        # turn off background listening while dictation writes to notepad
        if self.listening_active:
            self.toggle_listening(enable=False)

        self.dictation_text = []
        self.dictation_btn.configure(text="⏹️ Stop Dictation", fg_color="red")
        self.status_label.configure(text="Dictation Active - Speak now...", text_color="orange")
        self.chatbox.insert("end", "Dictation started. Speak now...\n\n")
        self.chatbox.see("end")

        try:
            self.notepad_process = subprocess.Popen(["notepad.exe"])
            time.sleep(1)
            self.dictation_thread = Thread(target=self._dictation_loop, daemon=True)
            self.dictation_thread.start()
        except Exception as e:
            print(f"Error opening notepad for dictation: {e}")
            self._stop_dictation()

    def _dictation_loop(self):
        while self.dictation_active:
            try:
                text = listen(timeout=5, phrase_time_limit=10)
                if text and self.dictation_active:
                    self.dictation_text.append(text)
                    try:
                        pyperclip.copy(text + " ")
                        windows = pyautogui.getWindowsWithTitle("Notepad")
                        if windows:
                            windows[0].activate()
                        pyautogui.hotkey("ctrl", "v")
                        self.after(0, self._update_dictation_status, " ".join(self.dictation_text))
                    except Exception as e:
                        print(f"Dictation write error: {e}")
            except Exception as e:
                print(f"Dictation listen error: {e}")
                break

    def _update_dictation_status(self, current_text):
        if not self.dictation_active:
            return
        try:
            self.chatbox.delete("1.0", "end")
            self.chatbox.insert(
                "1.0",
                "Dictation in progress... (speaking into Notepad)\n\n"
                + "Current text length: "
                + str(len(current_text))
                + " characters\n"
                + "Say 'stop dictation' when finished.",
            )
            self.chatbox.see("end")
        except Exception:
            pass

    def _stop_dictation(self):
        if not self.dictation_active and not hasattr(self, "dictation_thread"):
            return
        self.dictation_active = False
        self.dictation_btn.configure(text="🎤 Start Dictation", fg_color="gray")
        self.status_label.configure(text="Saving dictation...", text_color="orange")
        if hasattr(self, "dictation_thread") and self.dictation_thread.is_alive():
            self.dictation_thread.join(timeout=2)
        if hasattr(self, "dictation_text") and self.dictation_text:
            try:
                dictation_dir = os.path.join(os.path.expanduser("~"), "Documents", "Dictations")
                os.makedirs(dictation_dir, exist_ok=True)
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(dictation_dir, f"dictation_{timestamp}.txt")
                full_text = " ".join(self.dictation_text)
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(full_text)
                self.chatbox.insert("end", f"\nDictation saved to:\n{filename}\n")
                self.chatbox.see("end")
                self.status_label.configure(text="Dictation saved", text_color="green")
                speak("Dictation saved successfully.")
                if hasattr(self, "notepad_process"):
                    try:
                        self.notepad_process.terminate()
                    except Exception:
                        pass
                    delattr(self, "notepad_process")
                os.startfile(filename)
            except Exception as e:
                print(f"Error saving dictation: {e}")
                self.chatbox.insert("end", f"\nError saving dictation: {e}\n")
                self.status_label.configure(text="Save failed", text_color="red")
                speak("Sorry, I couldn't save the dictation.")
        else:
            self.chatbox.insert("end", "\nDictation stopped. No text was transcribed.\n")
            self.status_label.configure(text="Ready", text_color="green")
        self.chatbox.see("end")

    # ------------------ INTERVIEW ------------------

    def start_interview_mode(self):
        if self.interview_active:
            self.chatbox.insert("end", "Swara: Interview already in progress.\n\n")
            self.chatbox.see("end")
            return

        self.interview_active = True
        self.interview_btn.configure(state="disabled")
        self.interview_stop_btn.configure(state="normal")
        self.status_label.configure(text="Interview Active", text_color="orange")

        was_listening = self.listening_active
        if self.listening_active:
            # disable background listening while interview is running
            self.toggle_listening(enable=False)

        self._was_listening_before_interview = was_listening
        role = self.role_var.get()

        self.chatbox.insert("end", f"\n{'=' * 60}\nStarting {role} Interview\n{'=' * 60}\n\n")
        self.chatbox.see("end")

        # create stop event for interview thread
        self.interview_stop_event = threading.Event()

        def interview_thread():
            try:
                # pass gui_listener_controller so interview_mode can re-enable listening after finishing
                start_interview(
                    role,
                    gui_callback=self.add_chat_message,
                    stop_event=self.interview_stop_event,
                    gui_listener_controller=self.toggle_listening
                )
            except Exception as e:
                self.add_chat_message(f"Swara: Interview error: {str(e)}\n\n")
            finally:
                # cleanup (restore listening after interview finishes)
                self.after(0, self._cleanup_interview, was_listening)

        Thread(target=interview_thread, daemon=True).start()

    def stop_interview(self):
        if not self.interview_active:
            return
        # set flag to false and set stop_event so interview thread exits
        if hasattr(self, "interview_stop_event"):
            try:
                self.interview_stop_event.set()
            except Exception:
                pass
        command_manager.interrupt_current()
        stop_speech()
        self.chatbox.insert("end", "\nSwara: Interview stopped.\n\n")
        self.chatbox.see("end")
        # call cleanup immediately
        self._cleanup_interview(was_listening=False)

    def _cleanup_interview(self, was_listening):
        self.interview_active = False
        self.interview_btn.configure(state="normal")
        self.interview_stop_btn.configure(state="disabled")
        self.status_label.configure(text="Ready", text_color="green")

        if hasattr(self, "interview_stop_event"):
            try:
                self.interview_stop_event.set()
            except Exception:
                pass
            try:
                delattr(self, "interview_stop_event")
            except Exception:
                pass

        # restore listener only if it was active before interview AND dictation is not active
        def restore_listener():
            if was_listening and not self.dictation_active:
                self.toggle_listening(enable=True)

        # delay restore slightly to avoid race with interview thread
        self.after(2000, restore_listener)

    # ------------------ STOP CURRENT ACTION ------------------

    def stop_current_action(self):
        stop_speech()
        if self.dictation_active:
            self.toggle_dictation()
        if self.music_playing:
            try:
                response = music_player.stop()
                self.chatbox.insert("end", f"🎵 {response}\n\n")
            except Exception:
                pass
            self.music_playing = False
        command_manager.interrupt_current()
        msg = "Current action stopped."
        self.chatbox.insert("end", f"Swara: {msg}\n\n")
        self.chatbox.see("end")

    # ------------------ UTILS ------------------

    def add_chat_message(self, text):
        try:
            self.chatbox.insert("end", text)
            self.chatbox.see("end")
        except Exception:
            pass


if __name__ == "__main__":
    app = SwaraApp()
    app.mainloop()