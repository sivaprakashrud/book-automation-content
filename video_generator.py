import os
import json
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip


SUMMARY_FILE = "data/summaries.json"
VOICE_DIR = "voices"
VIDEO_DIR = "videos"

def generate_videos(summaries, voice_dir="voices", output_dir="videos"):
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
        try:
            # Check if voice file exists
            if not os.path.exists(voice_path):
                title = item["title"]
                summary = item["summary"]
                print(f"[INFO] Creating video for: {title}")


                if not os.path.exists(voice_path):
                    print(f"[WARN] Voice file missing for: {title}")
                    continue
    
                # Audio clip
                audioclip = AudioFileClip(voice_path)
                duration = audioclip.duration
    
                # Background color
                background = ColorClip(size=(1080, 1920), color=(30, 30, 30), duration=duration)
    
                # Text overlay
                txt_clip = TextClip(summary, fontsize=40, color='white', size=(1000, 1700), method='caption')
                txt_clip = txt_clip.set_duration(duration).set_position("center")
    
                # Composite video
                video = CompositeVideoClip([background, txt_clip])
                video = video.set_audio(audioclip)
    
                # Save
                output_path = os.path.join(output_dir, f"{title}.mp4")
                video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
    
                except Exception as e:
                    print(f"[ERROR] Failed to create video for '{title}': {e}")

    print(f"[INFO] All videos saved to {VIDEO_DIR}/")

if __name__ == "__main__":
    generate_videos()
