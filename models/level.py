from dataclasses import dataclass

from models.requirements.requirement_result import RequirementResult
from models.requirements.requirement_tree import RequirementTree


INTERN = "intern"
JUNIOR = "junior"
MIDDLE = "middle"
SENIOR = "senior"


@dataclass
class Level:
    id: int
    name: str = ""
    requirements: RequirementTree | None = None
    satisfied: bool = False     # stores a satisfied result from the latest run
    evaluated: bool = False
    cached_result: RequirementResult | None = None

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

        level = Level(id=0)
        level._initialize_name(yaml["level"])

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
            self.evaluated = True

            return requirement_result
        
        self.evaluated = True
        
        return None
    
    def _initialize_name(self, level_name: str):
        match level_name:
            case "intern":
                self.name = INTERN
            case "junior":
                self.name = JUNIOR
            case "middle":
                self.name = MIDDLE
            case "senior":
                self.name = SENIOR
            case _:
                self.name = ""
    
    def __repr__(self) -> str:
        return f"Level(id={self.id}, name={self.name}, requirements={self.requirements})"