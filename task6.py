import threading
import time

THREADS = 4
INCREMENTS = 2_000_000

counter = 0
locked_counter = 0
lock = threading.Lock()


def increment_without_lock():
    global counter

    for _ in range(INCREMENTS):
        counter += 1


def increment_with_lock():
    global locked_counter

    for _ in range(INCREMENTS):
        with lock:
            locked_counter += 1


def run_test(function):
    threads = [
        threading.Thread(target=function)
        for _ in range(THREADS)
    ]

    start = time.perf_counter()

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    return time.perf_counter() - start


def main():
    global counter, locked_counter

    expected = THREADS * INCREMENTS

    counter = 0
    no_lock_time = run_test(increment_without_lock)
    actual = counter

    lost_updates = expected - actual
    lost_percentage = max(0, lost_updates) / expected * 100

    locked_counter = 0
    lock_time = run_test(increment_with_lock)

    penalty = lock_time - no_lock_time
    penalty_percentage = (
        (lock_time / no_lock_time - 1) * 100
        if no_lock_time > 0 else 0
    )

    output = [
        "TASK 6: SYNCHRONIZATION COST & DATA LOSS",
        f"Threads: {THREADS}",
        f"Increments per thread: {INCREMENTS:,}",
        "",
        f"Expected final value: {expected:,}",
        f"Actual value without lock: {actual:,}",
        f"Lost updates: {max(0, lost_updates):,}",
        f"Lost updates percentage: {lost_percentage:.4f}%",
        f"Time without lock: {no_lock_time:.6f} seconds",
        "",
        f"Actual value with lock: {locked_counter:,}",
        f"Time with lock: {lock_time:.6f} seconds",
        f"Synchronization time penalty: {penalty:.6f} seconds",
        f"Synchronization overhead: {penalty_percentage:.2f}%",
        "",
        "Note: Python's GIL may prevent lost updates in this test.",
        "The Lock version guarantees synchronized counter updates.",
    ]

    result = "\n".join(output)
    print(result)

    with open("task6_output.txt", "w", encoding="utf-8") as file:
        file.write(result + "\n")


if __name__ == "__main__":
    main()