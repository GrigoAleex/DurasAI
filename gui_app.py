import math
import threading
import wave
from pathlib import Path
import tkinter as tk

import numpy as np
import sounddevice as sd

from config import INPUT_WAV
from main import ask_llm, speak, transcribe


class HoldToTalkRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.stream = None
        self.frames = []
        self.lock = threading.Lock()

    def _on_audio(self, indata, frames, time_info, status):
        if status:
            return
        with self.lock:
            self.frames.append(indata.copy())

    def start(self):
        if self.stream is not None:
            return
        with self.lock:
            self.frames = []
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            callback=self._on_audio,
        )
        self.stream.start()

    def stop(self, output_path):
        if self.stream is None:
            return 0.0

        self.stream.stop()
        self.stream.close()
        self.stream = None

        with self.lock:
            if not self.frames:
                return 0.0
            audio = np.concatenate(self.frames, axis=0)
            self.frames = []

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio.tobytes())

        return len(audio) / float(self.sample_rate)


class VoiceAssistantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Voice Assistant")
        self.geometry("520x700")
        self.minsize(440, 640)
        self.configure(bg="#0f172a")

        self.recorder = HoldToTalkRecorder()
        self.is_recording = False
        self.is_busy = False
        self.is_speaking = False
        self.space_down = False
        self.animation_phase = 0.0

        self.status_var = tk.StringVar(value="Hold button to talk")
        self.user_var = tk.StringVar(value="-")
        self.assistant_var = tk.StringVar(value="-")

        self._build_ui()
        self._animate_orb()

        self.bind("<KeyPress-space>", self._on_space_press)
        self.bind("<KeyRelease-space>", self._on_space_release)
        self.bind("<ButtonRelease-1>", self._on_global_release)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(150, self.focus_force)

    def _build_ui(self):
        shell = tk.Frame(self, bg="#0f172a")
        shell.pack(fill="both", expand=True, padx=24, pady=24)

        title = tk.Label(
            shell,
            text="Talk with your AI",
            font=("Avenir Next", 24, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            shell,
            text="Press and hold to record. Release to send.",
            font=("Avenir Next", 13),
            fg="#94a3b8",
            bg="#0f172a",
        )
        subtitle.pack(anchor="w", pady=(4, 24))

        self.canvas = tk.Canvas(
            shell,
            width=260,
            height=260,
            bg="#0f172a",
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(pady=(0, 16))
        self.glow = self.canvas.create_oval(40, 40, 220, 220, fill="#1e3a8a", outline="")
        self.core = self.canvas.create_oval(70, 70, 190, 190, fill="#2563eb", outline="")

        status = tk.Label(
            shell,
            textvariable=self.status_var,
            font=("Avenir Next", 13, "bold"),
            fg="#f8fafc",
            bg="#0f172a",
        )
        status.pack(pady=(0, 18))

        self.talk_button = tk.Button(
            shell,
            text="Hold to Talk",
            font=("Avenir Next", 15, "bold"),
            fg="#f8fafc",
            bg="#2563eb",
            activebackground="#1d4ed8",
            activeforeground="#f8fafc",
            width=22,
            height=2,
            bd=0,
            relief="flat",
        )
        self.talk_button.pack(pady=(0, 22))
        self.talk_button.bind("<ButtonPress-1>", self._on_button_press)
        self.talk_button.bind("<ButtonRelease-1>", self._on_button_release)

        user_panel = tk.Frame(shell, bg="#111827")
        user_panel.pack(fill="x", pady=(0, 12))
        user_label = tk.Label(
            user_panel,
            text="You said",
            font=("Avenir Next", 11, "bold"),
            fg="#93c5fd",
            bg="#111827",
            anchor="w",
            padx=12,
            pady=8,
        )
        user_label.pack(fill="x")
        self.user_text = tk.Label(
            user_panel,
            textvariable=self.user_var,
            font=("Avenir Next", 12),
            fg="#e5e7eb",
            bg="#111827",
            justify="left",
            anchor="w",
            wraplength=440,
            padx=12,
            pady=10,
        )
        self.user_text.pack(fill="x")

        assistant_panel = tk.Frame(shell, bg="#111827")
        assistant_panel.pack(fill="both", expand=True)
        assistant_label = tk.Label(
            assistant_panel,
            text="Assistant",
            font=("Avenir Next", 11, "bold"),
            fg="#fbbf24",
            bg="#111827",
            anchor="w",
            padx=12,
            pady=8,
        )
        assistant_label.pack(fill="x")
        self.assistant_text = tk.Label(
            assistant_panel,
            textvariable=self.assistant_var,
            font=("Avenir Next", 12),
            fg="#e5e7eb",
            bg="#111827",
            justify="left",
            anchor="w",
            wraplength=440,
            padx=12,
            pady=10,
        )
        self.assistant_text.pack(fill="x")

    def _set_button_idle(self):
        self.talk_button.configure(text="Hold to Talk", bg="#2563eb", activebackground="#1d4ed8")

    def _set_button_recording(self):
        self.talk_button.configure(text="Release to Send", bg="#059669", activebackground="#047857")

    def _set_button_busy(self):
        self.talk_button.configure(text="Working...", bg="#334155", activebackground="#334155")

    def _on_button_press(self, _event):
        self._start_recording()

    def _on_button_release(self, _event):
        self._stop_recording_and_process()

    def _on_global_release(self, _event):
        if self.is_recording:
            self._stop_recording_and_process()

    def _on_space_press(self, _event):
        if self.space_down:
            return
        self.space_down = True
        self._start_recording()

    def _on_space_release(self, _event):
        if not self.space_down:
            return
        self.space_down = False
        self._stop_recording_and_process()

    def _start_recording(self):
        if self.is_busy or self.is_recording:
            return
        try:
            self.recorder.start()
        except Exception as exc:
            self.status_var.set(f"Microphone error: {exc}")
            return
        self.is_recording = True
        self.status_var.set("Listening... release to send")
        self._set_button_recording()

    def _stop_recording_and_process(self):
        if not self.is_recording:
            return
        self.is_recording = False

        try:
            duration = self.recorder.stop(INPUT_WAV)
        except Exception as exc:
            self.status_var.set(f"Recording failed: {exc}")
            self._set_button_idle()
            return

        if duration < 0.25:
            self.status_var.set("Recording too short. Hold a little longer.")
            self._set_button_idle()
            return

        self.is_busy = True
        self.status_var.set("Transcribing...")
        self._set_button_busy()
        worker = threading.Thread(target=self._run_turn, daemon=True)
        worker.start()

    def _run_turn(self):
        try:
            user_text = transcribe()
            if not user_text:
                self.after(0, self.status_var.set, "No speech detected. Try again.")
                return

            self.after(0, self.user_var.set, user_text)
            self.after(0, self.status_var.set, "Thinking...")

            answer = ask_llm(user_text)
            self.after(0, self.assistant_var.set, answer)
            self.after(0, self.status_var.set, "AI speaking...")

            self.is_speaking = True
            speak(answer)
            self.after(0, self.status_var.set, "Ready for next turn")
        except Exception as exc:
            self.after(0, self.status_var.set, f"Error: {exc}")
        finally:
            self.is_speaking = False
            self.is_busy = False
            self.after(0, self._set_button_idle)

    def _animate_orb(self):
        self.animation_phase += 0.14

        if self.is_speaking:
            pulse = (math.sin(self.animation_phase * 2.7) + 1.0) / 2.0
            core_radius = 52 + pulse * 24
            glow_radius = 86 + pulse * 32
            core_color = self._mix_color("#f59e0b", "#ef4444", pulse)
            glow_color = self._mix_color("#a16207", "#b91c1c", pulse)
        elif self.is_recording:
            pulse = (math.sin(self.animation_phase * 4.1) + 1.0) / 2.0
            core_radius = 56 + pulse * 16
            glow_radius = 90 + pulse * 20
            core_color = self._mix_color("#34d399", "#10b981", pulse)
            glow_color = self._mix_color("#065f46", "#047857", pulse)
        else:
            pulse = (math.sin(self.animation_phase) + 1.0) / 2.0
            core_radius = 56 + pulse * 4
            glow_radius = 90 + pulse * 6
            core_color = self._mix_color("#2563eb", "#1d4ed8", pulse)
            glow_color = self._mix_color("#1e3a8a", "#1e40af", pulse)

        center = 130
        self.canvas.coords(
            self.glow,
            center - glow_radius,
            center - glow_radius,
            center + glow_radius,
            center + glow_radius,
        )
        self.canvas.coords(
            self.core,
            center - core_radius,
            center - core_radius,
            center + core_radius,
            center + core_radius,
        )
        self.canvas.itemconfigure(self.glow, fill=glow_color)
        self.canvas.itemconfigure(self.core, fill=core_color)
        self.after(33, self._animate_orb)

    def _on_close(self):
        try:
            if self.is_recording:
                self.recorder.stop(INPUT_WAV)
        finally:
            self.destroy()

    @staticmethod
    def _mix_color(start_hex, end_hex, t):
        t = max(0.0, min(1.0, t))
        s = tuple(int(start_hex[i : i + 2], 16) for i in (1, 3, 5))
        e = tuple(int(end_hex[i : i + 2], 16) for i in (1, 3, 5))
        mixed = tuple(int(s[idx] + (e[idx] - s[idx]) * t) for idx in range(3))
        return "#{:02x}{:02x}{:02x}".format(*mixed)


def main():
    app = VoiceAssistantApp()
    app.mainloop()


if __name__ == "__main__":
    main()
