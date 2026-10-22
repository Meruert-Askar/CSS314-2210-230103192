import threading
import time
import atomics

THREADS = 8
INCREMENTS = 1_00_000
TOTAL_OPS = THREADS * INCREMENTS


def benchmark_mutex():
    counter = 0
    lock = threading.Lock()
    start_event = threading.Event()
    ready = threading.Barrier(THREADS + 1)

    def worker():
        nonlocal counter
        ready.wait()
        start_event.wait()
        for _ in range(INCREMENTS):
            with lock:
                counter += 1

    threads = [threading.Thread(target=worker) for _ in range(THREADS)]

    for thread in threads:
        thread.start()

    ready.wait()
    start = time.perf_counter()
    start_event.set()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - start
    return counter, elapsed


def benchmark_cas():
    counter = atomics.atomic(width=4, atype=atomics.INT)
    counter.store(0)
    ready = threading.Barrier(THREADS + 1)
    start_event = threading.Event()

    def worker():
        ready.wait()
        start_event.wait()
        for _ in range(INCREMENTS):
            while True:
                current = counter.load()
                if counter.cmpxchg_strong(current, current + 1).success:
                    break

    threads = [threading.Thread(target=worker) for _ in range(THREADS)]

    for thread in threads:
        thread.start()

    ready.wait()
    start = time.perf_counter()
    start_event.set()

    for thread in threads:
        thread.join()

    elapsed = time.perf_counter() - start
    return counter.load(), elapsed


def report(name, counter, elapsed):
    throughput = TOTAL_OPS / elapsed
    print(f"{name} final counter: {counter:,}")
    print(f"{name} Execution Time: {elapsed * 1000:.3f} ms")
    print(f"{name} Throughput: {throughput:.2f} ops/sec")
    return throughput


def main():
    print("Task 6: Atomic CAS vs. Mutex")
    print(f"Threads: {THREADS}")
    print(f"Increments per thread: {INCREMENTS:,}")
    print(f"Expected counter: {TOTAL_OPS:,}\n", flush=True)

    mutex_counter, mutex_time = benchmark_mutex()
    cas_counter, cas_time = benchmark_cas()

    mutex_throughput = report("Mutex", mutex_counter, mutex_time)
    print()
    cas_throughput = report("Atomic CAS", cas_counter, cas_time)

    ratio = cas_throughput / mutex_throughput
    print(f"\nThroughput Ratio (CAS / Mutex): {ratio:.4f}")

    with open("task6p_output.txt", "w", encoding="utf-8") as file:
        file.write("Task 6: Atomic CAS vs. Mutex\n")
        file.write(f"Threads: {THREADS}\n")
        file.write(f"Increments per thread: {INCREMENTS:,}\n")
        file.write(f"Total operations: {TOTAL_OPS:,}\n\n")
        file.write(f"Mutex final counter: {mutex_counter:,}\n")
        file.write(f"Mutex Execution Time: {mutex_time * 1000:.3f} ms\n")
        file.write(f"Mutex Throughput: {mutex_throughput:.2f} ops/sec\n\n")
        file.write(f"Atomic CAS final counter: {cas_counter:,}\n")
        file.write(f"Atomic CAS Execution Time: {cas_time * 1000:.3f} ms\n")
        file.write(f"Atomic CAS Throughput: {cas_throughput:.2f} ops/sec\n\n")
        file.write(f"Throughput Ratio (CAS / Mutex): {ratio:.4f}\n")


if __name__ == "__main__":
    main()
