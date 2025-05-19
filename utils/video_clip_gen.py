# utils/video_clip_gen.py
import requests
import logging
import time
import hashlib
import json
import os
from pathlib import Path
from tqdm import tqdm

from config import OUTPUT_DIR, VIDEO_CLIP_DIR, VIDEO_RESOLUTION
from utils.translation import translate_to_english

# Pexels API
PEXELS_API_KEY_FILE = Path(__file__).parent.parent / "pexels_secret.txt"
PEXELS_API_URL = "https://api.pexels.com/videos/search"

# Persistent hash store
HASH_FILE = OUTPUT_DIR / "video_hashes.json"

def load_pexels_api_key():
    try:
        with open(PEXELS_API_KEY_FILE, 'r', encoding='utf-8') as f:
            api_key = f.read().strip()
        if not api_key:
            raise ValueError("Pexels API key is empty")
        return api_key
    except FileNotFoundError:
        logging.error("Pexels API key file not found. Please create 'pexels_secret.txt'")
        raise

def download_video_clip(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        logging.error(f"Failed to download video clip: {str(e)}")
        return False

def get_partial_video_hash(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        hasher = hashlib.md5()
        for chunk in response.iter_content(8192):
            hasher.update(chunk)
            break  # First chunk only
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Failed to hash remote video: {e}")
        return None

def load_existing_hashes():
    if HASH_FILE.exists():
        try:
            with open(HASH_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            logging.warning(f"Failed to load hash file: {e}")
    return set()

def save_hashes(hashes):
    try:
        with open(HASH_FILE, "w", encoding="utf-8") as f:
            json.dump(list(hashes), f)
    except Exception as e:
        logging.error(f"Failed to save video hashes: {e}")

def search_pexels_video(english_prompt, per_page=5, min_duration=4, max_duration=10):
    try:
        simplified_prompt = " ".join([
            "bioelectricity" if "bio" in english_prompt.lower() else word
            for word in english_prompt.split()[:6]
        ])
        headers = {"Authorization": load_pexels_api_key()}
        params = {
            "query": f"{english_prompt} crime scene historical mystery",
            "per_page": per_page,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "orientation": "portrait",
            "size": "medium",
            "color": "dark"
        }
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if not data.get('videos'):
            raise ValueError("No videos found")

        for video in data['videos']:
            for file in video['video_files']:
                if file['quality'] in ['hd', 'sd'] and file['width'] >= 720:
                    return file['link']

        raise ValueError("No suitable video file found")
    except Exception as e:
        logging.error(f"Pexels search failed: {str(e)}")
        raise

def get_existing_unique_videos():
    """Return paths to previously downloaded unique video clips"""
    return sorted([
        VIDEO_CLIP_DIR / fname for fname in os.listdir(VIDEO_CLIP_DIR)
        if fname.endswith(".mp4")
    ])

def generate_video_clips():
    try:
        line_file = OUTPUT_DIR / "line_by_line.txt"
        if not line_file.exists():
            raise FileNotFoundError(f"Script file not found: {line_file}")

        with open(line_file, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]

        VIDEO_CLIP_DIR.mkdir(parents=True, exist_ok=True)
        used_hashes = load_existing_hashes()
        reusable_videos = get_existing_unique_videos()
        fallback_index = 0

        for part, prompt in enumerate(tqdm(prompts, desc="Generating video clips")):
            try:
                clip_path = VIDEO_CLIP_DIR / f"part{part}.mp4"
                if clip_path.exists():
                    continue

                english_prompt = translate_to_english(prompt)
                logging.info(f"[Part {part}] Translated: {prompt} -> {english_prompt}")

                video_url = search_pexels_video(english_prompt)
                video_hash = get_partial_video_hash(video_url)

                if not video_hash:
                    raise ValueError("Could not generate hash from video URL")

                if video_hash in used_hashes:
                    logging.warning(f"[Part {part}] Duplicate video detected, using fallback.")
                    # Reuse a previously downloaded unique video as fallback
                    if fallback_index < len(reusable_videos):
                        fallback_clip = reusable_videos[fallback_index % len(reusable_videos)]
                        fallback_index += 1
                        fallback_target = VIDEO_CLIP_DIR / f"part{part}.mp4"
                        with open(fallback_clip, 'rb') as src, open(fallback_target, 'wb') as dst:
                            dst.write(src.read())
                        continue
                    else:
                        logging.warning(f"[Part {part}] No fallback available, skipping.")
                        continue

                if download_video_clip(video_url, clip_path):
                    used_hashes.add(video_hash)
                    logging.info(f"[Part {part}] Video downloaded and saved.")
                else:
                    raise ValueError("Download failed")

                time.sleep(1)

            except Exception as e:
                logging.error(f"[Part {part}] Error: {e}")
                # Use fallback if download or processing fails
                if fallback_index < len(reusable_videos):
                    fallback_clip = reusable_videos[fallback_index % len(reusable_videos)]
                    fallback_index += 1
                    fallback_target = VIDEO_CLIP_DIR / f"part{part}.mp4"
                    with open(fallback_clip, 'rb') as src, open(fallback_target, 'wb') as dst:
                        dst.write(src.read())
                    logging.info(f"[Part {part}] Fallback video reused from: {fallback_clip.name}")
                else:
                    logging.warning(f"[Part {part}] No fallback available for error case.")

        save_hashes(used_hashes)
        return True

    except Exception as e:
        logging.error(f"Video clip generation failed: {str(e)}")
        raise
