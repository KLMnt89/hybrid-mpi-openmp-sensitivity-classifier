"""
MPI Master Process
Maintains task queue and distributes files to workers
Implements dynamic work allocation pattern
"""

from typing import List, Any
from collections import deque


class MPIMaster:
    """
    MPI Master Process (Rank 0)

    Responsibilities:
    - Maintain task queue Q = {f1, f2, ..., fN}
    - Assign files to workers on-demand
    - Collect results from workers
    - Aggregate final results
    """

    def __init__(self, num_workers: int):
        """
        Args:
            num_workers: Number of worker processes (P-1, excluding master)
        """
        self.num_workers = num_workers
        self.task_queue = deque()
        self.results = []
        self.completed_tasks = 0
        self.total_tasks = 0

    def load_tasks(self, tasks: List[Any]):
        """
        Load tasks into the queue

        Args:
            tasks: List of tasks (files) to process
        """
        self.task_queue = deque(tasks)
        self.total_tasks = len(tasks)
        self.completed_tasks = 0
        self.results = []

    def get_next_task(self):
        """
        Get next task from queue (simulates MPI_Isend to worker)

        Returns:
            Next task or None if queue is empty
        """
        if self.task_queue:
            return self.task_queue.popleft()
        return None

    def receive_result(self, result: Any):
        """
        Receive result from worker (simulates MPI_Irecv)

        Args:
            result: Processed result from worker
        """
        self.results.append(result)
        self.completed_tasks += 1

    def is_complete(self) -> bool:
        """
        Check if all tasks are completed

        Returns:
            bool: True if all tasks processed
        """
        return self.completed_tasks >= self.total_tasks

    def get_results(self) -> List[Any]:
        """
        Get all aggregated results

        Returns:
            List of all results
        """
        return self.results

    def get_progress(self) -> float:
        """
        Get completion progress

        Returns:
            float: Progress percentage (0-100)
        """
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100