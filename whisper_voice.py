#!/usr/bin/env python3
# WhisperVoice — Local AI 多語言語音輸入 for M1 Mac
# 完全離線 · 免費 · 自動識別英文/廣東話/普通話

import os, sys, time, tempfile, subprocess, threading, wave
import numpy as np
import sounddevice as sd
import rumps
from faster_whisper import WhisperModel

MODEL_SIZE = 'base'   # tiny/base/small/medium — base 係最佳平衡
SAMPLE_RATE = 16000
SIGNAL_FILE = '/tmp/whispervoice_record'
MODEL_PATH = os.path.expanduser('~/.whispervoice_model')

# ── Load model (downloads once ~150MB, then cached) ───────────────────
print('Loading Whisper model...')
_model = None

def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(MODEL_SIZE, device='cpu', compute_type='int8',
                              download_root=MODEL_PATH)
    return _model

# ── Audio recorder ────────────────────────────────────────────────────
class Recorder:
    def __init__(self):
        self.frames = []
        self.running = False

    def start(self):
        self.frames = []
        self.running = True
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype='float32',
            callback=self._cb)
        self.stream.start()

    def _cb(self, indata, frames, t, status):
        if self.running:
            self.frames.append(indata.copy())

    def stop(self):
        self.running = False
        self.stream.stop()
        self.stream.close()
        if not self.frames:
            return None
        audio = np.concatenate(self.frames, axis=0).flatten()
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        with wave.open(tmp.name, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())
        return tmp.name

# ── Transcribe ────────────────────────────────────────────────────────
def transcribe(path):
    model = get_model()
    segments, info = model.transcribe(path, beam_size=5)
    text = ' '.join(s.text.strip() for s in segments)
    lang = info.language
    os.unlink(path)
    return text.strip(), lang

# ── Type text into focused app ────────────────────────────────────────
def type_text(text):
    safe = text.replace('\\', '\\\\').replace('"', '\\"')
    subprocess.run(['osascript', '-e',
        f'tell application "System Events" to keystroke "{safe}"'])

def notify(title, msg):
    subprocess.run(['osascript', '-e',
        f'display notification "{msg}" with title "{title}" sound name "Ping"'])

# ── Menubar App ───────────────────────────────────────────────────────
class WhisperVoiceApp(rumps.App):
    def __init__(self):
        super().__init__('🎤', quit_button=None)
        self.recorder = Recorder()
        self.recording = False
        self.status_item = rumps.MenuItem('Ready — press F5 to record')
        self.menu = [
            self.status_item,
            None,
            rumps.MenuItem('⏺  Record Now', callback=self.toggle_record),
            None,
            rumps.MenuItem('Model: base (auto-detects language)'),
            None,
            rumps.MenuItem('Quit', callback=rumps.quit_application),
        ]
        # Watch for F5 signal file
        t = threading.Thread(target=self._watch_signal, daemon=True)
        t.start()
        # Pre-load model in background
        threading.Thread(target=get_model, daemon=True).start()

    def _watch_signal(self):
        # Polls for signal file created by F5 Automator shortcut
        was_present = False
        while True:
            present = os.path.exists(SIGNAL_FILE)
            if present and not was_present:
                self._start_recording()
            elif not present and was_present and self.recording:
                self._stop_and_transcribe()
            was_present = present
            time.sleep(0.05)

    def toggle_record(self, _):
        if self.recording:
            if os.path.exists(SIGNAL_FILE):
                os.remove(SIGNAL_FILE)
        else:
            open(SIGNAL_FILE, 'w').close()

    def _start_recording(self):
        if self.recording:
            return
        self.recording = True
        self.title = '🔴'
        self.status_item.title = 'Recording... speak now'
        self.recorder.start()

    def _stop_and_transcribe(self):
        if not self.recording:
            return
        self.recording = False
        self.title = '⏳'
        self.status_item.title = 'Transcribing...'
        audio_path = self.recorder.stop()

        def process():
            if not audio_path:
                self.title = '🎤'
                self.status_item.title = 'Ready — press F5 to record'
                return
            try:
                text, lang = transcribe(audio_path)
                lang_map = {
                    'en': '🇬🇧 English',
                    'zh': '🇨🇳 Chinese',
                    'yue': '🀄 Cantonese',
                }
                lang_label = lang_map.get(lang, f'🌐 {lang}')
                self.title = '🎤'
                self.status_item.title = f'{lang_label} — ready'
                if text:
                    type_text(text)
                    notify(lang_label, text[:80])
            except Exception as e:
                self.title = '🎤'
                notify('WhisperVoice Error', str(e)[:80])

        threading.Thread(target=process, daemon=True).start()

if __name__ == '__main__':
    app = WhisperVoiceApp()
    app.run()
