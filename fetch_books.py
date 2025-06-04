import requests
from typing import List, Dict, Optional

def fetch_books_from_google(query: str, max_results: int = 5) -> List[Dict]:
    """
    Fetch books from Google Books API.
    """
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        'q': query,
        'maxResults': max_results
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        books = []
        for item in data.get('items', []):
            volume_info = item.get('volumeInfo', {})
            books.append({
                'title': volume_info.get('title'),
                'authors': volume_info.get('authors'),
                'description': volume_info.get('description'),
                'source': 'Google Books'
            })
        return books
    except requests.RequestException as e:
        print(f"Google Books API error: {e}")
        return []

def fetch_books_from_openlibrary(query: str, max_results: int = 5) -> List[Dict]:
    """
    Fetch books from Open Library API.
    """
    url = "https://openlibrary.org/search.json"
    params = {
        'q': query,
        'limit': max_results
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        books = []
        for doc in data.get('docs', []):
            books.append({
                'title': doc.get('title'),
                'authors': doc.get('author_name'),
                'description': None,  # Open Library search API doesn't provide descriptions
                'source': 'Open Library'
            })
        return books
    except requests.RequestException as e:
        print(f"Open Library API error: {e}")
        return []

def fetch_books_from_gutenberg(query: str, max_results: int = 5) -> List[Dict]:
    """
    Fetch books from Project Gutenberg via Gutendex API.
    """
    url = "https://gutendex.com/books"
    params = {
        'search': query,
        'page': 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        books = []
        for book in data.get('results', [])[:max_results]:
            books.append({
                'title': book.get('title'),
                'authors': [author.get('name') for author in book.get('authors', [])],
                'description': None,  # Gutendex doesn't provide descriptions
                'source': 'Project Gutenberg',
                'download_url': book.get('formats', {}).get('text/plain; charset=utf-8')
            })
        return books
    except requests.RequestException as e:
        print(f"Gutendex API error: {e}")
        return []

def fetch_books(query: str, max_results: int = 5) -> List[Dict]:
    """
    Fetch books from multiple sources with fallback.
    """
    books = fetch_books_from_google(query, max_results)
    if books:
        return books
    print("Falling back to Open Library...")
    books = fetch_books_from_openlibrary(query, max_results)
    if books:
        return books
    print("Falling back to Project Gutenberg...")
    books = fetch_books_from_gutenberg(query, max_results)
    return books
import re

def clean_book_data(book: Dict, max_description_length: int = 1000) -> Dict:
    """
    Clean and truncate book fields for safe processing.
    """
    # Truncate overly long descriptions
    description = book.get('description', '')
    if description and len(description) > max_description_length:
        description = description[:max_description_length].rsplit('.', 1)[0] + "..."

    # Clean weird characters, escape sequences, etc.
    description = re.sub(r'\s+', ' ', description).replace('\\', '')

    # Safely format title and author names
    book['title'] = str(book.get('title', '')).strip()
    book['authors'] = [str(a).strip() for a in book.get('authors', [])]
    book['description'] = description.strip()

    return book
for item in data.get('items', []):
    volume_info = item.get('volumeInfo', {})
    book = {
        'title': volume_info.get('title'),
        'authors': volume_info.get('authors'),
        'description': volume_info.get('description'),
        'source': 'Google Books'
    }
    cleaned = clean_book_data(book)
    books.append(cleaned)
print(f"Processed Book: {cleaned['title']} by {cleaned['authors']}")
