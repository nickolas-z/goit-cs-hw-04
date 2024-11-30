from math import log
import time
from file_utils import (
    create_test_files_and_folders,
    find_all_files,
    Methods,
)
from thread_search import parallel_file_search_threading
from process_search import parallel_file_search_multiprocessing
import logging

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('app.log', mode='a')  # Append mode

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

stream_handler.setLevel(logging.CRITICAL)  # Only critical errors will be output to the stream
file_handler.setLevel(logging.DEBUG)  # All debug and above levels will be logged to the file

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)

def main():
    # Find test files
    print("Finding test files...")
    file_paths = find_all_files(logger=logger)
    if not file_paths:
        print("Files not found, generating...")
        file_paths = create_test_files_and_folders(
            num_files=100000, parallel_method=Methods.MULTIPROCESSING, logger=logger
        )
        print(f"Created {len(file_paths)} files")
    else:
        print(f"Found {len(file_paths)} files")

    # Keywords to search for
    keywords = ["python", "data", "algorithm"]
    print(f"\nKeywords to search: {keywords}")

    print(f"\n{'=' * 80}")
    print("Search using threads:")
    start_time = time.time()
    threading_results = parallel_file_search_threading(file_paths, keywords, logger=logger)
    threading_time = time.time() - start_time

    print("\nSearch results (Threading):")
    for keyword, locations in threading_results.items():
        print(f"{keyword}: found in {len(locations)} places")
    print(f"Execution time (Threading): {threading_time:.4f} seconds")

    print(f"\n{'=' * 80}")
    print("Search using processes:")
    start_time = time.time()
    multiprocessing_results = parallel_file_search_multiprocessing(file_paths, keywords, logger=logger)
    multiprocessing_time = time.time() - start_time

    print("\nSearch results (Multiprocessing):")
    for keyword, locations in multiprocessing_results.items():
        print(f"{keyword}: found in {len(locations)} places")
    print(f"Execution time (Multiprocessing): {multiprocessing_time:.4f} seconds")


if __name__ == "__main__":
    main()
