import cohere
import csv
import os
import time
import cohere
import os

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def summarize_text(text):
    try:
        response = co.summarize(text=text, format="paragraph", model="command", length="medium")
        return response.summary
    except Exception as e:
        print(f"[ERROR] Summarization failed: {e}")
        return "Summary unavailable"
