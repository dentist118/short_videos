import os
import logging
import hashlib
from moviepy.editor import (VideoFileClip, AudioFileClip, CompositeVideoClip,
                          concatenate_videoclips, TextClip, ColorClip)
from moviepy.video.fx import all as vfx
from config import VIDEO_RESOLUTION, VIDEO_FPS, FONT_FILE

# Fallback system
FALLBACK_COLORS = [
    (40, 40, 40),   # Dark gray
    (10, 20, 30),   # Dark blue
    (30, 10, 10)    # Dark red
]

def get_fallback_clip(index, duration):
    """Returns a colored background clip as fallback"""
    return ColorClip(VIDEO_RESOLUTION, color=FALLBACK_COLORS[index % 3]).set_duration(duration)

def get_video_hash(video_path):
    """Generate consistent hash for video file"""
    with open(video_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def create_text(text, duration):
    """Improved text creation with multiple fallback fonts"""
    font_options = [
        str(FONT_FILE) if FONT_FILE.exists() else None,
        'Arial-Unicode-MS',
        'Arial',
        'Courier-New',
        'Verdana',
        None  # System default
    ]
    
    for font in font_options:
        try:
            text_clip = TextClip(
                txt=text,
                fontsize=70,
                color='white',
                font=font,
                stroke_color='black',
                stroke_width=2,
                size=(1000, None),
                method='caption',
                align='center',
                kerning=2
            ).set_duration(duration)
            
            bg = ColorClip(
                size=(text_clip.w + 40, text_clip.h + 20),
                color=(0, 0, 0)
            ).set_opacity(0.6).set_duration(duration)
            
            return CompositeVideoClip([
                bg.set_position(('center', 'bottom')),
                text_clip.set_position(('center', 'bottom'))
            ])
        except Exception as e:
            logging.warning(f"Failed with font {font}: {str(e)}")
            continue
    
    logging.error("All font options failed for text")
    return ColorClip((100,100), color=(0,0,0)).set_duration(0.1)

def create_video_clip(video_path, duration):
    try:
        clip = VideoFileClip(str(video_path))
        if clip.duration > duration:
            clip = clip.subclip(0, duration)
        elif clip.duration < duration:
            clip = clip.fx(vfx.speedx, clip.duration/duration)
        
        clip = clip.resize(height=VIDEO_RESOLUTION[1])
        if clip.w > VIDEO_RESOLUTION[0]:
            clip = clip.crop(x_center=clip.w/2, width=VIDEO_RESOLUTION[0])
        
        return clip.set_position('center')
    except Exception as e:
        logging.error(f"Video clip error: {str(e)}")
        return get_fallback_clip(0, duration)

def create_video():
    with open('./outputs/line_by_line.txt', 'r', encoding='utf-8') as f:
        content = [line.strip() for line in f if line.strip()]
    
    clips = []
    used_hashes = set()
    
    for part, text in enumerate(content):
        # Audio handling
        audio_path = f'./outputs/audio/part{part}.mp3'
        if os.path.exists(audio_path):
            audioclip = AudioFileClip(audio_path)
            duration = audioclip.duration
        else:
            duration = 5
            audioclip = AudioClip(lambda t: 0, duration=duration)
        
        # Video handling with deduplication
        video_path = f'./outputs/video_clips/part{part}.mp4'
        if os.path.exists(video_path):
            try:
                current_hash = get_video_hash(video_path)
                if current_hash in used_hashes:
                    logging.warning(f"Duplicate video at part {part}")
                    video_clip = get_fallback_clip(part, duration)
                else:
                    used_hashes.add(current_hash)
                    video_clip = create_video_clip(video_path, duration)
            except Exception as e:
                logging.error(f"Video load failed for part {part}: {str(e)}")
                video_clip = get_fallback_clip(part, duration)
        else:
            video_clip = get_fallback_clip(part, duration)
        
        # Text handling
        text_clip = create_text(text, duration)
        
        # Compose final segment
        segment = CompositeVideoClip([
            video_clip,
            text_clip
        ]).set_audio(audioclip)
        clips.append(segment)
    
    if not clips:
        raise ValueError("No valid clips available for video creation")
    
    final_clip = concatenate_videoclips(clips)
    output_path = './outputs/youtube_short.mp4'
    final_clip.write_videofile(output_path, fps=VIDEO_FPS, threads=4)
    return output_path