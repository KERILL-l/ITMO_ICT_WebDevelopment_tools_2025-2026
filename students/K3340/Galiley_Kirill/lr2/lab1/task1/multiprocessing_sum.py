# Multiprocessing example for sum
import multiprocessing
import time

N = 10_000_000
PROCS = 4

def partial_sum(start, end):
    return sum(range(start, end))

def calculate_sum():
    step = N // PROCS
    with multiprocessing.Pool(PROCS) as pool:
        tasks = [(i * step, N if i == PROCS - 1 else (i + 1) * step) for i in range(PROCS)]
        results = pool.starmap(partial_sum, tasks)
    return sum(results)

if __name__ == "__main__":
    start = time.time()
    total = calculate_sum()
    print(f"Total: {total}")
    print(f"Time: {time.time() - start:.2f} sec")
