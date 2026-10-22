
import os
import time
import sys
import numpy as np
from concurrent.futures import ThreadPoolExecutor

STUDENT_ID = 230103192
SIZE = 2_000_000
WORKERS = min(4, os.cpu_count() or 1)


def serial_scan(data):
    output = np.empty_like(data)
    total = 0

    for i in range(len(data)):
        total += int(data[i])
        output[i] = total

    return output


def calculate_chunk(args):
    data, start, end = args
    chunk = data[start:end]
    output = np.cumsum(chunk, dtype=np.int64)
    return output, int(output[-1])


def parallel_scan(data):
    chunk_size = (len(data) + WORKERS - 1) // WORKERS
    ranges = [
        (start, min(start + chunk_size, len(data)))
        for start in range(0, len(data), chunk_size)
    ]

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        results = list(
            executor.map(
                calculate_chunk,
                [(data, start, end) for start, end in ranges]
            )
        )

    local_outputs = [result[0] for result in results]
    chunk_sums = [result[1] for result in results]

    offsets = [0] * len(chunk_sums)
    running_total = 0

    for i, chunk_sum in enumerate(chunk_sums):
        offsets[i] = running_total
        running_total += chunk_sum

    output = np.empty_like(data)

    for i, (start, end) in enumerate(ranges):
        output[start:end] = local_outputs[i] + offsets[i]

    return output


def main():
    rng = np.random.default_rng(STUDENT_ID)
    data = rng.integers(1, 11, size=SIZE, dtype=np.int64)

    print(f"Student ID: {STUDENT_ID}", flush=True)
    print(f"Array size: {SIZE:,}", flush=True)
    print(f"Workers: {WORKERS}", flush=True)

    print("Running serial scan...", flush=True)
    start = time.perf_counter()
    serial_output = serial_scan(data)
    serial_time = (time.perf_counter() - start) * 1000

    print("Running parallel scan...", flush=True)
    start = time.perf_counter()
    parallel_output = parallel_scan(data)
    parallel_time = (time.perf_counter() - start) * 1000

    try:
        assert parallel_output[-1] == serial_output[-1]
        verification = "PASS"
    except AssertionError:
        verification = "FAIL"

        output_text = (
            f"Serial Time (ms): {serial_time:.3f}\n"
            f"Parallel Time (ms): {parallel_time:.3f}\n"
            f"Speedup: {serial_time / parallel_time:.3f}x\n"
            f"Verification Status: {verification}\n"
        )

        print(output_text)

        with open("task3_output.txt", "w", encoding="utf-8") as file:
            file.write(output_text)

        sys.exit(1)

    speedup = serial_time / parallel_time if parallel_time else 0

    output_text = (
        "TASK 3: Prefix Scan (Step Efficiency vs. Work Efficiency)\n"
        f"Student ID: {STUDENT_ID}\n"
        f"Array size: {SIZE:,}\n"
        f"Workers: {WORKERS}\n"
        f"Serial Time (ms): {serial_time:.3f}\n"
        f"Parallel Time (ms): {parallel_time:.3f}\n"
        f"Speedup: {speedup:.3f}x\n"
        f"Verification Status: {verification}\n"
        f"Final prefix sum: {serial_output[-1]}\n"
    )

    print("\n" + output_text)

    with open("task3p_output.txt", "w", encoding="utf-8") as file:
        file.write(output_text)


if __name__ == "__main__":
    main()
