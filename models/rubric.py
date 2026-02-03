from dataclasses import dataclass


@dataclass
class Rubric:
    id: int
    title: str
    data: list[dict]    # List of rubric criteria