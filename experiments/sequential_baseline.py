"""
experiments/sequential_baseline.py
==================================
Sequential baseline со реални податоци
"""

import time
from typing import List, Tuple
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.classification.pipeline import ClassificationPipeline
from src.utils.data_structures import FileMetadata, ClassificationResult


def run_sequential_experiment(files: List[FileMetadata]) -> Tuple[List[ClassificationResult], float]:
    """
    Sequential baseline - процесира датотеки една по една

    Args:
        files: Lista na FileMetadata objekti

    Returns:
        (results, execution_time)
    """
    print(f"\n🔄 Sequential Baseline ({len(files)} files)...")

    pipeline = ClassificationPipeline()

    start_time = time.time()
    results = []

    for i, file_meta in enumerate(files):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(files)}", end='\r')

        result = pipeline.classify_file(file_meta)
        results.append(result)

    elapsed_time = time.time() - start_time

    print(f"\n  ✓ Time: {elapsed_time:.2f}s")
    print(f"  ✓ Throughput: {len(files)/elapsed_time:.2f} files/s")

    return results, elapsed_time


if __name__ == "__main__":
    # Test
    from real_file_loader import RealFileLoader

    loader = RealFileLoader()
    files = loader.load_from_directory('datasets/govdocs1/000', max_files=10)

    results, time_taken = run_sequential_experiment(files)
    print(f"Classified {len(results)} files in {time_taken:.2f}s")