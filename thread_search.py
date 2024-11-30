import os
import threading
from typing import List, Dict
from file_utils import search_keywords_in_file

def thread_search(
    files: List[str], keywords: List[str], result_dict: Dict, lock: threading.Lock, logger=None
) -> Dict[str, List[str]]:
    """
    Threaded keyword search.
    params:
        files: List of files to process
        keywords: Keywords to search for
        result_dict: Shared result dictionary
        lock: Lock for thread-safe updates
        logger: Logger for logging messages
    return:
        Result dictionary
    """
    if logger:
        logger.info(f"Thread started for files: {files}")
    else:
        print(f"Thread started for files: {files}")
    thread_results = {}
    for file in files:
        try:
            file_results = search_keywords_in_file(file, keywords, logger)
            for keyword, locations in file_results.items():
                if keyword not in thread_results:
                    thread_results[keyword] = []
                thread_results[keyword].extend(locations)
        except Exception as e:
            print(f"Error processing file {file}: {e}")

    with lock:
        for keyword, locations in thread_results.items():
            if keyword not in result_dict:
                result_dict[keyword] = []
            result_dict[keyword].extend(locations)


def parallel_file_search_threading(
    file_paths: List[str], keywords: List[str], num_threads: int = None, logger=None
) -> Dict[str, List[str]]:
    """
    Parallel search using threads.
    params:
        file_paths: List of file paths
        keywords: Keywords to search for
        num_threads: Number of threads (default is number of CPUs)
        logger: Logger for logging messages
    return:
        Result dictionary
    """
    if num_threads is None:
        num_threads = os.cpu_count()
        if logger:
            logger.info(f"Number of threads: {num_threads}")
        else:
            print(f"Number of threads: {num_threads}")

    # Split files among threads
    files_per_thread = [file_paths[i::num_threads] for i in range(num_threads)]

    result_dict = {}
    lock = threading.Lock()
    threads = []

    for thread_files in files_per_thread:
        thread = threading.Thread(
            target=thread_search, args=(thread_files, keywords, result_dict, lock, logger)
        )
        thread.start()
        threads.append(thread)
        if logger:
            logger.info(f"Started thread for files: {thread_files}")
        else:
            print(f"Started thread for files: {thread_files}")

    # Wait for all threads to finish
    for thread in threads:
        thread.join()
        if logger:
            logger.info(f"Thread {thread.name} finished")
        else:
            print(f"Thread {thread.name} finished")

    return result_dict

if __name__ == "__main__":
    pass