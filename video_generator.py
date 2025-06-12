import os
import json
import re
import textwrap
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

SUMMARY_FILE = "data/summaries.json"
VOICE_DIR = "voices"
VIDEO_DIR = "videos"

def sanitize_filename(title):
    """Remove characters not safe for file names."""
    return re.sub(r'[\\/*?:"<>|()\']', "", title.replace(" ", "_"))

def generate_videos(summary_file=SUMMARY_FILE, voice_dir=VOICE_DIR, output_dir=VIDEO_DIR):
    if not os.path.exists(summary_file):
        print("[ERROR] Summary file not found. Please run summarize.py first.")
        return

    os.makedirs(output_dir, exist_ok=True)

    with open(summary_file, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    for item in summaries:
        title = item["title"]
        summary = item["summary"]
        print(f"[INFO] Creating video for: {title}")

        safe_title = sanitize_filename(title)
        voice_path = os.path.join(voice_dir, f"{safe_title}.mp3")

        if not os.path.exists(voice_path):
            print(f"[WARN] Voice file missing for: {title} (Expected: {voice_path})")
            continue

        try:
            # Audio
            audioclip = AudioFileClip(voice_path)
            duration = audioclip.duration

            wrapped_text = "\n".join(textwrap.wrap(summary, width=60))
            
            # Video background
            background = ColorClip(size=(1080, 1920), color=(30, 30, 30), duration=duration)

            try:
                txt_clip = TextClip(txt=wrapped_text,
                                    method='caption',
                                    size=(1000, 1600),
                                    color='white',
                                    font='DejaVu-Sans',
                                    fontsize=40)
            except Exception as font_error:
                print(f"[WARN] Font error: {font_error} — falling back to default font.")
                try:
                    txt_clip = TextClip(txt=wrapped_text,
                                        method='caption',
                                        size=(1000, 1600),
                                        color='white',
                                        fontsize=40)
                except Exception as fallback_error:
                    print(f"[ERROR] Final fallback failed: {fallback_error}")
                    continue
                    
            # Final video
            video = CompositeVideoClip([background, txt_clip]).set_audio(audioclip)

            # Save to output
            output_path = os.path.join(output_dir, f"{safe_title}.mp4")
            video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')

        except Exception as e:
            print(f"[ERROR] Failed to create video for '{title}': {e}")

    print(f"[INFO] All videos saved to {output_dir}/")

if __name__ == "__main__":
    generate_videos()
