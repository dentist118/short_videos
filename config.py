import os
from pathlib import Path

##import os
IMAGEMAGICK_BINARY = os.path.join(r"C:\ImageMagick\magick.exe")


# Base directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
AUDIO_DIR = OUTPUT_DIR / "audio"
IMAGE_DIR = OUTPUT_DIR / "images"
VIDEO_CLIP_DIR = OUTPUT_DIR / "video_clips"  # New directory for video clips

# API Configuration
GEMINI_API_KEY_FILE = BASE_DIR / "gemini_secret.txt"
ELEVENLABS_API_KEY_FILE = BASE_DIR / "voice_secret.txt"
PEXELS_API_KEY_FILE = BASE_DIR / "pexels_secret.txt"  # New Pexels API key

# Video Settings
VIDEO_RESOLUTION = (1080, 1920)  # Vertical/Short format
VIDEO_FPS = 30
FONT_FILE = BASE_DIR / "font.ttf"  # Default font path
MAX_CLIP_DURATION = 8  # Maximum duration per clip in seconds
MIN_CLIP_DURATION = 3  # Minimum duration per clip in seconds

# ElevenLabs Settings
VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Default voice
VOICE_SETTINGS = {
    "stability": 0.0,
    "similarity_boost": 1.0,
    "style": 0.0,
    "use_speaker_boost": True
}

# Create directories if they don't exist
for directory in [OUTPUT_DIR, AUDIO_DIR, IMAGE_DIR, VIDEO_CLIP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
