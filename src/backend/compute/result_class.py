from dataclasses import dataclass


@dataclass
class ResultClass:
    problem_list: list
    task_assignments_list: list
    employees_list: list
    tasks_list: list
    dependencies_list: list
    start_times_dict: dict
