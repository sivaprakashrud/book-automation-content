import os
from gtts import gTTS
import json
import re

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|()\']', "", title.replace(" ", "_"))

def generate_voices(summary_file="data/summaries.json", output_folder="voices"):
    os.makedirs(output_folder, exist_ok=True)

    with open(summary_file, "r", encoding="utf-8") as f:
        summaries = json.load(f)

    for i, summary in enumerate(summaries):
        text = summary.get("summary")
        title = summary.get("title", f"summary_{i+1}")
        if not text:
            print(f"[WARN] No summary found for item {title}")
            continue

        try:
            tts = gTTS(text)
            filename = f"{sanitize_filename(title)}.mp3"
            voice_path = os.path.join("voices", filename)
            tts.save(filename)
            print(f"[INFO] Saved voice file: {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to generate voice for summary {title}: {e}")
