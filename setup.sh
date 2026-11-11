#!/bin/bash
# WhisperVoice Setup Script
echo "Installing WhisperVoice dependencies..."
/opt/homebrew/bin/pip3.12 install faster-whisper sounddevice numpy rumps --break-system-packages
echo ""
echo "Done! Now:"
echo "1. Run: python3.12 whisper_voice.py"
echo "2. Set F5 shortcut in System Settings > Keyboard > Keyboard Shortcuts > Services"
