import os
import json
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip


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
        # Define the voice file path
        voice_path = os.path.join(voice_dir, f"{title}.mp3")
        # Check if voice file exists
        if not os.path.exists(voice_path):
            print(f"[WARN] Voice file missing for: {title}")
            continue
        print(f"[INFO] Creating video for: {title}")

        try:
            print(f"[INFO] Creating video for: {title}")
            audio = AudioFileClip(voice_path)
            duration = audio.duration

            # Background
            bg = ColorClip(size=(1080, 1920), color=(240, 240, 240), duration=duration)

            # Title Text
            title_clip = TextClip(
                title,
                fontsize=70,
                color='black',
                size=(1000, None),
                method='caption',
                align='center',
            ).set_position(("center", 100)).set_duration(duration)

            # Summary Text (below title)
            summary_clip = TextClip(
                text,
                fontsize=40,
                color='black',
                size=(900, None),
                method='caption',
                align='center',
            ).set_position(("center", 300)).set_duration(duration)

            video = CompositeVideoClip([bg, title_clip, summary_clip])
            video = video.set_audio(audio)

            output_path = os.path.join(output_dir, f"{title}.mp4")
            video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        except Exception as e:
            print(f"[ERROR] Failed to create video for '{title}': {e}")

    print(f"[INFO] All videos saved to {VIDEO_DIR}/")

if __name__ == "__main__":
    generate_videos()


