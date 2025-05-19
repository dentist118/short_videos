import pyttsx3
import os
from config import AUDIO_DIR, OUTPUT_DIR
import logging

def generate_voices():
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed percent
        engine.setProperty('volume', 0.9)  # Volume 0-1
        
        with open(OUTPUT_DIR / "line_by_line.txt", 'r', encoding='utf-8') as f:
            sentences = [line.strip() for line in f if line.strip()]
        
        for i, sentence in enumerate(sentences):
            audio_path = AUDIO_DIR / f"part{i}.mp3"
            if audio_path.exists():
                continue
                
            logging.info(f"Generating voice for sentence {i+1}/{len(sentences)}")
            engine.save_to_file(sentence, str(audio_path))
            engine.runAndWait()
            time.sleep(1)
            
        return True
        
    except Exception as e:
        logging.error(f"Voice generation failed: {str(e)}")
        raise