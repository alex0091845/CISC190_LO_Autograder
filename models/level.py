from dataclasses import dataclass

from models.requirements.requirement_result import RequirementResult
from models.requirements.requirement_tree import RequirementTree

class Level:
    INSUFFICIENT = "insufficient"
    INTERN = "intern"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"

    @staticmethod
    def level_str_to_score(level_name: str):
        match level_name:
            case Level.INSUFFICIENT:
                return 0
            case Level.INTERN:
                return 1
            case Level.JUNIOR:
                return 2
            case Level.MIDDLE:
                return 3
            case Level.SENIOR:
                return 4
            case _:
                raise ValueError(f"Level name is not one of {Level.INTERN}, {Level.JUNIOR}, {Level.MIDDLE}, or {Level.SENIOR}")
    
    @staticmethod
    def level_score_to_str(level_score: int):
        match level_score:
            case 0:
                return Level.INSUFFICIENT
            case 1:
                return Level.INTERN
            case 2:
                return Level.JUNIOR
            case 3:
                return Level.MIDDLE
            case 4:
                return Level.SENIOR
            case _:
                raise ValueError(f"Level score is not one of 0, 1, 2, 3, or 4")

    def __init__(self,
                 id: int=-1,
                 name: str="",
                 requirements: RequirementTree | None=None):
        self.id: int = id
        self.name: str = name
        self.requirements: RequirementTree | None = requirements

        self.satisfied: bool = False     # stores a satisfied result from the latest run
        self.evaluated: bool = False
        self.cached_result: RequirementResult | None = None

    @staticmethod
    def from_yaml(yaml: dict):
        """Creates a Level from a YAML string.
        Args:
            yaml: The yaml string.
        Returns:
            Level object.
        """
        if "level" not in yaml:
            raise ValueError("YAML does not contain 'level' key.")

        level = Level()
        level.name = yaml["level"]

        tree = RequirementTree.from_yaml(yaml)
        level.requirements = tree

        return level

    def evaluate(self, **params) -> RequirementResult | None:
        reevaluate = params.get("reevaluate")

        if self.evaluated and not reevaluate:
            return self.cached_result
        
        if self.requirements is not None:
            requirement_result = self.requirements.evaluate(**params)

            # cache
            self.satisfied = requirement_result.satisfied
            self.cached_result = requirement_result
            # self.evaluated = True

            return requirement_result
        
        # self.evaluated = True
        
        return None
    
    def __repr__(self) -> str:
        return f"Level(id={self.id}, name={self.name}, requirements={self.requirements})"