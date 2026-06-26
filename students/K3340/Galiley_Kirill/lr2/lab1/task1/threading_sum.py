# Threading example for sum
import threading
import time

N = 10_000_000
THREADS = 4

def partial_sum(start, end, result, idx):
    result[idx] = sum(range(start, end))

def calculate_sum():
    step = N // THREADS
    threads = []
    result = [0] * THREADS
    for i in range(THREADS):
        start = i * step
        end = N if i == THREADS - 1 else (i + 1) * step
        t = threading.Thread(target=partial_sum, args=(start, end, result, i))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return sum(result)

if __name__ == "__main__":
    start = time.time()
    total = calculate_sum()
    print(f"Total: {total}")
    print(f"Time: {time.time() - start:.2f} sec")
