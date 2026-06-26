# Asyncio example for sum
import asyncio
import time

N = 10_000_000
TASKS = 4

async def partial_sum(start, end):
    return sum(range(start, end))

async def calculate_sum():
    step = N // TASKS
    tasks = [partial_sum(i * step, N if i == TASKS - 1 else (i + 1) * step) for i in range(TASKS)]
    results = await asyncio.gather(*tasks)
    return sum(results)

if __name__ == "__main__":
    start = time.time()
    total = asyncio.run(calculate_sum())
    print(f"Total: {total}")
    print(f"Time: {time.time() - start:.2f} sec")
