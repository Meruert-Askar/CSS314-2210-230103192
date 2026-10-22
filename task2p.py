import math
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor

STUDENT_ID = 230103192
THREADS = 4
TOTAL_POINTS = 40_000_000
POINTS_PER_THREAD = TOTAL_POINTS // THREADS

shared_rng = random.Random(STUDENT_ID)
rng_lock = threading.Lock()


def shared_worker(points):
    inside = 0

    for _ in range(points):
        with rng_lock:
            x = shared_rng.random()
            y = shared_rng.random()

        if x * x + y * y <= 1.0:
            inside += 1

    return inside


def independent_worker(args):
    thread_index, points = args
    rng = random.Random((STUDENT_ID * 10) + thread_index)
    inside = 0

    for _ in range(points):
        x = rng.random()
        y = rng.random()

        if x * x + y * y <= 1.0:
            inside += 1

    return inside


def run_shared():
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        results = list(
            executor.map(shared_worker, [POINTS_PER_THREAD] * THREADS)
        )

    elapsed_ms = (time.perf_counter() - start) * 1000
    pi_estimate = 4.0 * sum(results) / TOTAL_POINTS

    return pi_estimate, elapsed_ms


def run_independent():
    start = time.perf_counter()

    args = [
        (i, POINTS_PER_THREAD)
        for i in range(THREADS)
    ]

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        results = list(executor.map(independent_worker, args))

    elapsed_ms = (time.perf_counter() - start) * 1000
    pi_estimate = 4.0 * sum(results) / TOTAL_POINTS

    return pi_estimate, elapsed_ms


def main():
    shared_pi, shared_time = run_shared()
    independent_pi, independent_time = run_independent()

    shared_error = abs(shared_pi - math.pi)
    independent_error = abs(independent_pi - math.pi)

    speedup = (
        shared_time / independent_time
        if independent_time > 0 else float("inf")
    )

    output = [
        "TASK 2: Pseudo-Random Generator State Bottleneck",
        f"Student ID: {STUDENT_ID}",
        f"Threads: {THREADS}",
        f"Total sample points: {TOTAL_POINTS:,}",
        "",
        "Shared PRNG:",
        f"Computed pi: {shared_pi:.10f}",
        f"Absolute error: {shared_error:.10f}",
        f"Wall time: {shared_time:.3f} ms",
        "",
        "Independent PRNG:",
        f"Computed pi: {independent_pi:.10f}",
        f"Absolute error: {independent_error:.10f}",
        f"Wall time: {independent_time:.3f} ms",
        "",
        f"Speedup (shared / independent): {speedup:.3f}x",
    ]

    result = "\n".join(output)
    print(result)

    with open("task2p_output.txt", "w", encoding="utf-8") as file:
        file.write(result + "\n")


if __name__ == "__main__":
    main()
