import os
import json
from moviepy.video.VideoClip import TextClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

SUMMARY_FILE = "data/summaries.json"
VOICE_DIR = "voices"
VIDEO_DIR = "videos"

def generate_videos():
    if not os.path.exists(SUMMARY_FILE):
        print("[ERROR] Summary file not found. Please run summarize.py first.")
        return

    os.makedirs(VIDEO_DIR, exist_ok=True)

    with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    for i, item in enumerate(summaries):
        title = item.get("title", f"Book {i+1}")
        summary = item.get("summary", "")
        audio_path = os.path.join(VOICE_DIR, f"summary_{i+1}.mp3")

        if not os.path.exists(audio_path):
            print(f"[WARNING] Voice file for '{title}' not found. Skipping.")
            continue

        print(f"[INFO] Creating video for: {title}")

        try:
            # Audio Clip
            audio = AudioFileClip(audio_path)
            duration = audio.duration

            # Background Color Clip
            background = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=duration)

            # Text Overlay
            text = TextClip(summary[:300] + "...", fontsize=48, color='white', size=(1000, None), method='caption')
            text = text.set_position('center').set_duration(duration)

            # Combine
            final = CompositeVideoClip([background, text.set_audio(audio)])

            output_path = os.path.join(VIDEO_DIR, f"summary_{i+1}.mp4")
            final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        except Exception as e:
            print(f"[ERROR] Failed to create video for '{title}': {e}")

    print(f"[INFO] All videos saved to {VIDEO_DIR}/")

if __name__ == "__main__":
    generate_videos()
