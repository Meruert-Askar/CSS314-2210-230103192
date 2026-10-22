import os
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

SIZES = [100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000]
A = 2.5
B = 1.5
REPEATS = 3


def serial_operation(x):
    return [A * value + B for value in x]


def process_chunk(args):
    chunk, a, b = args
    return [a * value + b for value in chunk]


def parallel_operation(x, pool, workers):
    chunk_size = max(1, (len(x) + workers - 1) // workers)

    chunks = [
        x[i:i + chunk_size]
        for i in range(0, len(x), chunk_size)
    ]

    args = [(chunk, A, B) for chunk in chunks]
    results = pool.map(process_chunk, args)

    return [value for chunk in results for value in chunk]


def benchmark(function, repeats=REPEATS):
    times = []

    for _ in range(repeats):
        start = time.perf_counter()
        result = function()
        times.append(time.perf_counter() - start)

        if result:
            _ = result[-1]

    return min(times)


def main():
    workers = os.cpu_count() or 1
    results = []

    print("TASK 5: THE OVERHEAD CROSSOVER POINT")
    print(f"Available logical CPUs: {workers}")
    print(f"Repeats per test: {REPEATS}")
    print()

    with ProcessPoolExecutor(max_workers=workers) as pool:
        for n in SIZES:
            x = [float(i) for i in range(n)]

            serial_time = benchmark(lambda: serial_operation(x))
            parallel_time = benchmark(
                lambda: parallel_operation(x, pool, workers)
            )

            speedup = serial_time / parallel_time
            faster = parallel_time < serial_time

            results.append({
                "n": n,
                "serial": serial_time,
                "parallel": parallel_time,
                "speedup": speedup,
                "faster": faster,
            })

            print(
                f"N={n:>10,} | "
                f"Serial={serial_time:.6f}s | "
                f"Process pool={parallel_time:.6f}s | "
                f"Speedup={speedup:.3f}x | "
                f"{'PARALLEL FASTER' if faster else 'SERIAL FASTER'}"
            )

    crossover = None

    for i in range(1, len(results)):
        if not results[i - 1]["faster"] and results[i]["faster"]:
            crossover = (results[i - 1]["n"], results[i]["n"])
            break

    if crossover:
        crossover_text = (
            f"Crossover range: N > {crossover[0]:,} "
            f"and N <= {crossover[1]:,} (tested sizes)."
        )
    else:
        first_faster = next(
            (r["n"] for r in results if r["faster"]), None
        )
        last_slower = next(
            (r["n"] for r in reversed(results) if not r["faster"]), None
        )

        if first_faster is None:
            crossover_text = (
                "No crossover found: process pool was not faster "
                "at any tested size."
            )
        elif last_slower is None:
            crossover_text = (
                f"Process pool was faster at all tested sizes; "
                f"crossover is at or below N={first_faster:,}."
            )
        else:
            crossover_text = (
                "No direct slower-to-faster transition was observed "
                "between adjacent tested sizes. "
                f"First faster size: N={first_faster:,}; "
                f"largest slower size: N={last_slower:,}."
            )

    output_lines = [
        "TASK 5: THE OVERHEAD CROSSOVER POINT",
        f"Available logical CPUs: {workers}",
        f"Repeats per test: {REPEATS}",
        "",
        f"{'N':>12} {'Serial (s)':>14} {'Process pool (s)':>18} "
        f"{'Speedup':>12} {'Result':>18}",
        "-" * 78,
    ]

    for r in results:
        output_lines.append(
            f"{r['n']:>12,} "
            f"{r['serial']:>14.6f} "
            f"{r['parallel']:>18.6f} "
            f"{r['speedup']:>11.3f}x "
            f"{'PARALLEL FASTER' if r['faster'] else 'SERIAL FASTER':>18}"
        )

    output_lines.extend(["", crossover_text])
    with open("task5_output.txt", "w", encoding="utf-8") as file:
        file.write("\n" .join(output_lines) + "\n")
        print()
        print(crossover_text)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()