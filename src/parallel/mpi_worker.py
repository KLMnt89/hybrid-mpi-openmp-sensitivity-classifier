"""
MPI Worker Process
Requests tasks from master, processes files, returns results
"""

from typing import Callable, Any


class MPIWorker:
    """
    MPI Worker Process (Rank 1..P)

    Responsibilities:
    - Request tasks from master
    - Process tasks (classify files)
    - Send results back to master
    - Repeat until no more tasks
    """

    def __init__(self, rank: int, processing_func: Callable):
        """
        Args:
            rank: MPI rank (1..P)
            processing_func: Function to process each task
        """
        self.rank = rank
        self.processing_func = processing_func
        self.tasks_completed = 0

    def request_task(self, master):
        """
        Request next task from master (simulates MPI_Irecv)

        Args:
            master: MPIMaster instance

        Returns:
            Task or None if no more tasks
        """
        return master.get_next_task()

    def process_task(self, task: Any) -> Any:
        """
        Process a single task

        Args:
            task: Task to process

        Returns:
            Processed result
        """
        result = self.processing_func(task)
        self.tasks_completed += 1
        return result

    def send_result(self, master, result: Any):
        """
        Send result to master (simulates MPI_Isend)

        Args:
            master: MPIMaster instance
            result: Processed result
        """
        master.receive_result(result)

    def run(self, master):
        """
        Main worker loop: request task -> process -> send result -> repeat

        Args:
            master: MPIMaster instance
        """
        while True:
            # Request task from master
            task = self.request_task(master)

            # If no more tasks, worker is done
            if task is None:
                break

            # Process task
            result = self.process_task(task)

            # Send result back to master
            self.send_result(master, result)

    def get_stats(self) -> dict:
        """
        Get worker statistics

        Returns:
            dict: Worker statistics
        """
        return {
            'rank': self.rank,
            'tasks_completed': self.tasks_completed
        }