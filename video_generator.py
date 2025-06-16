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
MAX_WAIT_SEC   = 15 * 60   # 15-minute safety cap
DOT_INTERVAL   = 15        # seconds between “still waiting …” dots

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
    r = requests.post(
        API_RENDER + "?wait=true",    # <── wait for finished render
        json=payload,
        headers={"Authorization": f"Bearer {API_KEY}"},
        timeout=MAX_WAIT_SEC + 30     # allow socket a bit longer
    )

    if r.status_code not in (200, 202):
        sys.exit(f"[ERROR] render start failed {r.status_code}: {r.text}")

    data = r.json()
    if isinstance(data, list):
        data = data[0]

    render_id = data["id"]
    status    = data["status"]

    if status == "finished":
        print(f"[INFO] Render done instantly, id={render_id}", flush=True)
        return render_id, data["url"]

    # ───── fallback: we got 202 + planned ─────
    print(f"[INFO] Render queued (id={render_id}). Falling back to poll …",
          flush=True)
    return render_id, None


def poll_render(render_id: str) -> str:
    url = f"{API_RENDER}/{render_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    waited = 0
    while waited < MAX_WAIT_SEC:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code != 200:
            sys.exit(f"[ERROR] Poll failed {r.status_code}: {r.text}")

        data = r.json()
        status = data["status"]
        if status == "finished":
            print(f"\n[INFO] Render finished in {waited} s", flush=True)
            return data["url"]
        if status in {"failed", "cancelled"}:
            sys.exit(f"[ERROR] Render {status}: {data}")

        print(".", end="", flush=True)
        time.sleep(DOT_INTERVAL)
        waited += DOT_INTERVAL

    # safety stop
    print("\n[WARN] Max wait exceeded, cancelling render …", flush=True)
    requests.delete(url, headers=headers, timeout=10)
    sys.exit("[ERROR] Render timed-out and was cancelled")
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
