import os
import json
import re
import textwrap
from moviepy.video.VideoClip import ColorClip, TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

# Directories
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
        try:
            summaries = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to load summaries.json: {e}")
            return

    for item in summaries:
        try:
            title = item.get("title", "Untitled")
            summary = item.get("summary", "")
            if not title or not summary:
                print(f"[WARN] Missing title or summary in entry: {item}")
                continue

            print(f"[INFO] Creating video for: {title}")

            safe_title = sanitize_filename(title)
            voice_path = os.path.join(voice_dir, f"{safe_title}.mp3")

            if not os.path.exists(voice_path):
                print(f"[WARN] Voice file missing for: {title} (Expected: {voice_path})")
                continue

            # Load audio
            try:
                audioclip = AudioFileClip(voice_path)
                duration = audioclip.duration
            except Exception as audio_error:
                print(f"[ERROR] Failed to load audio file {voice_path}: {audio_error}")
                continue

            wrapped_text = "\n".join(textwrap.wrap(summary, width=60))

            # Create video background
            try:
                background = ColorClip(size=(1080, 1920), color=(30, 30, 30), duration=duration)
            except Exception as bg_error:
                print(f"[ERROR] Failed to create background clip: {bg_error}")
                continue

            # Create moving text overlay (Fixed font issue)
            try:
                txt_clip = TextClip(wrapped_text,  
                                    method='caption',
                                    size=(800, 100),  
                                    color='white',
                                    font="Arial",  # Explicitly setting a valid font
                                    font_size=40).set_duration(duration)

                # Animate text movement from left to right
                txt_clip = txt_clip.set_position(lambda t: (50*t, 500))

            except Exception as font_error:
                print(f"[WARN] Font error: {font_error} — falling back to default font.")
                try:
                    txt_clip = TextClip(wrapped_text,  
                                        method='caption',
                                        size=(800, 100),
                                        color='white',
                                        font="DejaVu-Sans",  # Fallback font
                                        font_size=40).set_duration(duration)
                    txt_clip = txt_clip.set_position(lambda t: (50*t, 500))  # Apply movement
                except Exception as fallback_error:
                    print(f"[ERROR] Final fallback failed: {fallback_error}")
                    continue

            # Final video composition
            try:
                video = CompositeVideoClip([background, txt_clip]).set_audio(audioclip)
                output_path = os.path.join(output_dir, f"{safe_title}.mp4")
                video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
                print(f"[INFO] Video saved: {output_path}")
            except Exception as video_error:
                print(f"[ERROR] Failed to create video for '{title}': {video_error}")

        except Exception as e:
            print(f"[ERROR] Unexpected error processing '{title}': {e}")

    print(f"[INFO] All videos saved to {output_dir}/")

if __name__ == "__main__":
    generate_videos()
