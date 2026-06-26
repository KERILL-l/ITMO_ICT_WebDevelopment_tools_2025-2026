# Threading web parser
import threading
import sqlite3
import requests
from bs4 import BeautifulSoup

URLS = [
    'https://example.com',
    'https://www.python.org',
    'https://www.wikipedia.org',
    'https://www.github.com'
]

conn = sqlite3.connect('threading.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS pages (url TEXT, title TEXT)')
conn.commit()

def parse_and_save(url):
    # Create a new connection for each thread
    conn = sqlite3.connect('threading.db')
    c = conn.cursor()
    
    try:
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'
        c.execute('INSERT INTO pages VALUES (?, ?)', (url, title))
        conn.commit()
        print(f'{url}: {title}')
    finally:
        conn.close()

import time

def main():
    start_time = time.time()
    threads = []
    for url in URLS:
        t = threading.Thread(target=parse_and_save, args=(url,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")
    conn.close()

if __name__ == '__main__':
    main()
