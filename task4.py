import time
import threading
from concurrent.futures import ThreadPoolExecutor

ITEMS = 1000
WORKERS = 4
CHUNK_SIZE = 1


def workload(i):
    time.sleep(0.0001 * (i % 20))


def run_static():
    chunks = [
        list(range(i * (ITEMS // WORKERS), (i + 1) * (ITEMS // WORKERS)))
        for i in range(WORKERS)
    ]
    finish_times = [0.0] * WORKERS

    def worker(worker_id, items):
        for i in items:
            workload(i)
        finish_times[worker_id] = time.perf_counter()

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [
            executor.submit(worker, worker_id, chunks[worker_id])
            for worker_id in range(WORKERS)
        ]
        for future in futures:
            future.result()

    total_time = time.perf_counter() - start
    delta = max(finish_times) - min(finish_times)
    return total_time, delta


def run_dynamic():
    next_item = 0
    lock = threading.Lock()
    finish_times = [0.0] * WORKERS

    def worker(worker_id):
        nonlocal next_item

        while True:
            with lock:
                if next_item >= ITEMS:
                    break
                start_index = next_item
                next_item += CHUNK_SIZE

            end_index = min(start_index + CHUNK_SIZE, ITEMS)

            for i in range(start_index, end_index):
                workload(i)

        finish_times[worker_id] = time.perf_counter()

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [
            executor.submit(worker, worker_id)
            for worker_id in range(WORKERS)
        ]
        for future in futures:
            future.result()

    total_time = time.perf_counter() - start
    delta = max(finish_times) - min(finish_times)
    return total_time, delta


def main():
    static_time, static_delta = run_static()
    dynamic_time, dynamic_delta = run_dynamic()

    output = [
        "TASK 4: WORK STEALING & SCHEDULING UNDER SKEW",
        f"Items: {ITEMS}",
        f"Workers: {WORKERS}",
        f"Dynamic chunk size: {CHUNK_SIZE}",
        "",
        f"{'Strategy':<25}{'Total Time (s)':>18}{'Finish Delta (s)':>20}",
        "-" * 63,
        f"{'Static chunks':<25}{static_time:>18.6f}{static_delta:>20.6f}",
        f"{'Dynamic scheduling':<25}{dynamic_time:>18.6f}{dynamic_delta:>20.6f}",
        "",
        f"Speedup (Static / Dynamic): {static_time / dynamic_time:.4f}x",
    ]

    result = "\n".join(output)
    print(result)

    with open("task4_output.txt", "w", encoding="utf-8") as file:
        file.write(result + "\n")


if __name__ == "__main__":
    main()