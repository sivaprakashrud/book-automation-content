import os
import json
import re
import sys
import subprocess
import requests
from datetime import datetime

# --- Configuration ---
DATA_DIR = "data"
SUMMARY_FILE = os.path.join(DATA_DIR, "summaries.json")
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

# Hypothetical credentials for AI video generation.
AI_VIDEO_API_ENDPOINT = "https://api.example-ai-video.com/generate"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

# Instagram Reel constraints
ASPECT_RATIO = "9:16"
MAX_DURATION = 60  # seconds

# --- Helper Functions ---
def safe_name(txt: str) -> str:
    return re.sub(r'[\\/*?:"<>|()\']', "", txt.replace(" ", "_"))

def load_summary():
    if not os.path.exists(SUMMARY_FILE):
        print("[ERROR] summaries.json not found. Run summarize.py first.")
        sys.exit(1)
    with open(SUMMARY_FILE, encoding="utf-8") as f:
        books = json.load(f)
    if not books:
        print("[WARN] summaries.json is empty.")
        sys.exit(1)
    # For demonstration, we will use the first book's first summary.
    book = books[0]
    title = book.get("title", "Untitled")
    transcript = book.get("summaries", [""])[0].strip()
    if not transcript:
        transcript = "No transcript available."
    return title, transcript

def generate_ai_video(text_prompt: str, aspect_ratio: str = "9:16", duration: int = 60) -> str:
    """
    Send a text prompt to the AI video generation API.
    Returns the URL to the generated video (or downloads/saves the video locally).
    
    Note: This function assumes the API accepts JSON body with keys:
      - "prompt" : the text input
      - "aspect_ratio": a string like "9:16"
      - "duration": desired video duration in seconds
      
    And returns a JSON response with the key "video_url".
    """
    payload = {
        "prompt": text_prompt,
        "aspect_ratio": aspect_ratio,
        "duration": duration
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    print("[INFO] Sending request to AI video generation API...")
    response = requests.post(AI_VIDEO_API_ENDPOINT, json=payload, headers=headers)
    if response.status_code != 200:
        print("[ERROR] AI video generation API request failed:", response.text)
        sys.exit(1)
    data = response.json()
    video_url = data.get("video_url")
    if not video_url:
        print("[ERROR] API response missing video URL")
        sys.exit(1)
    print("[INFO] Video generated successfully. Video URL:", video_url)
    return video_url

def download_video(video_url: str, output_path: str):
    """
    Download the video from the provided URL and save it locally.
    """
    print(f"[INFO] Downloading video from {video_url}")
    r = requests.get(video_url, stream=True)
    if r.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[INFO] Video saved to {output_path}")
    else:
        print("[ERROR] Failed to download video:", r.text)
        sys.exit(1)

def post_to_instagram(video_path: str, caption: str):
    """
    Placeholder function for posting the video as an Instagram Reel.
    Posting to Instagram requires using the Facebook Graph API and proper authentication.
    For details, see: https://developers.facebook.com/docs/instagram-api
    """
    print(f"[INFO] Posting video {video_path} with caption: {caption}")
    # You would implement the Facebook Graph API call here.
    # For example, using requests to POST the video file along with caption with proper access tokens.
    # This example simply prints a confirmation.
    print("[INFO] Video posted to Instagram (simulated).")


# --- Main Driver ---
def main():
    title, transcript = load_summary()
    safe_title = safe_name(title)
    
    # Create a custom text prompt that explains the summary.
    # You could refine this prompt based on your summary content.
    text_prompt = f"Create an Instagram Reel scene that visually explains the following summary:\n\n{transcript}\n\nStyle: Cinematic, animated, with transitions. Format: 9:16."
    print("[INFO] Generated text prompt for AI video generation:")
    print(text_prompt)
    
    # Call the AI video generation API.
    video_url = generate_ai_video(text_prompt, aspect_ratio=ASPECT_RATIO, duration=MAX_DURATION)
    
    # Download the generated video.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{safe_title}_reel_{timestamp}.mp4"
    output_path = os.path.join(VIDEO_DIR, output_filename)
    download_video(video_url, output_path)
    
    # (Optional) You might want to add additional processing here (crop/resize)
    # For example, using FFmpeg to ensure the video is exactly 9:16.
    # This can be done via:
    # subprocess.run(["ffmpeg", "-i", output_path, "-vf", "scale=1080:1920", new_output_path])
    
    # Post to Instagram (placeholder function).
    caption = f"Check out this reel on '{title}'! Generated via AI. #AI #Reel #Summary"
    post_to_instagram(output_path, caption)

if __name__ == "__main__":
    main()
