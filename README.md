# WhisperVoice

Local AI multilingual voice input for macOS (Apple Silicon)
100% Free, Offline, No API key needed

Press F5 to speak. Auto-detects English / Cantonese / Mandarin.

## Requirements
- macOS 12+, Apple Silicon (M1/M2/M3/M4)
- Python 3.12 via Homebrew
- 150MB disk for Whisper model (auto-downloaded on first run)

## Install
git clone https://github.com/mingchan1348/whisper-voice.git
cd whisper-voice
./setup.sh

## Assign F5 Shortcut
1. Copy WhisperVoice.workflow to ~/Library/Services/
2. System Settings > Keyboard > Keyboard Shortcuts > Services
3. Find WhisperVoice > assign F5

## Usage
- F5        : Start recording
- F5 again  : Stop + AI transcribes + types into active app

## Roadmap
- Screen overlay / floating translation panel
- Push-to-talk (hold F5)
- Translation mode (speak Chinese, output English)
