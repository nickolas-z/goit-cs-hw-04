import os
import random
import string
import threading
import multiprocessing
import time
import shutil
from typing import List, Dict
from enum import Enum


class Methods(Enum):
    THREADING = "threading"
    MULTIPROCESSING = "multiprocessing"


def generate_random_text(min_words: int = 50, max_words: int = 500) -> str:
    """
    Generate random text.
    params:
        min_words: Minimum number of words
        max_words: Maximum number of words
    return:
        Generated text
    """
    words = [
        "python",
        "data",
        "algorithm",
        "machine",
        "learning",
        "artificial",
        "intelligence",
        "programming",
        "code",
        "software",
        "computer",
        "science",
        "developer",
        "technology",
        "system",
    ]

    # Additional words for variety
    random_words = [
        "".join(random.choices(string.ascii_lowercase, k=random.randint(3, 8)))
        for _ in range(50)
    ]

    # Combine main and random words
    total_words = words + random_words

    # Generate text
    num_words = random.randint(min_words, max_words)
    text_words = [random.choice(total_words) for _ in range(num_words)]

    # Add keywords with a certain probability
    for keyword in ["python", "data", "algorithm"]:
        if random.random() < 0.7:  # 70% chance to add a keyword
            text_words.append(keyword)

    return " ".join(text_words)


def create_file_thread_worker(
    base_dir: str,
    files_to_create: List[Dict[str, str]],
    result_queue: multiprocessing.Queue = None,
    lock: threading.Lock = None,
) -> List[str]:
    """
    Thread worker for creating files.
    params:
        base_dir: Base directory
        files_to_create: List of files to create
        result_queue: Queue for passing results (optional)
        lock: Lock for synchronization (optional)
    return:
        List of created file paths
    """

    created_files = []
    buffer_size = 1024 * 1024  # 1MB buffer size

    for file_info in files_to_create:
        # Full file path
        file_path = os.path.join(base_dir, file_info["subdir"], file_info["filename"])

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Generate text
        text = generate_random_text()

        # Create file with buffering
        with open(file_path, "w", encoding="utf-8") as f:
            start = 0
            while start < len(text):
                f.write(text[start:start + buffer_size])
                start += buffer_size

        created_files.append(file_path)

    # If a result queue is passed, add the result
    if result_queue is not None:
        result_queue.put(created_files)

    return created_files


def create_test_files_and_folders(
    base_dir: str = "test_search_files",
    num_files: int = 50,
    parallel_method: str = Methods.MULTIPROCESSING.value,
) -> List[str]:
    """
    Create test files and folders using parallel methods.
    params:
        base_dir: Base directory for creating files
        num_files: Number of files to generate
        parallel_method: Parallel processing method ('threading' or 'multiprocessing')
    return:
        List of created file paths
    """
    # Remove existing directory if it exists
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)

    # Create base directory
    os.makedirs(base_dir, exist_ok=True)

    # Subdirectories
    subdirs = ["subdir1", "subdir2", "subdir3"]
    nested_subdirs = ["nested1", "nested2"]

    # Prepare list of files to create
    files_to_create = []
    for i in range(num_files):
        # Randomly choose a subdirectory
        subdir_choices = [
            "",
            *subdirs,
            *[f"{subdir}/{nested}" for subdir in subdirs for nested in nested_subdirs],
        ]

        random_subdir = random.choice(subdir_choices)
        filename = f"file_{i}.txt"

        files_to_create.append({"subdir": random_subdir, "filename": filename})

    # Determine number of threads/processes
    num_workers = os.cpu_count()

    # Distribute files among threads/processes
    files_per_worker = [files_to_create[i::num_workers] for i in range(num_workers)]

    # List to store created files
    all_created_files = []

    # Choose parallel processing method
    if parallel_method == Methods.THREADING.value:
        # Multithreading method
        result_lock = threading.Lock()
        threads = []

        for worker_files in files_per_worker:
            thread = threading.Thread(
                target=create_file_thread_worker,
                args=(base_dir, worker_files),
                kwargs={"lock": result_lock},
            )
            thread.start()
            threads.append(thread)

        # Wait for threads to finish
        for thread in threads:
            thread.join()

    elif parallel_method == Methods.MULTIPROCESSING.value:
        # Multiprocessing method
        result_queue = multiprocessing.Queue()
        processes = []

        for worker_files in files_per_worker:
            process = multiprocessing.Process(
                target=create_file_thread_worker,
                args=(base_dir, worker_files, result_queue),
            )
            process.start()
            processes.append(process)

        # Collect results
        for _ in processes:
            all_created_files.extend(result_queue.get())

        # Wait for processes to finish
        for process in processes:
            process.join()

    else:
        # Sequential method as a fallback
        all_created_files = create_file_thread_worker(base_dir, files_to_create)

    return all_created_files

def find_all_files(base_dir: str = "test_search_files") -> List[str]:
    """
    Find all files in the given directory.
    params:
        base_dir: Base directory to search for files
    return:
        List of all found file paths
    """
    all_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            all_files.append(os.path.join(root, file))
    return all_files


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
    buffer_size = 1024 * 1024  # 1MB buffer size

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            line_num = 0
            while True:
                buffer = file.read(buffer_size)
                if not buffer:
                    break
                lines = buffer.splitlines(keepends=True)
                for line in lines:
                    line_num += 1
                    for keyword in keywords:
                        if keyword.lower() in line.lower():
                            results[keyword].append(f"{file_path}:line {line_num}")
    except FileNotFoundError as e:
        print(f"File not found: {file_path}")
    except IOError as e:
        print(f"IO error processing file {file_path}: {e}")

    return {k: v for k, v in results.items() if v}


def main():
    # Demonstration of parallel file creation

    for method in Methods:
        print(f"\nCreating files using method: {method}")

        start_time = time.time()
        file_paths = create_test_files_and_folders(
            num_files=1000, parallel_method=method.value
        )

        creation_time = time.time() - start_time
        print(f"Created {len(file_paths)} files in {creation_time:.4f} seconds")


if __name__ == "__main__":
    main()
