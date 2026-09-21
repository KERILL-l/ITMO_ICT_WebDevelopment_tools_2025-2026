"""
Задача 2 — Multiprocessing: параллельный парсинг веб-страниц
=============================================================
Каждый URL парсится в отдельном процессе.

Важно: соединения с БД нельзя передавать между процессами —
каждый процесс создаёт собственное соединение.
Для I/O-bound задач (сеть) multiprocessing даёт меньше выигрыша
чем threading, но зато полностью изолирован по памяти.
"""

import multiprocessing
import time
import requests
from bs4 import BeautifulSoup
from database import get_connection, ensure_parser_user, save_parsed_result

URLS = [
    "https://python.org",
    "https://fastapi.tiangolo.com",
    "https://docs.python.org/3/",
    "https://pypi.org",
    "https://realpython.com",
    "https://habr.com",
    "https://github.com",
    "https://stackoverflow.com",
]


def parse_and_save(url: str) -> dict:
    """
    Загрузить страницу, извлечь заголовок, сохранить в БД.
    Запускается в отдельном процессе — создаёт своё соединение с БД.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "Без заголовка"

        
        conn = get_connection()
        user_id = ensure_parser_user(conn)
        save_parsed_result(conn, user_id, title, url)
        conn.close()

        print(f"  [OK] {url} → «{title}»")
        return {"url": url, "title": title, "status": "ok"}

    except Exception as e:
        print(f"  [ERR] {url} → {e}")
        return {"url": url, "title": None, "status": f"error: {e}"}


def main() -> float:
    print(f"[Multiprocessing] Парсинг {len(URLS)} URL в {len(URLS)} процессах")
    t0 = time.perf_counter()

    with multiprocessing.Pool(processes=len(URLS)) as pool:
        results = pool.map(parse_and_save, URLS)

    elapsed = time.perf_counter() - t0
    ok = sum(1 for r in results if r["status"] == "ok")
    print(f"\n  Успешно: {ok}/{len(URLS)}, Время: {elapsed:.4f} сек\n")
    return elapsed


if __name__ == "__main__":
    main()
