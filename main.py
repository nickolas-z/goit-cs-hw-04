import os
import threading
import multiprocessing
import time
from typing import List, Dict
from file_generator import create_test_files_and_folders, Methods


def search_keywords_in_file(
    file_path: str, keywords: List[str]
) -> Dict[str, List[str]]:
    """
    Search for keywords in a specific file.
    params:
        file_path: Path to the file
        keywords: List of keywords to search for
    return:
        Dictionary of found keywords and their locations
    """

    results = {keyword: [] for keyword in keywords}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                for keyword in keywords:
                    if keyword.lower() in line.lower():
                        results[keyword].append(f"{file_path}:line {line_num}")
    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
    except IOError as e:
        print(f"IO error processing file {file_path}: {e}")

    return {k: v for k, v in results.items() if v}


def thread_search(
    files: List[str], keywords: List[str], result_dict: Dict, lock: threading.Lock
) -> Dict[str, List[str]]:
    """
    Threaded keyword search.
    params:
        files: List of files to process
        keywords: Keywords to search for
        result_dict: Shared result dictionary
        lock: Lock for thread-safe updates
    return:
        Result dictionary
    """
    thread_results = {}
    for file in files:
        file_results = search_keywords_in_file(file, keywords)
        for keyword, locations in file_results.items():
            if keyword not in thread_results:
                thread_results[keyword] = []
            thread_results[keyword].extend(locations)

    with lock:
        for keyword, locations in thread_results.items():
            if keyword not in result_dict:
                result_dict[keyword] = []
            result_dict[keyword].extend(locations)


def process_search(
    files: List[str], keywords: List[str], result_queue: multiprocessing.Queue
) -> Dict[str, List[str]]:
    """
    Multiprocessing keyword search.
    params:
        files: List of files to process
        keywords: Keywords to search for
        result_queue: Queue for passing results
    return:
        Result dictionary
    """
    process_results = {}
    for file in files:
        file_results = search_keywords_in_file(file, keywords)
        for keyword, locations in file_results.items():
            if keyword not in process_results:
                process_results[keyword] = []
            process_results[keyword].extend(locations)

    result_queue.put(process_results)


def parallel_file_search_threading(
    file_paths: List[str], keywords: List[str], num_threads: int = None
) -> Dict[str, List[str]]:
    """
    Parallel search using threads.
    params:
        file_paths: List of file paths
        keywords: Keywords to search for
        num_threads: Number of threads (default is number of CPUs)
    return:
        Result dictionary
    """
    if num_threads is None:
        num_threads = os.cpu_count()
        print(f"Number of threads: {num_threads}")

    # Split files among threads
    files_per_thread = [file_paths[i::num_threads] for i in range(num_threads)]

    result_dict = {}
    lock = threading.Lock()
    threads = []

    for thread_files in files_per_thread:
        thread = threading.Thread(
            target=thread_search, args=(thread_files, keywords, result_dict, lock)
        )
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    return result_dict


def parallel_file_search_multiprocessing(
    file_paths: List[str], keywords: List[str], num_processes: int = None
) -> Dict[str, List[str]]:
    """
    Parallel search using processes.
    params:
        file_paths: List of file paths
        keywords: Keywords to search for
        num_processes: Number of processes (default is number of CPUs)
    return:
        Result dictionary
    """
    if num_processes is None:
        num_processes = os.cpu_count()
        print(f"Number of processes: {num_processes}")

    # Split files among processes
    files_per_process = [file_paths[i::num_processes] for i in range(num_processes)]

    result_queue = multiprocessing.Queue()
    processes = []

    for process_files in files_per_process:
        process = multiprocessing.Process(
            target=process_search, args=(process_files, keywords, result_queue)
        )
        process.start()
        processes.append(process)

    # Collect results
    results = {}
    for _ in processes:
        process_result = result_queue.get()
        for keyword, locations in process_result.items():
            if keyword not in results:
                results[keyword] = []
            results[keyword].extend(locations)

    # Wait for all processes to finish
    for process in processes:
        process.join()

    return results


def main():
    # Generate test files
    print("Generating test files...")
    file_paths = create_test_files_and_folders(
        num_files=1000, parallel_method=Methods.MULTIPROCESSING
    )
    print(f"Created {len(file_paths)} files")

    # Keywords to search for
    keywords = ["python", "data", "algorithm"]

    print("\nSearch using threads:")
    start_time = time.time()
    threading_results = parallel_file_search_threading(file_paths, keywords)
    threading_time = time.time() - start_time

    print("\nSearch results (Threading):")
    for keyword, locations in threading_results.items():
        print(f"{keyword}: found in {len(locations)} places")
    print(f"Execution time (Threading): {threading_time:.4f} seconds")

    print("\nSearch using processes:")
    start_time = time.time()
    multiprocessing_results = parallel_file_search_multiprocessing(file_paths, keywords)
    multiprocessing_time = time.time() - start_time

    print("\nSearch results (Multiprocessing):")
    for keyword, locations in multiprocessing_results.items():
        print(f"{keyword}: found in {len(locations)} places")
    print(f"Execution time (Multiprocessing): {multiprocessing_time:.4f} seconds")


if __name__ == "__main__":
    main()
