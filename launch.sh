#!/bin/bash
# WhisperVoice launcher
PYTHON=/opt/homebrew/bin/python3.12
APP_DIR=/Users/ming/Applications/WhisperVoice

# Install deps if needed
$PYTHON -m pip install openai sounddevice numpy rumps --quiet 2>/dev/null

# Launch
cd "$APP_DIR"
$PYTHON whisper_voice.py
