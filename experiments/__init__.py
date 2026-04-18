"""
experiments/__init__.py
=======================
Experiments module za real data
"""

from .sequential_baseline import run_sequential_experiment
from .mpi_only import run_mpi_only_experiment
from .openmp_only import run_openmp_only_experiment
from .hybrid_mpi_openmp import run_hybrid_experiment

__all__ = [
    'run_sequential_experiment',
    'run_mpi_only_experiment',
    'run_openmp_only_experiment',
    'run_hybrid_experiment',
]