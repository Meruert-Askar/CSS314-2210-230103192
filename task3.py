import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ITERATIONS = 5_000_000


def get_worker_count():
    if len(sys.argv) > 1:
        return int(sys.argv[1])
    return os.cpu_count() or 1


def run_unpadded(shared_counts, index):
    for _ in range(ITERATIONS):
        shared_counts[index] += 1


def run_local(counts, index):
    local_count = 0
    for _ in range(ITERATIONS):
        local_count += 1
    counts[index] = local_count


def run_benchmark(workers, function, counts):
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(function, counts, i)
            for i in range(workers)
        ]
        for future in futures:
            future.result()

    return time.perf_counter() - start


def main():
    workers = get_worker_count()

    if workers < 1:
        raise ValueError("Worker count must be at least 1")

    shared_counts = [0] * workers
    unpadded_time = run_benchmark(
        workers, run_unpadded, shared_counts
    )

    padded_counts = [0] * workers
    padded_time = run_benchmark(
        workers, run_local, padded_counts
    )

    local_counts = [0] * workers
    local_time = run_benchmark(
        workers, run_local, local_counts
    )

    expected = workers * ITERATIONS

    assert sum(shared_counts) == expected
    assert sum(padded_counts) == expected
    assert sum(local_counts) == expected

    lines = [
        "TASK 3: FALSE SHARING BENCHMARK",
        f"Workers: {workers}",
        f"Iterations per worker: {ITERATIONS:,}",
        "",
        f"{'Variant':<28} {'Wall Time (s)':>15}",
        "-" * 44,
        f"{'Unpadded Shared':<28} {unpadded_time:>15.6f}",
        f"{'Padded / Local':<28} {padded_time:>15.6f}",
        f"{'Local + final write':<28} {local_time:>15.6f}",
        "",
        f"Execution ratio (Unpadded / Padded): {unpadded_time / padded_time:.4f}x",
        f"Execution ratio (Unpadded / Local): {unpadded_time / local_time:.4f}x",
        "",
        f"Expected total increments: {expected:,}",
        f"Unpadded total: {sum(shared_counts):,}",
        f"Padded total: {sum(padded_counts):,}",
        f"Local total: {sum(local_counts):,}",
    ]

    output = "\n".join(lines)
    print(output)

    with open("task3_output.txt", "w", encoding="utf-8") as file:
        file.write(output + "\n")


if __name__ == "__main__":
    main()