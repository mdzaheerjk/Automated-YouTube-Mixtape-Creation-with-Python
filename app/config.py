import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
ALLOWED_AUDIO_EXT = (".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg")
