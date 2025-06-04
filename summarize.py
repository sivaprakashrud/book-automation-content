from transformers import pipeline

# OLD (probably something like this)
# summarizer = pipeline("summarization")

# NEW — handles shorter input more appropriately
summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=60, min_length=10, do_sample=False)
def summarize_text(text):
    length = len(text.split())
    max_len = min(100, max(20, int(length * 1.5)))  # adaptive length
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", max_length=max_len, min_length=10, do_sample=False)
    summary = summarizer(text, truncation=True)[0]['summary_text']
    return summary
