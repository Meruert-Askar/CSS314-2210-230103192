#!/usr/bin/env python3
import math
import multiprocessing as mp
import os
import platform
import random
import time
from array import array
from multiprocessing import shared_memory

STUDENT_ID = "230103192"
ELEMENT_COUNT = 20_000_000
PARALLEL_FRACTION = 0.95

_shared_memory = None
_values = None


def attach_shared_array(name):
    global _shared_memory, _values
    _shared_memory = shared_memory.SharedMemory(name=name)
    _values = _shared_memory.buf.cast("d")


def sum_chunk(bounds):
    start, end = bounds
    return math.fsum(_values[start:end])


def benchmark(shared_name, worker_count):
    chunk_bounds = [
        (ELEMENT_COUNT * i // worker_count, ELEMENT_COUNT * (i + 1) // worker_count)
        for i in range(worker_count)
    ]

    started = time.perf_counter()
    with mp.Pool(
        processes=worker_count,
        initializer=attach_shared_array,
        initargs=(shared_name,),
    ) as pool:
        partial_sums = pool.map(sum_chunk, chunk_bounds)

    elapsed = time.perf_counter() - started
    return math.fsum(partial_sums), elapsed


def main():
    max_cores = os.cpu_count() or 1
    worker_counts = [1, 2, 4, max_cores, max_cores * 2]

    print(f"Student ID: {STUDENT_ID}")
    print(f"OS: {platform.platform()}")
    print(f"CPU model/platform details: {platform.processor() or platform.machine()}")
    print(f"Logical cores detected: {max_cores}")
    print(f"Array elements: {ELEMENT_COUNT}")
    print(f"Worker counts: {worker_counts}")
    print()

    rng = random.Random(STUDENT_ID)
    values = array("d", (rng.random() for _ in range(ELEMENT_COUNT)))

    shm = shared_memory.SharedMemory(create=True, size=len(values) * values.itemsize)
    try:
        shm.buf[:] = values.tobytes()
        del values

        results = [benchmark(shm.name, workers) for workers in worker_counts]
        baseline_time = results[0][1]

        print(f"{'Cores':>8} | {'Wall Time (ms)':>15} | {'Speedup':>9} | {'Amdahl Upper Bound':>19}")
        print("-" * 64)

        for workers, (total, elapsed) in zip(worker_counts, results):
            speedup = baseline_time / elapsed
            amdahl_bound = 1 / ((1 - PARALLEL_FRACTION) + PARALLEL_FRACTION / workers)
            print(
                f"{workers:8d} | {elapsed * 1000:15.3f} | "
                f"{speedup:9.3f} | {amdahl_bound:19.3f}"
            )

        print(f"\nMathematical sum: {results[0][0]:.12f}")
    finally:
        shm.close()
        shm.unlink()


if name == "__main__":
    mp.freeze_support()
    main()