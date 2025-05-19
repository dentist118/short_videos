import time
from pathlib import Path
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from config import AUDIO_DIR, OUTPUT_DIR, ELEVENLABS_API_KEY_FILE, VOICE_ID, VOICE_SETTINGS
import logging
import subprocess  # For potential audio post-processing

def load_api_key():
    try:
        with open(ELEVENLABS_API_KEY_FILE, 'r', encoding='utf-8') as f:
            api_key = f.read().strip()
        
        if not api_key:
            raise ValueError("ElevenLabs API key is empty")
            
        return api_key
        
    except FileNotFoundError:
        logging.error("ElevenLabs API key file not found. Please create 'voice_secret.txt'")
        time.sleep(5)
        exit(1)
    except Exception as e:
        logging.error(f"Failed to load ElevenLabs API key: {str(e)}")
        time.sleep(5)
        exit(1)

def generate_voices():
    """Generate voiceovers for each line in the script."""
    try:
        line_file = OUTPUT_DIR / "line_by_line.txt"
        if not line_file.exists():
            raise FileNotFoundError(f"Script file not found: {line_file}")
        
        with open(line_file, 'r', encoding='utf-8') as f:
            sentences = [line.strip() for line in f if line.strip()]
        
        client = ElevenLabs(api_key=load_api_key())
        
        for i, sentence in enumerate(sentences):
            try:
                audio_path = AUDIO_DIR / f"part{i}.mp3"
                if audio_path.exists():
                    continue
                
                logging.info(f"Generating voice for sentence {i+1}/{len(sentences)}")
                
                response = client.text_to_speech.convert(
                    voice_id=VOICE_ID,
                    optimize_streaming_latency='0',
                    output_format='mp3_22050_32',
                    text=sentence,
                    model_id='eleven_multilingual_v2',
                    voice_settings=VoiceSettings(**VOICE_SETTINGS)
                )
                
                with open(audio_path, 'wb') as f:
                    for chunk in response:
                        if chunk:
                            f.write(chunk)
                
                # Rate limit protection
                time.sleep(1)
                
                # --- Potential Audio Post-Processing (Example: Trimming Silence) ---
                # This is an example using ffmpeg (you need to install it)
                # You might need to adjust the parameters for your needs
                # try:
                #     subprocess.run([
                #         "ffmpeg",
                #         "-i", str(audio_path),
                #         "-filter:a", "silenceremove=start_periods=1:stop_periods=1:start_threshold=-60dB:stop_threshold=-60dB",
                #         "-acodec", "libmp3lame",  # Or your preferred codec
                #         str(audio_path).replace(".mp3", "_trimmed.mp3")
                #     ], check=True, capture_output=True)
                #     logging.info(f"Trimmed silence from {audio_path}")
                #     audio_path.unlink()  # Remove the original
                #     Path(str(audio_path).replace(".mp3", "_trimmed.mp3")).rename(audio_path) # Rename the trimmed file
                # except FileNotFoundError:
                #     logging.warning("ffmpeg not found. Skipping audio trimming.")
                # except subprocess.CalledProcessError as e:
                #     logging.error(f"Error trimming audio: {e.stderr.decode()}")
                
            except Exception as e:
                logging.error(f"Failed to generate voice for part {i}: {str(e)}")
                continue
                
        return True
        
    except Exception as e:
        logging.error(f"Voice generation failed: {str(e)}")
        raise
