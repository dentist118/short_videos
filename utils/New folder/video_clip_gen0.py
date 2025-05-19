# utils/video_clip_gen.py
import requests
from pathlib import Path
from config import OUTPUT_DIR, VIDEO_CLIP_DIR
from tqdm import tqdm
import logging
import time
from utils.translation import translate_to_english
import os
# Add to imports:
import unicodedata
from config import VIDEO_RESOLUTION


# Pexels API configuration
PEXELS_API_KEY_FILE = Path(__file__).parent.parent / "pexels_secret.txt"
PEXELS_API_URL = "https://api.pexels.com/videos/search"

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
    """Download video clip from Pexels"""
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

#def search_pexels_video(english_prompt, per_page=3, min_duration=3, max_duration=10):
# Add to imports:
import unicodedata
from config import VIDEO_RESOLUTION

# Replace search_pexels_video() with:
def search_pexels_video(english_prompt, per_page=3, min_duration=3, max_duration=10):
    """Improved video search with better query handling"""
    try:
        # Clean and simplify prompt
        simplified_prompt = " ".join([
            "bioelectricity" if "bio" in english_prompt.lower() else word
            for word in english_prompt.split()[:6]  # Use first 6 words max
        ])
        
        headers = {"Authorization": load_pexels_api_key()}
##        params = {
##            "query": simplified_prompt + " science medical research",
##            "per_page": per_page,
##            "min_duration": min_duration,
##            "max_duration": max_duration,
##            "orientation": "portrait",
##            "size": "medium"  # Better quality than SD
##}
        # In video_clip_gen.py, update the search parameters:
        params = {
            "query": f"{english_prompt} crime scene historical mystery",  # Added crime-related terms
            "per_page": 5,  # Get more options
            "min_duration": 4,
            "max_duration": 10,
            "orientation": "portrait",
            "size": "medium",
            "color": "dark"  # More atmospheric for crime content
        }
        
        response = requests.get(PEXELS_API_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('videos'):
            raise ValueError("No videos found")
            
        # Prioritize HD videos
        for video in data['videos']:
            for file in video['video_files']:
                if file['quality'] in ['hd', 'sd'] and file['width'] >= 720:
                    return file['link']
        
        raise ValueError("No suitable video file found")
        
    except Exception as e:
        logging.error(f"Pexels search failed: {str(e)}")
        raise

def generate_video_clips():
    """Generate video clips for each line in the script"""
    try:
        line_file = OUTPUT_DIR / "line_by_line.txt"
        if not line_file.exists():
            raise FileNotFoundError(f"Script file not found: {line_file}")
        
        with open(line_file, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        # Create video clips directory if not exists
        VIDEO_CLIP_DIR.mkdir(parents=True, exist_ok=True)
        
        for part, prompt in enumerate(tqdm(prompts, desc="Generating video clips")):
            try:
                clip_path = VIDEO_CLIP_DIR / f"part{part}.mp4"
                if clip_path.exists():
                    continue
                
                # Translate Arabic prompt to English
                english_prompt = translate_to_english(prompt)
                logging.info(f"Translated prompt: {prompt} -> {english_prompt}")
                
                # Search and download video clip
                video_url = search_pexels_video(english_prompt)
                download_video_clip(video_url, clip_path)
                
                # Add slight delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logging.error(f'Error processing video clip [{prompt}]: {e}')
                continue
                
        return True
        
    except Exception as e:
        logging.error(f"Video clip generation failed: {str(e)}")
        raise
