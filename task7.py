import os
import time
import math
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

N = 30_000_000
CHUNK_SIZE = 250_000
MAX_CORES = os.cpu_count() or 1
CORE_COUNTS = sorted(set([1, min(2, MAX_CORES), MAX_CORES]))


def copy_kernel(args):
    start, end = args
    return [float(i) for i in range(start, end)]


def compute_kernel(args):
    start, end = args
    result = []
    for i in range(start, end):
        x = i * 0.000001
        result.append(math.sin(x) * math.cos(x) + math.tan(x))
    return result


def run_serial_copy():
    source = [float(i) for i in range(N)]
    target = [0.0] * N

    for i in range(N):
        target[i] = source[i]

    return target[-1]


def run_parallel(kernel, cores):
    chunks = [
        (start, min(start + CHUNK_SIZE, N))
        for start in range(0, N, CHUNK_SIZE)
    ]

    with ProcessPoolExecutor(max_workers=cores) as pool:
        results = list(pool.map(kernel, chunks))

    return results[-1][-1]


def measure(function):
    start = time.perf_counter()
    result = function()
    elapsed = time.perf_counter() - start
    return elapsed, result


def main():
    results = []
    print("TASK 7: ARITHMETIC INTENSITY VS MEMORY BOTTLENECKS")
    print(f"Elements: {N:,}")
    print(f"Available logical CPUs: {MAX_CORES}")
    print()

    for kernel_name, kernel in [
        ("Kernel A - Memory Copy", copy_kernel),
        ("Kernel B - Trigonometry", compute_kernel),
    ]:
        times = {}

        for cores in CORE_COUNTS:
            elapsed, _ = measure(lambda: run_parallel(kernel, cores))
            times[cores] = elapsed

        baseline = times[1]

        for cores in CORE_COUNTS:
            speedup = baseline / times[cores]
            efficiency = speedup / cores

            results.append({
                "kernel": kernel_name,
                "cores": cores,
                "time": times[cores],
                "speedup": speedup,
                "efficiency": efficiency,
            })

    lines = [
        "TASK 7: ARITHMETIC INTENSITY VS MEMORY BOTTLENECKS",
        f"Elements: {N:,}",
        f"Available logical CPUs: {MAX_CORES}",
        "",
        f"{'Kernel':<28} {'Cores':>7} {'Time (s)':>12} "
        f"{'Speedup':>12} {'Efficiency':>12}",
        "-" * 75,
    ]

    for row in results:
        lines.append(
            f"{row['kernel']:<28} "
            f"{row['cores']:>7} "
            f"{row['time']:>12.4f} "
            f"{row['speedup']:>11.3f}x "
            f"{row['efficiency']:>11.3f}"
        )

    memory_rows = [
        row for row in results
        if row["kernel"] == "Kernel A - Memory Copy"
    ]
    compute_rows = [
        row for row in results
        if row["kernel"] == "Kernel B - Trigonometry"
    ]

    if len(memory_rows) > 1:
        max_memory = memory_rows[-1]
        two_memory = next(
            (r for r in memory_rows if r["cores"] == 2),
            None
        )
        if two_memory and max_memory["cores"] > 2:
            if max_memory["speedup"] < two_memory["speedup"] * (
                max_memory["cores"] / 2
            ) * 0.7:
                conclusion = (
                    "Kernel A shows limited scaling at higher core counts; "
                    "memory bandwidth saturation is a possible cause."
                )
            else:
                conclusion = (
                    "Kernel A did not show strong evidence of memory "
                    "bandwidth saturation in these measurements."
                )
        else:
            conclusion = (
                "Not enough distinct core counts to determine memory "
                "bandwidth saturation reliably."
            )
    else:
        conclusion = "Not enough core-count measurements to assess scaling."

    lines.extend([
        "",
        "SCALING ANALYSIS",
        conclusion,
        "Kernel B performs more arithmetic per element and may scale "
        "differently from Kernel A.",
        "Process creation and result transfer add overhead to both tests.",
    ])
    output = "\n".join(lines)
    print(output)

    with open("task7_output.txt", "w", encoding="utf-8") as file:
        file.write(output + "\n")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()