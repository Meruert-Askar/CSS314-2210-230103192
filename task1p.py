import os
import time
import numpy as np
from concurrent.futures import ThreadPoolExecutor

STUDENT_ID = 230103192
SIZE = 8000
LOGICAL_CORES = os.cpu_count() or 1
WORKERS = LOGICAL_CORES


def sum_rows(matrix, start, end):
    return np.sum(matrix[start:end, :])


def sum_columns(matrix, start, end):
    return np.sum(matrix[:, start:end])


def benchmark(matrix, mode):
    step = (SIZE + WORKERS - 1) // WORKERS
    ranges = [
        (start, min(start + step, SIZE))
        for start in range(0, SIZE, step)
    ]

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        if mode == "row":
            futures = [
                executor.submit(sum_rows, matrix, start, end)
                for start, end in ranges
            ]
        else:
            futures = [
                executor.submit(sum_columns, matrix, start, end)
                for start, end in ranges
            ]

        total = sum(future.result() for future in futures)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return elapsed_ms, total


def main():
    rng = np.random.default_rng(STUDENT_ID)
    matrix = rng.random((SIZE, SIZE), dtype=np.float64)

    row_time, row_sum = benchmark(matrix, "row")
    column_time, column_sum = benchmark(matrix, "column")

    penalty = column_time / row_time if row_time else float("inf")

    output = [
        "TASK 1: Row-Major vs. Column-Major Parallel Cache Traversal",
        f"Student ID: {STUDENT_ID}",
        f"Logical core count: {LOGICAL_CORES}",
        f"Matrix size: {SIZE} x {SIZE}",
        f"Data type: float64",
        f"Workers: {WORKERS}",
        "",
        f"Mode A (Row-Major): {row_time:.3f} ms",
        f"Mode B (Column-Major / Strided): {column_time:.3f} ms",
        f"Cache penalty factor (B / A): {penalty:.3f}x",
        "",
        f"Row-Major sum: {row_sum:.6f}",
        f"Column-Major sum: {column_sum:.6f}",
    ]

    result = "\n".join(output)
    print(result)

    with open("task1p_output.txt", "w", encoding="utf-8") as file:
        file.write(result + "\n")


if __name__ == "__main__":
    main()
