"""
Utils Module
Data structures and helper functions
"""

from .data_structures import SensitivityLevel, FileMetadata, ClassificationResult
from .dataset_generator import generate_synthetic_dataset, generate_test_file
from .metrics import (
    calculate_speedup,
    calculate_efficiency,
    calculate_throughput,
    calculate_classification_accuracy,
    compare_approaches,
    format_results_table
)

__all__ = [
    'SensitivityLevel',
    'FileMetadata',
    'ClassificationResult',
    'generate_synthetic_dataset',
    'generate_test_file',
    'calculate_speedup',
    'calculate_efficiency',
    'calculate_throughput',
    'calculate_classification_accuracy',
    'compare_approaches',
    'format_results_table',
]