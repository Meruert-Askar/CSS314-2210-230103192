
import os
import time
import pickle
import multiprocessing as mp
from multiprocessing import shared_memory

import numpy as np

SIZES = [100_000, 1_000_000, 10_000_000]


def pickle_worker(data_bytes, queue):
    start = time.perf_counter()
    array = pickle.loads(data_bytes)
    result = float(array[-1])
    queue.put((time.perf_counter() - start, result))


def shared_memory_worker(name, size, queue):
    start = time.perf_counter()

    shm = shared_memory.SharedMemory(name=name)
    array = np.ndarray((size,), dtype=np.float64, buffer=shm.buf)
    result = float(array[-1])

    elapsed = time.perf_counter() - start
    queue.put((elapsed, result))
    shm.close()


def benchmark_pickle(array):
    data_bytes = pickle.dumps(array, protocol=pickle.HIGHEST_PROTOCOL)
    queue = mp.Queue()

    start = time.perf_counter()
    process = mp.Process(
        target=pickle_worker,
        args=(data_bytes, queue)
    )
    process.start()

    worker_time, result = queue.get()
    process.join()
    total_time = time.perf_counter() - start

    queue.close()

    return total_time * 1000, worker_time * 1000, result


def benchmark_shared_memory(array):
    shm = shared_memory.SharedMemory(create=True, size=array.nbytes)
    queue = mp.Queue()

    try:
        shared_array = np.ndarray(
            array.shape,
            dtype=array.dtype,
            buffer=shm.buf
        )
        shared_array[:] = array

        start = time.perf_counter()
        process = mp.Process(
            target=shared_memory_worker,
            args=(shm.name, array.size, queue)
        )
        process.start()

        worker_time, result = queue.get()
        process.join()
        total_time = time.perf_counter() - start

        return total_time * 1000, worker_time * 1000, result

    finally:
        queue.close()
        shm.close()
        shm.unlink()


def main():
    output = [
        "TASK 4: Host-to-Device Transfer Penalty",
        f"CPU count: {os.cpu_count()}",
        "",
        (
            f"{'N':>12} {'Pickle Total (ms)':>20} "
            f"{'Shared Mem Total (ms)':>23} "
            f"{'Pickle Worker (ms)':>21} {'Shared Worker (ms)':>21}"
        ),
        "-" * 103,
    ]

    for n in SIZES:
        print(f"Testing N={n:,}...", flush=True)

        array = np.arange(n, dtype=np.float64)

        pickle_total, pickle_worker_time, pickle_result = (
            benchmark_pickle(array)
        )

        shared_total, shared_worker_time, shared_result = (
            benchmark_shared_memory(array)
        )

        assert pickle_result == shared_result == float(array[-1])

        output.append(
            f"{n:>12,} "
            f"{pickle_total:>20.3f} "
            f"{shared_total:>23.3f} "
            f"{pickle_worker_time:>21.3f} "
            f"{shared_worker_time:>21.3f}"
        )

    output.extend([
        "",
    ])

    result_text = "\n".join(output)
    print("\n" + result_text)

    with open("task4p_output.txt", "w", encoding="utf-8") as file:
        file.write(result_text + "\n")


if __name__ == "__main__":
    mp.freeze_support()
    main()
