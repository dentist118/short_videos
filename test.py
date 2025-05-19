from moviepy.editor import TextClip
from config import font
try:
    test = TextClip(txt="Test", fontsize=70, color='white', font=font.ttf)
    print("Font works!")
except Exception as e:
    print(f"Font error: {str(e)}")
