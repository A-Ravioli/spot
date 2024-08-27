import os
import sys
import threading
import queue
import speech_recognition as sr
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from whisper import load_model, transcribe
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import psutil
from transformers import pipeline  # Import Hugging Face transformers library
from lucide_py import icons

# Initialize Spotify API
scope = "user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


class Spot(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spot: Spotify Voice Control Assistant")
        self.geometry("600x400")

        self.scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing playlist-modify-public"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))
        self.whisper_model = load_model("base")

        self.is_listening = False
        self.command_queue = queue.Queue()
        self.create_ui()
        self.setup_audio_processing()

        # Define possible actions
        self.actions = [
            "skip",
            "previous",
            "restart",
            "pause",
            "play",
            "add_to_playlist",
            "adjust_volume",
            "like_song",
            "dislike_song",
            "get_song_info",
            "shuffle_on",
            "shuffle_off",
            "repeat_on",
            "repeat_off",
        ]

        # Initialize Hugging Face classifier
        self.classifier = pipeline(
            "zero-shot-classification", model="facebook/bart-large-mnli"
        )

    def classify_action(self, text):
        # Use Hugging Face model to classify text
        result = self.classifier(text, self.actions)
        return result["labels"][
            0
        ].lower()  # Return the highest scoring label as the action

    def create_ui(self):
        # Toggle Button for Listening
        self.toggle_button = ttk.Checkbutton(
            self, text="Listen", command=self.toggle_listening
        )
        self.toggle_button.grid(row=0, column=0, padx=20, pady=20)

        # Transcription label
        self.transcription_label = ttk.Label(self, text="")
        self.transcription_label.grid(row=1, column=0, padx=20, pady=10)

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        # Code to start listening
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        def listen_loop():
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                while self.is_listening:
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        self.command_queue.put(audio)
                    except sr.WaitTimeoutError:
                        pass  # Continue listening if timeout occurs

        self.listening_thread = threading.Thread(target=listen_loop)
        self.listening_thread.start()

    def stop_listening(self):
        # Code to stop listening
        self.is_listening = False

    def execute_action(self, action, text):
        try:
            if action == "skip":
                self.sp.next_track()
                self.update_history("Skipping to the next track.")
            elif action == "previous":
                self.sp.previous_track()
                self.update_history("Going to the previous track.")
            elif action == "restart":
                self.sp.seek_track(0)
                self.update_history("Restarting the current track.")
            elif action == "pause":
                self.sp.pause_playback()
                self.update_history("Pausing playback.")
            elif action == "play":
                self.sp.start_playback()
                self.update_history("Starting playback.")
            elif action == "add_to_playlist":
                self.update_history("Feature not implemented: Adding to playlist.")
            elif action == "adjust_volume":
                volume_level = next(
                    (int(word) for word in text.split() if word.isdigit()), None
                )
                if volume_level is not None and 0 <= volume_level <= 100:
                    self.sp.volume(volume_level)
                    self.update_history(f"Setting volume to {volume_level}%")
                else:
                    self.update_history(
                        "Please specify a volume level between 0 and 100."
                    )
            elif action == "like_song":
                current_track = self.sp.current_user_playing_track()
                if current_track:
                    self.sp.current_user_saved_tracks_add([current_track["item"]["id"]])
                    self.update_history("Added current song to your liked songs.")
                else:
                    self.update_history("No track is currently playing.")
            elif action == "dislike_song":
                self.update_history("Feature not implemented: Disliking song.")
            elif action == "get_song_info":
                current_track = self.sp.current_user_playing_track()
                if current_track:
                    track_name = current_track["item"]["name"]
                    artist_name = current_track["item"]["artists"][0]["name"]
                    self.update_history(
                        f"Currently playing: {track_name} by {artist_name}"
                    )
                else:
                    self.update_history("No track is currently playing.")
            elif action == "shuffle_on":
                self.sp.shuffle(True)
                self.update_history("Shuffle mode turned on.")
            elif action == "shuffle_off":
                self.sp.shuffle(False)
                self.update_history("Shuffle mode turned off.")
            elif action == "repeat_on":
                self.sp.repeat("track")
                self.update_history("Repeat mode turned on.")
            elif action == "repeat_off":
                self.sp.repeat("off")
                self.update_history("Repeat mode turned off.")
            else:
                self.update_history(f"Action not recognized: {action}")
        except Exception as e:
            self.update_history(f"Error executing action: {str(e)}")

    def transcribe_and_execute(self, audio):
        try:
            # Save audio to a temporary file for whisper model usage
            with open("temp_audio.wav", "wb") as f:
                f.write(audio.get_wav_data())

            text = self.whisper_model.transcribe("temp_audio.wav")["text"].lower()
            self.update_history(f"You said: {text}")

            action = self.classify_action(text)
            self.execute_action(action, text)
        except Exception as e:
            self.update_history(f"An error occurred: {str(e)}")
        finally:
            self.update_now_playing()  # Ensure this method is defined


def is_spotify_running():
    return "Spotify.exe" in (p.name() for p in psutil.process_iter())


def run_app():
    app = Spot()
    app.mainloop()


if __name__ == "__main__":
    if is_spotify_running():
        run_app()
    else:
        print("Spotify is not running. Please start Spotify first.")
