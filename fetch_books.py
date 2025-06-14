import os
import subprocess
import json

# ——————————————————————————————————————————————————————————————
# Ensure requests is installed
# ——————————————————————————————————————————————————————————————
try:
    import requests
except ImportError:
    print("[WARN] `requests` not found. Installing…")
    subprocess.check_call(["pip", "install", "requests"])
    import requests

# ——————————————————————————————————————————————————————————————
# Configuration & Paths
# ——————————————————————————————————————————————————————————————
DATA_DIR   = "data"
BOOK_PATH  = os.path.join(DATA_DIR, "books.json")

# ——————————————————————————————————————————————————————————————
# Helper: sanitize file/URL keys
# ——————————————————————————————————————————————————————————————
def clean_subject(niche: str) -> str:
    """Turn 'Productivity Hacks' → 'productivity_hacks' for the OL subject path."""
    return niche.strip().lower().replace(" ", "_")

# ——————————————————————————————————————————————————————————————
# 1) OpenLibrary: use the Subjects API for true niche relevance
# ——————————————————————————————————————————————————————————————
def fetch_from_openlibrary(niche="productivity", max_results=5):
    subj = clean_subject(niche)
    url = f"https://openlibrary.org/subjects/{subj}.json?limit={max_results}"
    print(f"[INFO] OpenLibrary ⟶ Subject search `{niche}` ({max_results})")
    books = []

    try:
        r = requests.get(url)
        r.raise_for_status()
        works = r.json().get("works", [])
    except Exception as e:
        print(f"[ERROR] OL subject fetch failed: {e}")
        works = []

    for entry in works:
        key = entry.get("key", "")
        if not key.startswith("/works/"):
            continue
        detail_url = f"https://openlibrary.org{key}.json"

        try:
            dr = requests.get(detail_url)
            dr.raise_for_status()
            data = dr.json()
        except Exception as e:
            print(f"[WARN] Failed to fetch work details {key}: {e}")
            continue

        desc = data.get("description", "No full text available.")
        if isinstance(desc, dict):
            desc = desc.get("value", desc)

        # authors: look inside the `authors` list
        authors = []
        for a in (data.get("authors") or []):
            # sometimes it's { "author": { "key": ... } }
            name = a.get("name") or a.get("author", {}).get("name")
            if name:
                authors.append(name)
        if not authors:
            authors = entry.get("authors", ["Unknown"])

        books.append({
            "title":      entry.get("title", "Untitled"),
            "authors":    authors,
            "full_text":  desc,
            "source":     "OpenLibrary"
        })

    print(f"[INFO] OpenLibrary → Retrieved {len(books)} books for `{niche}`")
    return books

# ——————————————————————————————————————————————————————————————
# 2) Gutenberg: free-text search + post-filter on title/subjects
# ——————————————————————————————————————————————————————————————
def fetch_from_gutenberg(niche="productivity", max_results=5):
    query = niche.strip()
    url   = f"https://gutendex.com/books/?search={query}&limit={max_results*3}"
    # we fetch 3× as many so we can filter down to max_results
    print(f"[INFO] Gutenberg ⟶ Search `{niche}` (fetch {max_results*3})")
    books = []

    try:
        r = requests.get(url)
        r.raise_for_status()
        results = r.json().get("results", [])
    except Exception as e:
        print(f"[ERROR] Gutenberg fetch failed: {e}")
        results = []

    # filter to those that actually mention the niche in title or subjects
    filtered = []
    for item in results:
        title   = item.get("title", "")
        subjects = item.get("subjects", [])
        if niche.lower() in title.lower() or any(niche.lower() in s.lower() for s in subjects):
            # fetch full text
            bid = item.get("id")
            txt_url = f"https://www.gutenberg.org/files/{bid}/{bid}-0.txt"
            try:
                tr = requests.get(txt_url)
                full_text = tr.text if tr.status_code == 200 else "No full text available."
            except:
                full_text = "No full text available."

            authors = [a.get("name", "Unknown") for a in item.get("authors", [])] or ["Unknown"]
            filtered.append({
                "title":     title,
                "authors":   authors,
                "full_text": full_text,
                "source":    "Project Gutenberg"
            })

        if len(filtered) >= max_results:
            break

    print(f"[INFO] Gutenberg → Retrieved {len(filtered)} books for `{niche}`")
    return filtered

# ——————————————————————————————————————————————————————————————
# 3) Save combined results
# ——————————————————————————————————————————————————————————————
def save_books(books):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(BOOK_PATH, "w", encoding="utf-8") as f:
            json.dump(books, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved {len(books)} books to {BOOK_PATH}")
    except Exception as e:
        print(f"[ERROR] Saving failed: {e}")

# ——————————————————————————————————————————————————————————————
# 4) Orchestrator
# ——————————————————————————————————————————————————————————————
def fetch_books(niche="productivity", per_source=5):
    print(f"[INFO] >>> Fetching `{niche}` books ({per_source} each source)")
    ol_books = fetch_from_openlibrary(niche, per_source)
    gut_books = fetch_from_gutenberg(niche, per_source)

    combined = ol_books + gut_books
    save_books(combined)

# ——————————————————————————————————————————————————————————————
if __name__ == "__main__":
    # Change the niche here
    fetch_books(niche="productivity", per_source=5)
