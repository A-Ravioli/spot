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
import openai
from lucide_py import icons

# init Spotify API
scope = "user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# load Whisper for speech recognition
# whisper_model = load_model("base") #nvm not rn


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

        openai.api_key = os.getenv("OPENAI_API_KEY")

    def classify_action(self, text):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a voice command classifier for a Spotify control app. Given a user's voice command, classify it into one of the following actions: {', '.join(self.actions)}. Respond with only the action name.",
                },
                {"role": "user", "content": text},
            ],
        )
        return response.choices[0].message["content"].strip().lower()

    def create_ui(self):
        # Mic button
        mic_icon = icons.Mic2(size=24, color="gray")
        self.mic_button = ttk.Button(
            self, image=mic_icon, command=self.handle_voice_control
        )
        self.mic_button.grid(row=0, column=0, padx=20, pady=20)

        # Transcription label
        self.transcription_label = ttk.Label(self, text="")
        self.transcription_label.grid(row=1, column=0, padx=20, pady=10)

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
                # This would require additional logic to specify which playlist
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
            text = self.whisper_model.transcribe(audio.get_wav_data())["text"].lower()
            self.update_history(f"You said: {text}")

            action = self.classify_action(text)
            self.execute_action(action, text)
        except Exception as e:
            self.update_history(f"An error occurred: {str(e)}")
        finally:
            self.update_now_playing()


def is_spotify_running():
    return "Spotify.exe" in (p.name() for p in psutil.process_iter())


def run_app():
    app = Spot()
    app.run()


if __name__ == "__main__":
    if is_spotify_running():
        run_app()
    else:
        print("Spotify is not running. Please start Spotify first.")
