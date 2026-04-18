"""
MPI Coordinator
Simulates MPI master-worker pattern for file distribution
"""

from typing import List, Callable, Any


class MPICoordinator:
    """
    Simulates MPI master-worker coordination

    In real implementation, this would use mpi4py:
    - Master (Rank 0) maintains task queue
    - Workers (Rank 1..P) request files on-demand
    - Non-blocking communication (MPI_Isend, MPI_Irecv)
    """

    def __init__(self, num_processes: int = 4):
        """
        Args:
            num_processes: Number of MPI processes (P)
        """
        self.num_processes = num_processes
        self.rank = 0  # Simulated rank

    def distribute_work(self, tasks: List[Any], worker_func: Callable) -> List[Any]:
        """
        Distribute tasks across workers (simulated)

        Args:
            tasks: List of tasks to process
            worker_func: Function to process each task

        Returns:
            List of results from all workers
        """
        # Split tasks into chunks for each process
        chunk_size = len(tasks) // self.num_processes
        if chunk_size == 0:
            chunk_size = 1

        chunks = [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]

        # Simulate parallel processing
        # In real MPI: each process would run this independently
        all_results = []
        for chunk in chunks:
            chunk_results = [worker_func(task) for task in chunk]
            all_results.extend(chunk_results)

        return all_results

    def gather_results(self, results: List[Any]) -> List[Any]:
        """
        Gather results from all workers (simulated MPI_Gather)

        Args:
            results: Results from workers

        Returns:
            Aggregated results
        """
        # In real MPI, this would use MPI_Gather
        return results

    def get_dynamic_workload(self, tasks: List[Any], worker_func: Callable) -> List[Any]:
        """
        Dynamic work allocation (simulates on-demand file assignment)

        Args:
            tasks: List of tasks
            worker_func: Processing function

        Returns:
            List of results
        """
        # Simulate dynamic scheduling
        # Workers request new tasks as they complete current ones
        results = []
        task_queue = list(tasks)

        while task_queue:
            # Simulate worker requesting work
            task = task_queue.pop(0)
            result = worker_func(task)
            results.append(result)

        return results