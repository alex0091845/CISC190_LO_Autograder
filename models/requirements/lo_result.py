from models.level import Level
from models.requirements.requirement_result import RequirementResult


class LoResult:
    ## Report needs to provide level and get results
    ## Rubric marker (if needed) needs to only mark the missing ones, and then also the incomplete levels
    ## which means it needs to know which levels are incomplete, so everything basically (level results?)
    ## and the score overall, and the student's level
    def __init__(self, level_results: dict[str, RequirementResult | None]):
        self.level_results: dict[str, RequirementResult | None] = level_results
        self.level_score: int = 0
        self.level_attained: str = Level.INSUFFICIENT
        self.interpret_results()
    
    def interpret_results(self):
        for level_name, level_result in self.level_results.items():
            if level_result and level_result.satisfied:
                self.level_score = max(Level.level_str_to_score(level_name), self.level_score)
        
        self.level_attained = Level.level_score_to_str(self.level_score)