"""
Generate an Instagram-Reel-ready MP4 via Creatomate,
download it, and (optionally) hand it off for Instagram upload.
"""

import os, json, re, sys, time, requests
from datetime import datetime

# ────────────────────────────────────────────────────────────────
# Config & constants
# ────────────────────────────────────────────────────────────────
DATA_DIR        = "data"
SUMMARY_FILE    = os.path.join(DATA_DIR, "summaries.json")
VIDEO_DIR       = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

API_KEY         = os.getenv("CREATOMATE_API_KEY")
if not API_KEY:
    sys.exit(
        "[ERROR] Environment variable CREATOMATE_API_KEY is missing.\n"
        "Add it as a repo secret (Actions → Secrets → New) or `export` it locally."
    )

API_RENDER      = "https://api.creatomate.com/v1/renders"
POLL_INTERVAL   = 5        # seconds
MAX_DURATION    = 45       # sec for a Reel
WIDTH, HEIGHT   = 1080, 1920

# ────────────────────────────────────────────────────────────────
# Helper
# ────────────────────────────────────────────────────────────────
def safe_name(text: str) -> str:
    return re.sub(r'[\\/*?:"<>|()\']', "", text.replace(" ", "_"))

def load_summary() -> tuple[str, str]:
    if not os.path.exists(SUMMARY_FILE):
        sys.exit("[ERROR] summaries.json missing – run summarize.py first.")
    with open(SUMMARY_FILE, encoding="utf-8") as f:
        books = json.load(f)
    if not books:
        sys.exit("[ERROR] summaries.json is empty.")
    title = books[0].get("title", "Untitled")
    summary = books[0].get("summaries", [""])[0].strip() or "No summary."
    return title, summary

# ────────────────────────────────────────────────────────────────
# Creatomate API helpers  – patched to accept 202 + array payload
# ────────────────────────────────────────────────────────────────
def start_render(prompt: str) -> str:
    payload = {
        "source": {
            "output_format": "mp4",
            "width": WIDTH,
            "height": HEIGHT,
            "duration": MAX_DURATION,
            "elements": [
                {
                    "type": "video",
                    "src": "https://creatomate-static.s3.amazonaws.com/demo/video1.mp4",
                    "track": 1
                },
                {
                    "type": "text",
                    "text": prompt,
                    "position": {"x": "50%", "y": "90%"},
                    "style": {
                        "font_size": "48px",
                        "color": "#FFFFFF",
                        "text_align": "center",
                        "font_family": "Arial",
                        "shadow_color": "#000000",
                        "shadow_blur": 4
                    }
                }
            ]
        }
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.post(API_RENDER, json=payload, headers=headers, timeout=30)

    # The render service returns 202 Accepted with an ARRAY payload:
    #   [{"id": "...", "status": "planned", ...}]
    if r.status_code not in (200, 202):
        sys.exit(f"[ERROR] Creatomate render start failed "
                 f"{r.status_code}: {r.text}")

    data = r.json()
    if isinstance(data, list):          # normal case (HTTP 202)
        data = data[0]

    render_id = data.get("id")
    if not render_id:
        sys.exit(f"[ERROR] Could not find render ID in response: {data}")

    print(f"[INFO] Render queued, id={render_id}")
    return render_id
def poll_render(render_id: str) -> str:
    """
    Poll until status == finished. Returns final video URL.
    """
    url = f"{API_RENDER}/{render_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    while True:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            sys.exit(f"[ERROR] Poll failed {r.status_code}: {r.text}")
        data = r.json()
        status = data["status"]
        print(f"[INFO] Render status: {status}")
        if status == "finished":
            return data["url"]
        if status in {"failed", "cancelled"}:
            sys.exit(f"[ERROR] Render {status}: {data}")
        time.sleep(POLL_INTERVAL)

def download_file(file_url: str, out_path: str):
    print(f"[INFO] Downloading: {file_url}")
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
    print(f"[INFO] Saved to {out_path}")

# ────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────
def main():
    title, summary = load_summary()
    prompt = f"Instagram Reel visualising the summary:\n{summary}"
    render_id = start_render(prompt)
    video_url = poll_render(render_id)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = os.path.join(VIDEO_DIR, f"{safe_name(title)}_{ts}.mp4")
    download_file(video_url, out_file)

    print("[SUCCESS] Reel ready:", out_file)
    # TODO: upload via Instagram Graph API

if __name__ == "__main__":
    main()
