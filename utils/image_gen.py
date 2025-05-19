# utils/image_gen.py
import requests
from PIL import Image
from io import BytesIO
from pathlib import Path
from config import OUTPUT_DIR, IMAGE_DIR
from tqdm import tqdm
import logging
import time
from utils.translation import translate_to_english  # New import for translation

def generate_images():
    """Generate images for each line in the script by first translating Arabic prompts to English"""
    try:
        line_file = OUTPUT_DIR / "line_by_line.txt"
        if not line_file.exists():
            raise FileNotFoundError(f"Script file not found: {line_file}")
        
        with open(line_file, 'r', encoding='utf-8') as f:
            prompts = [line.strip() for line in f if line.strip()]
        
        for part, prompt in enumerate(tqdm(prompts, desc="Generating images")):
            try:
                image_path = IMAGE_DIR / f"part{part}.jpg"
                if image_path.exists():
                    continue
                
                # Translate Arabic prompt to English
                english_prompt = translate_to_english(prompt)
                logging.info(f"Translated prompt: {prompt} -> {english_prompt}")
                
                url = f'https://image.pollinations.ai/prompt/{english_prompt}'
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                
                # Save the image
                img = Image.open(BytesIO(resp.content))
                img.save(image_path)
                
                # Add slight delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                logging.error(f'Error downloading/saving image [{prompt}]: {e}')
                continue
                
        return True
        
    except Exception as e:
        logging.error(f"Image generation failed: {str(e)}")
        raise