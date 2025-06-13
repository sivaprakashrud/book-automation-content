import os
import json
import re
import random
from gtts import gTTS

# File Paths
DATA_DIR = "data"
SUMMARY_FILE = os.path.join(DATA_DIR, "summaries.json")
VOICE_DIR = "voices"

# List of available voices (accents)
VOICES = ["en", "en-au", "en-uk", "en-us", "en-in"]

def sanitize_filename(title):
    """Remove invalid characters for file names."""
    return re.sub(r'[\\/*?:"<>|()\']', "", title.replace(" ", "_"))

def generate_voices(summary_file=SUMMARY_FILE, output_folder=VOICE_DIR):
    """Generate voice files from book summaries using random AI voices."""
    if not os.path.exists(summary_file):
        print(f"[ERROR] Summary file not found at: {summary_file}")
        return

    os.makedirs(output_folder, exist_ok=True)

    with open(summary_file, "r", encoding="utf-8") as f:
        try:
            summaries = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to load summaries file: {e}")
            return

    if not summaries:
        print("[WARN] No summaries found in file.")
        return

    for i, summary in enumerate(summaries):
        title = summary.get("title", f"untitled_{i}")
        text_list = summary.get("summaries", [])

        if not text_list:
            print(f"[WARN] No content to generate voice for: {title}")
            continue

        safe_title = sanitize_filename(title)

        for j, text in enumerate(text_list):
            if not text.strip():
                continue

            try:
                voice = random.choice(VOICES)  # ✅ Randomly select a voice
                tts = gTTS(text, lang=voice)
                voice_path = os.path.join(output_folder, f"{safe_title}_part{j+1}.mp3")
                tts.save(voice_path)
                print(f"[INFO] Saved voice file: {voice_path} (Voice: {voice})")
            except Exception as e:
                print(f"[ERROR] Failed to generate voice for {title} (Part {j+1}): {e}")

if __name__ == "__main__":
    generate_voices()
