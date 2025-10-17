import time
from typing import Callable
import os
from functools import wraps
import numpy as np
from tabulate import tabulate




def measure_rw(fun: Callable) -> Callable:
    @wraps(fun)
    def wrapper(*args, **kwargs):
        #start_write = time.perf_counter()
        result = fun(*args, **kwargs)
        #end_write = time.perf_counter()

        #if not (isinstance(result, tuple) and len(result) == 2):
            #raise ValueError("Function must return a tuple: (file_paths, total_size)")

        file_paths, file_sizes = result
        all_write_durations = []
        for path in file_paths:
            start_write = time.perf_counter()
            result = fun(*args, **kwargs)
            end_write = time.perf_counter()
            all_write_durations.append(end_write - start_write)

        # --- READ phase ---
        all_read_durations = []
        for path in file_paths:
            start_read = time.perf_counter()
            if os.path.exists(path):
                _ = np.load(path, allow_pickle=True)
            end_read = time.perf_counter()
            all_read_durations.append(end_read - start_read)

        # --- Compute Speeds ---
        average_write_time = np.mean(all_write_durations)
        std_write_time = np.std(all_write_durations)
        median_write_time = np.median(all_write_durations)

        average_read_time = np.mean(all_read_durations)
        std_read_time = np.std(all_read_durations)
        median_read_time = np.median(all_read_durations)

        average_file_size = np.mean(file_sizes)
        std_file_size = np.std(file_sizes)
        median_file_size = np.median(file_sizes)

        # Return stats dictionary alongside the original result
        stats = {
            "function": fun.__name__,
            "num_files": len(file_paths),

            "average_size_bytes": average_file_size,
            "std_file_size": std_file_size,
            "median_file_size": median_file_size,

            "average_write_time": average_write_time,
            "std_write_time": std_write_time,
            "median_write_time": median_write_time,

            "average_read_time": average_read_time,
            "std_read_time": std_read_time,
            "median_read_time": median_read_time
        }
        
        return  stats  # ← Return only stats here to simplify DataFrame construction
    return wrapper