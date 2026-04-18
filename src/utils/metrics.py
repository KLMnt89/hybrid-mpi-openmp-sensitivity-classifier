"""
Performance Metrics
Computes speedup, efficiency, throughput for Results section
"""

from typing import List, Dict
from .data_structures import ClassificationResult, SensitivityLevel


def calculate_speedup(sequential_time: float, parallel_time: float) -> float:
    """
    Calculate speedup: S = T_sequential / T_parallel

    Args:
        sequential_time: Time for sequential execution
        parallel_time: Time for parallel execution

    Returns:
        float: Speedup factor
    """
    if parallel_time == 0:
        return 0.0
    return sequential_time / parallel_time


def calculate_efficiency(speedup: float, num_processors: int) -> float:
    """
    Calculate parallel efficiency: E = S / P

    Args:
        speedup: Speedup factor
        num_processors: Number of processors used

    Returns:
        float: Efficiency (0-1, where 1 is ideal)
    """
    if num_processors == 0:
        return 0.0
    return speedup / num_processors


def calculate_throughput(num_files: int, total_time: float) -> float:
    """
    Calculate throughput: files per second

    Args:
        num_files: Number of files processed
        total_time: Total processing time (seconds)

    Returns:
        float: Files per second
    """
    if total_time == 0:
        return 0.0
    return num_files / total_time


def calculate_classification_accuracy(results: List[ClassificationResult]) -> Dict:
    """
    Calculate classification distribution and statistics

    Args:
        results: List of classification results

    Returns:
        dict: Statistics including level distribution
    """
    level_counts = {level: 0 for level in SensitivityLevel}
    total_files = len(results)

    for result in results:
        level_counts[result.sensitivity_level] += 1

    # Calculate percentages
    distribution = {}
    for level, count in level_counts.items():
        percentage = (count / total_files * 100) if total_files > 0 else 0
        distribution[level.name] = {
            'count': count,
            'percentage': percentage
        }

    # Calculate average scores
    avg_scores = {
        'rule': sum(r.rule_score for r in results) / total_files if total_files > 0 else 0,
        'content': sum(r.content_score for r in results) / total_files if total_files > 0 else 0,
        'metadata': sum(r.metadata_score for r in results) / total_files if total_files > 0 else 0,
        'entropy': sum(r.entropy_score for r in results) / total_files if total_files > 0 else 0,
        'final': sum(r.final_score for r in results) / total_files if total_files > 0 else 0,
    }

    return {
        'distribution': distribution,
        'average_scores': avg_scores,
        'total_files': total_files
    }


def compare_approaches(results_dict: Dict[str, tuple]) -> Dict:
    """
    Compare multiple approaches (Sequential, MPI, Hybrid)

    Args:
        results_dict: Dict with approach names as keys, (results, time) tuples as values
                     Example: {'Sequential': (results, 100.5), 'Hybrid': (results, 15.2)}

    Returns:
        dict: Comparison metrics
    """
    comparison = {}

    # Get sequential baseline
    if 'Sequential' not in results_dict:
        return {'error': 'Sequential baseline required for comparison'}

    seq_results, seq_time = results_dict['Sequential']

    for approach, (results, time) in results_dict.items():
        speedup = calculate_speedup(seq_time, time)

        # Estimate number of processors from approach name
        # (This is simplified; in real code you'd track this explicitly)
        if 'Hybrid' in approach:
            num_procs = 16  # Example: 4 processes × 4 threads
        elif 'MPI' in approach:
            num_procs = 4
        else:
            num_procs = 1

        efficiency = calculate_efficiency(speedup, num_procs)
        throughput = calculate_throughput(len(results), time)

        comparison[approach] = {
            'time': time,
            'speedup': speedup,
            'efficiency': efficiency,
            'throughput': throughput,
            'files_processed': len(results)
        }

    return comparison


def format_results_table(comparison: Dict) -> str:
    """
    Format comparison results as a text table

    Args:
        comparison: Output from compare_approaches()

    Returns:
        str: Formatted table
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"{'Approach':<20} {'Time (s)':<12} {'Speedup':<10} {'Efficiency':<12} {'Throughput':<15}")
    lines.append("-" * 80)

    for approach, metrics in comparison.items():
        lines.append(
            f"{approach:<20} "
            f"{metrics['time']:<12.2f} "
            f"{metrics['speedup']:<10.2f}x "
            f"{metrics['efficiency']:<12.2%} "
            f"{metrics['throughput']:<15.2f} files/s"
        )

    lines.append("=" * 80)
    return "\n".join(lines)