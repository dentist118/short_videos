import os
font_path = os.path.join(os.getcwd(), 'font.ttf')
font = font_path
import logging
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    TextClip,
    ColorClip
)
from moviepy.video.fx import all as vfx
from config import VIDEO_RESOLUTION, VIDEO_FPS

def zoom_in_image(t):
    return 1.5 + 0.1 * t

##def create_text(text, duration):
##    text_clip = TextClip(
##        txt=text,
##        fontsize=80,
##        color='yellow',
##        stroke_color='None',
##        stroke_width=0,
##        font=font,
##        method='caption',
##        size=(1000, None),
##        align='center'
##    ).set_duration(duration)
##    
##    bg = ColorClip(
##        size=(1080, 300),
##        color=(0, 0, 0)
##    ).set_opacity(0.5).set_duration(duration)
##    
##    bg = bg.set_position(('center', 1450))
##    text_clip = text_clip.set_position(('center', 1450))
##    
##    return CompositeVideoClip([bg, text_clip]).set_duration(duration)
# In video_creation.py
def create_text(text, duration):
    try:
        # Try system fonts first
        fonts_to_try = ['Arial', 'Courier', 'Times-New-Roman', 'Verdana']
        
        for font_name in fonts_to_try:
            try:
                text_clip = TextClip(
                    txt=text,
                    fontsize=60,  # Slightly smaller
                    color='white',
                    font=font_name,
                    stroke_color='black',
                    stroke_width=1,
                    size=(900, None),
                    method='caption',
                    align='center'
                )
                break
            except:
                continue
                
        bg = ColorClip(size=(1080, 150), color=(0,0,0)).set_opacity(0.7)
        return CompositeVideoClip([bg.set_position(('center', 1600)), 
                                 text_clip.set_position(('center', 1600))])
    except Exception as e:
        print(f"Text rendering failed: {str(e)}")
        return None
    
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
        logging.error(f"Error processing video clip: {str(e)}")
        return ColorClip(VIDEO_RESOLUTION, color=(0,0,0)).set_duration(duration)

def create_video():
    with open('./outputs/line_by_line.txt', 'r', encoding='utf-8') as f:
        content = f.read().split('\n')
    
    clips = []
    used_videos = set()  # Track used video files
    
    for part, text in enumerate(content):
        if not text.strip():
            continue
            
        # Audio handling
        mp3_path = f'./outputs/audio/part{part}.mp3'
        wav_path = f'./outputs/audio/part{part}.wav'
        
        if os.path.exists(mp3_path):
            audioclip = AudioFileClip(mp3_path)
            duration = audioclip.duration
        elif os.path.exists(wav_path):
            audioclip = AudioFileClip(wav_path)
            duration = audioclip.duration
        else:
            duration = 5
            audioclip = AudioClip(lambda t: 0, duration=duration)
        
        # Video handling
        video_path = f'./outputs/video_clips/part{part}.mp4'
        if os.path.exists(video_path):
            video_hash = hash(open(video_path, 'rb').read())
            if video_hash in used_videos:
                print(f"Duplicate video detected for part {part}, using fallback")
                video_clip = get_fallback_clip(part % 3)  # Rotate through 3 fallbacks
            else:
                used_videos.add(video_hash)
                video_clip = create_video_clip(video_path, duration)
        else:
            video_clip = get_fallback_clip(part % 3)
        
        # Text handling
        text_clip = create_text(text, duration)
        
        # Compose final segment
        segment = CompositeVideoClip([video_clip, text_clip]).set_audio(audioclip)
        clips.append(segment)
    
    if not clips:
        raise ValueError("No clips available for video creation")
    
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile('./outputs/youtube_short.mp4', fps=VIDEO_FPS)
