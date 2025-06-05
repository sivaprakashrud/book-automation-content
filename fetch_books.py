import requests
import time
import random
from typing import List, Dict
from bs4 import BeautifulSoup


def fetch_books_from_google_books(query: str = "self-help", max_results: int = 5) -> List[Dict]:
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        books = []
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            books.append({
                'title': volume_info.get('title', 'No Title'),
                'authors': volume_info.get('authors', ['Unknown']),
                'description': volume_info.get('description', 'No Description')
            })
        return books
    except Exception as e:
        print(f"Google Books fetch failed: {e}")
        return []


def fetch_books_from_gutenberg(query: str = "self-help", max_results: int = 5) -> List[Dict]:
    base_url = "https://www.gutenberg.org/ebooks/search/?query="
    search_url = f"{base_url}{query.replace(' ', '+')}"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        book_elements = soup.select("li.booklink")[:max_results]

        books = []
        for book in book_elements:
            title = book.select_one("span.title").text.strip() if book.select_one("span.title") else "No Title"
            author = book.select_one("span.subtitle").text.strip() if book.select_one("span.subtitle") else "Unknown"
            books.append({
                'title': title,
                'authors': [author],
                'description': f"Project Gutenberg eBook titled '{title}' by {author}"
            })
        return books
    except Exception as e:
        print(f"Gutenberg fetch failed: {e}")
        return []


def fetch_books(query: str = "self-help", max_results: int = 5) -> List[Dict]:
    print("Fetching books from multiple sources...")
    books = []

    google_books = fetch_books_from_google_books(query, max_results)
    gutenberg_books = fetch_books_from_gutenberg(query, max_results)

    books.extend(google_books)
    books.extend(gutenberg_books)

    # De-duplicate by title
    unique_titles = set()
    filtered_books = []
    for book in books:
        if book['title'] not in unique_titles:
            filtered_books.append(book)
            unique_titles.add(book['title'])

    print(f"✅ Total books fetched: {len(filtered_books)}")
    return filtered_books[:max_results]  # Return only the top n unique books
