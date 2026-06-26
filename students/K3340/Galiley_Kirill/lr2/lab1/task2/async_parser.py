# Asyncio web parser
import asyncio
import aiohttp
import sqlite3
from bs4 import BeautifulSoup

URLS = [
    'https://example.com',
    'https://www.python.org',
    'https://www.wikipedia.org',
    'https://www.github.com'
]

async def parse_and_save(session, url, conn):
    async with session.get(url) as resp:
        text = await resp.text()
        soup = BeautifulSoup(text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'
        conn.execute('INSERT INTO pages VALUES (?, ?)', (url, title))
        conn.commit()
        print(f'{url}: {title}')

import asyncio
import time

async def main():
    start_time = time.time()
    conn = sqlite3.connect('async.db')
    conn.execute('CREATE TABLE IF NOT EXISTS pages (url TEXT, title TEXT)')
    async with aiohttp.ClientSession() as session:
        tasks = [parse_and_save(session, url, conn) for url in URLS]
        await asyncio.gather(*tasks)
    conn.close()
    end_time = time.time()
    print(f"Время выполнения: {end_time - start_time:.2f} секунд")

if __name__ == '__main__':
    asyncio.run(main())
