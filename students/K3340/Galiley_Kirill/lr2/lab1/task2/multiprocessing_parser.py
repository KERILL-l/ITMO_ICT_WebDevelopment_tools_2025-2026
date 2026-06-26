# Multiprocessing web parser
import multiprocessing
import sqlite3
import requests
from bs4 import BeautifulSoup

URLS = [
    'https://example.com',
    'https://www.python.org',
    'https://www.wikipedia.org',
    'https://www.github.com'
]

def parse_and_save(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.string if soup.title else 'No title'
    conn = sqlite3.connect('multiprocessing.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS pages (url TEXT, title TEXT)')
    c.execute('INSERT INTO pages VALUES (?, ?)', (url, title))
    conn.commit()
    conn.close()
    print(f'{url}: {title}')

import time

def main():
    start_time = time.time()
    with multiprocessing.Pool(4) as pool:
        pool.map(parse_and_save, URLS)
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")

if __name__ == '__main__':
    main()
