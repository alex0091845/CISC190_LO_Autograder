from dataclasses import dataclass
from typing import Optional


@dataclass
class Submission:
    assignment_id: int
    user_id: int
    grade: Optional[str] = None
    score: Optional[float] = None
    points_possible: float = 0.0
    
    def is_complete(self) -> bool:
        return (self.grade and self.grade.lower() == "complete") or \
               (self.score and self.score >= self.points_possible)