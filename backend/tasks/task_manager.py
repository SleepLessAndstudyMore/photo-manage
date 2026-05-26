"""Async task management. Implemented in S1."""


class TaskManager:
    def __init__(self):
        pass

    def submit_task(self, task_type: str, **kwargs):
        raise NotImplementedError("S1: Task submission")


task_manager = TaskManager()
