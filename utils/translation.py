# utils/translation.py
import requests
import logging

def translate_to_english(text):
    """Fallback translation using Google Translate API"""
    try:
        if not text.strip():
            return text
            
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'ar',
            'tl': 'en',
            'dt': 't',
            'q': text
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()[0][0][0]
        
    except Exception as e:
        logging.error(f"Translation failed: {str(e)}")
        return text