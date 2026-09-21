"""
Задача 1 — Async / Await
==========================
Вычисление суммы чисел от 1 до N с использованием asyncio.

Особенность: asyncio — это однопоточная событийная петля (event loop).
Она отлично подходит для I/O-bound задач (сеть, файлы), но НЕ даёт
ускорения для CPU-bound вычислений в чистом виде.

Чтобы добиться параллелизма для CPU-bound работы внутри asyncio,
используем loop.run_in_executor() с ProcessPoolExecutor —
это позволяет запускать тяжёлые вычисления в отдельных процессах
и ожидать их результат асинхронно через await.
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

N_TARGET = 10_000_000_000_000
N_DEMO = 10_000_000
NUM_WORKERS = 4


def calculate_sum(start: int, end: int) -> int:
    """
    Синхронная CPU-bound функция.
    Запускается в ProcessPoolExecutor, поэтому не блокирует event loop.
    """
    return sum(range(start, end + 1))


async def async_calculate_sum(
    executor: ProcessPoolExecutor, start: int, end: int
) -> int:
    """
    Асинхронная обёртка: отправляет задачу в executor и ждёт результат.
    Пока задача выполняется в другом процессе, event loop может
    заниматься другими корутинами.
    """
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(executor, calculate_sum, start, end)
    print(f"  Воркер завершил: sum({start}..{end}) = {result}")
    return result


async def main_async(n: int = N_DEMO) -> float:
    """Запустить вычисление суммы 1..n асинхронно через ProcessPoolExecutor."""
    chunk = n // NUM_WORKERS

    print(f"[Async + ProcessPoolExecutor] {NUM_WORKERS} воркеров, N = {n:,}")
    t0 = time.perf_counter()

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        
        
        tasks = [
            async_calculate_sum(
                executor,
                i * chunk + 1,
                (i + 1) * chunk if i < NUM_WORKERS - 1 else n,
            )
            for i in range(NUM_WORKERS)
        ]
        partial_sums = await asyncio.gather(*tasks)

    elapsed = time.perf_counter() - t0
    total = sum(partial_sums)
    expected = n * (n + 1) // 2

    print(f"\n  Результат : {total:,}")
    print(f"  Ожидалось : {expected:,}")
    print(f"  Корректно : {total == expected}")
    print(f"  Время     : {elapsed:.4f} сек\n")
    return elapsed


def main(n: int = N_DEMO) -> float:
    return asyncio.run(main_async(n))


if __name__ == "__main__":
    main()
