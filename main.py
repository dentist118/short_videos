from utils.script_writer import generate_script
#from utils.image_gen import generate_images
from utils.video_clip_gen import generate_video_clips as generate_media
from utils.voice_gen import generate_voices
from utils.video_creation import create_video
from config import OUTPUT_DIR
import logging
import os
#FFMPEG_BINARY = r"C:\Program Files\ffmpeg-7.1-full_build\bin\ffmpeg.exe"
#IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick\magick.exe"
os.environ["IMAGEMAGICK_BINARY"] =  r"C:\Program Files\ImageMagick\magick.exe"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(OUTPUT_DIR / 'generation.log'),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    logging.info("Starting video generation process")
    
    try:
        # Step 1: Generate script/content
        logging.info("Generating script content...")
        script_path = generate_script()
        
        # Step 2: Generate images
        logging.info("Generating images...")
        generate_media()
        
        # Step 3: Generate voiceovers
        logging.info("Generating voiceovers...")
        generate_voices()
        
        # Step 4: Create final video
        logging.info("Creating final video...")
        video_path = create_video()
        
        logging.info(f"Video generation complete! Output: {video_path}")
        return video_path
        
    except Exception as e:
        logging.error(f"Video generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
