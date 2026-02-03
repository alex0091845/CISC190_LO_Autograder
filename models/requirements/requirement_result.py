from typing import List


class RequirementResult:
    def __init__(self, satisfied: bool, missing: List[str] = [], completed: List[str] = []):
        self.satisfied = satisfied
        self.missing = missing or []
        self.completed = completed or []
    
    def __repr__(self):
        return f"RequirementResult(satisfied={self.satisfied}, missing={self.missing})"