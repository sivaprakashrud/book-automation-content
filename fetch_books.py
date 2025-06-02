import requests
from bs4 import BeautifulSoup

def fetch_books_from_gutenberg(query, max_books=5):
    url = f'https://www.gutenberg.org/ebooks/search/?query={query}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    books = soup.select('.booklink')
    links = []
    for book in books[:max_books]:
        link_tag = book.select_one('a')
        if link_tag:
            href = link_tag['href']
            book_url = f"https://www.gutenberg.org{href}.txt.utf-8"
            links.append(book_url)
    return links