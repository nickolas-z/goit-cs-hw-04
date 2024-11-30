import os
import multiprocessing
from typing import List, Dict
from file_utils import search_keywords_in_file

def process_search(
    files: List[str], keywords: List[str], result_queue: multiprocessing.Queue, logger=None
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
        try:
            if logger:
                logger.info(f"Processing file: {file}")
            else:
                print(f"Processing file: {file}")
                
            file_results = search_keywords_in_file(file, keywords, logger=logger)
            for keyword, locations in file_results.items():
                if keyword not in process_results:
                    process_results[keyword] = []
                process_results[keyword].extend(locations)
                
            if logger:
                logger.info(f"Finished processing file: {file}")
            else:
                print(f"Finished processing file: {file}")
                
        except Exception as e:
            error_message = f"Error processing file {file}: {e}"
            if logger:
                logger.error(error_message)
            else:
                print(error_message)

    result_queue.put(process_results)


def parallel_file_search_multiprocessing(
    file_paths: List[str], keywords: List[str], num_processes: int = None, logger=None
) -> Dict[str, List[str]]:
    """
    Parallel search using processes.
    params:
        file_paths: List of file paths
        keywords: Keywords to search for
        num_processes: Number of processes (default is number of CPUs)
        logger: Logger for logging messages
    return:
        Result dictionary
    """
    if num_processes is None:
        num_processes = os.cpu_count()
        if logger:
            logger.info(f"Number of processes: {num_processes}")
        else:
            print(f"Number of processes: {num_processes}")

    # Split files among processes
    files_per_process = [file_paths[i::num_processes] for i in range(num_processes)]

    result_queue = multiprocessing.Queue()
    processes = []

    for process_files in files_per_process:
        if logger:
            logger.info(f"Starting process for files: {process_files}")
        else:
            print(f"Starting process for files: {process_files}")
        process = multiprocessing.Process(
            target=process_search, args=(process_files, keywords, result_queue, logger)
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
        if logger:
            logger.info(f"Process {process.pid} finished")
        else:
            print(f"Process {process.pid} finished")

    return results

if __name__ == "__main__":
    pass
