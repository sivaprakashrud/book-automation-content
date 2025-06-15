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

# Read your Creatomate API key from an environment variable (set this as a secret in GitHub)
CREATOMATE_API_KEY = os.getenv("CREATOMATE_API_KEY")
if not CREATOMATE_API_KEY:
    print("[ERROR] The environment variable CREATOMATE_API_KEY is not set. Please set it as a GitHub secret or in your local environment.")
    sys.exit(1)

# Updated Creatomate API endpoint for video rendering.
# Documentation: https://creatomate.com/docs/api/introduction
CREATOMATE_API_ENDPOINT = "https://api.creatomate.com/v1/renders"

# Instagram Reel constraints
ASPECT_RATIO_WIDTH = 1080
ASPECT_RATIO_HEIGHT = 1920
MAX_DURATION = 45  # seconds

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
    # For demonstration, we use the first book's first summary.
    book = books[0]
    title = book.get("title", "Untitled")
    transcript = book.get("summaries", [""])[0].strip()
    if not transcript:
        transcript = "No transcript available."
    return title, transcript

def generate_ai_video(text_prompt: str, width: int, height: int, duration: int) -> str:
    """
    Call the Creatomate API to generate a video.
    This function builds a JSON payload for a video that combines:
      - A background video element.
      - An overlay text element using the text_prompt.
    The video is rendered in a 9:16 format for Instagram Reels.
    Returns the URL of the rendered video.
    """
    payload = {
        "source": {
            "outputFormat": "mp4",
            "width": width,
            "height": height,
            "duration": duration,
            "elements": [
                # Background video element (using one of Creatomate's demo videos)
                {
                    "type": "video",
                    "src": "https://creatomate-static.s3.amazonaws.com/demo/video1.mp4",
                    "track": 1,
                },
                # Overlay text element (the prompt that explains the summary)
                {
                    "type": "text",
                    "text": text_prompt,
                    "position": {"x": "50%", "y": "90%"},
                    "style": {
                        "fontSize": "48px",
                        "color": "#FFFFFF",
                        "textAlign": "center",
                        "fontFamily": "Arial"
                    },
                },
            ],
        }
    }

    headers = {
        "Authorization": f"Bearer {CREATOMATE_API_KEY}",
        "Content-Type": "application/json"
    }

    print("[INFO] Sending request to Creatomate API...")
    response = requests.post(CREATOMATE_API_ENDPOINT, json=payload, headers=headers)
    if response.status_code != 200:
        print("[ERROR] Creatomate API request failed:", response.text)
        sys.exit(1)
    data = response.json()
    video_url = data.get("url")
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
    Posting to Instagram requires using the Facebook Graph API with proper authentication.
    For details, see: https://developers.facebook.com/docs/instagram-api
    """
    print(f"[INFO] Posting video {video_path} with caption: {caption}")
    # Implement actual Instagram posting logic (using the Graph API) here.
    print("[INFO] Video posted to Instagram (simulated).")

# --- Main Driver ---
def main():
    title, transcript = load_summary()
    safe_title = safe_name(title)
    
    # Create a text prompt that visually explains the summary.
    text_prompt = (f"Create an Instagram Reel scene that visually explains the following summary:\n\n"
                   f"{transcript}\n\n"
                   "Style: Cinematic, animated, with smooth transitions. Format: 9:16.")
    print("[INFO] Generated text prompt for Creatomate API:")
    print(text_prompt)
    
    # Call the Creatomate API.
    video_url = generate_ai_video(text_prompt, ASPECT_RATIO_WIDTH, ASPECT_RATIO_HEIGHT, MAX_DURATION)
    
    # Download the generated video.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{safe_title}_reel_{timestamp}.mp4"
    output_path = os.path.join(VIDEO_DIR, output_filename)
    download_video(video_url, output_path)
    
    # Post to Instagram (placeholder).
    caption = f"Check out this reel on '{title}'! Generated with AI. #AI #Reel #Summary"
    post_to_instagram(output_path, caption)

if __name__ == "__main__":
    main()
