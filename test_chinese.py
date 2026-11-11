#!/usr/bin/env python3
# Quick test: record 5 seconds and transcribe
import sounddevice as sd
import numpy as np
import wave, tempfile, os, sys
sys.path.insert(0, '/Users/ming/Applications/WhisperVoice')

SAMPLE_RATE = 16000
DURATION = 5

print('Recording 5 seconds... SPEAK NOW in Chinese or English!')
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE,
               channels=1, dtype='float32')
sd.wait()
print('Done recording. Transcribing...')

tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
with wave.open(tmp.name, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes((audio.flatten() * 32767).astype(np.int16).tobytes())

from faster_whisper import WhisperModel
print('Loading model...')
model = WhisperModel('base', device='cpu', compute_type='int8',
                     download_root=os.path.expanduser('~/.whispervoice_model'))

# Key fix: do NOT pass language= so it auto-detects
segments, info = model.transcribe(tmp.name, beam_size=5)
text = ' '.join(s.text.strip() for s in segments)
os.unlink(tmp.name)

print(f'Detected language: {info.language} (confidence: {info.language_probability:.0%})')
print(f'Transcribed text: {text}')
