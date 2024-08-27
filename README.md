# Spot: A Voice Assistant for Spotify Desktop

This application allows you to control your Spotify playback using voice commands. It uses the Whisper model for speech recognition and the OpenAI GPT model for command classification.

## Features

- Voice control for common Spotify actions (play, pause, skip, etc.)
- Displays currently playing track with album art
- Command history log
- Automatic startup when Spotify is launched

## Prerequisites

- Python 3.7+
- Spotify Premium account
- Spotify Developer account
- OpenAI API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/voice-controlled-spotify-app.git
   cd voice-controlled-spotify-app
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your Spotify Developer account and create an app:
   - Go to https://developer.spotify.com/dashboard/
   - Create a new app
   - Add `http://localhost:8888/callback` to the Redirect URIs

4. Create a `.env` file in the project root and add your Spotify and OpenAI credentials:
   ```
   SPOTIPY_CLIENT_ID=your_spotify_client_id
   SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Start the Spotify desktop app.
2. Run the Voice-Controlled Spotify App:
   ```
   python main.py
   ```
3. Click the microphone button to start listening for commands.
4. Speak your command (e.g., "Skip to the next song" or "Pause the music").

## Packaging the App

To create an executable (.exe) file:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create the executable:
   ```
   pyinstaller --onefile --windowed main.py
   ```

3. The executable will be in the `dist` folder.

## Releasing on GitHub

1. Create a new repository on GitHub.
2. Push your code to the repository.
3. Go to the "Releases" section of your GitHub repository.
4. Click "Create a new release".
5. Tag the version (e.g., v1.0.0).
6. Add release notes describing the features and any known issues.
7. Attach the packaged .exe file to the release.
8. Publish the release.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.