
import os
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor

TASKS = 10_000
HASH_ROUNDS = 500
CORES = os.cpu_count() or 1
POOL_SIZES = sorted({1, max(1, CORES // 2), CORES, CORES * 2, CORES * 4, CORES * 16, 256})

DATA = b"A" * 1024


def cpu_task(task_id):
    value = DATA + str(task_id).encode()

    for _ in range(HASH_ROUNDS):
        value = hashlib.sha256(value).digest()

    return value


def run_benchmark(pool_size):
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=pool_size) as executor:
        results = list(executor.map(cpu_task, range(TASKS)))

    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, len(results)


def main():
    results = []

    print("TASK 5: THREAD OVERSUBSCRIPTION THRESHOLD")
    print(f"Logical CPU cores: {CORES}")
    print(f"Tasks: {TASKS:,}")
    print(f"Hash rounds per task: {HASH_ROUNDS}")
    print()

    for pool_size in POOL_SIZES:
        print(f"Testing pool size {pool_size}...", flush=True)
        elapsed_ms, completed = run_benchmark(pool_size)

        results.append({
            "pool": pool_size,
            "time": elapsed_ms,
            "completed": completed
        })

    baseline = next(r["time"] for r in results if r["pool"] == 1)

    worsening_pool = None
    best_time_so_far = baseline

    for result in results[1:]:
        if result["time"] > best_time_so_far:
            worsening_pool = result["pool"]
            break

        best_time_so_far = min(best_time_so_far, result["time"])

    lines = [
        "TASK 5: Thread Oversubscription Threshold",
        f"Logical CPU cores: {CORES}",
        f"Tasks: {TASKS:,}",
        f"Hash rounds per task: {HASH_ROUNDS}",
        "",
        f"{'Pool Size':>12} {'Execution Time (ms)':>22} "
        f"{'Speedup':>12} {'Status':>18}",
        "-" * 68
    ]

    for result in results:
        speedup = baseline / result["time"] if result["time"] else 0

        if result["pool"] == 1:
            status = "BASELINE"
        elif worsening_pool == result["pool"]:
            status = "WORSENING START"
        elif result["time"] < baseline:
            status = "FASTER"
        else:
            status = "SLOWER"

        lines.append(
            f"{result['pool']:>12} "
            f"{result['time']:>22.3f} "
            f"{speedup:>11.3f}x "
            f"{status:>18}"
        )

    lines.append("")

    if worsening_pool is not None:
        lines.append(
            f"First observed worsening: pool size {worsening_pool}."
        )
    else:
        lines.append(
            "No worsening point detected compared with the best "
            "previous result in the tested pool sizes."
        )

    output = "\n".join(lines)
    print("\n" + output)

    with open("task5p_output.txt", "w", encoding="utf-8") as file:
        file.write(output + "\n")


if __name__ == "__main__":
    main()
