from enum import Enum
from context.autograder_context import AutograderContext
from models.level import Level
from models.requirements.lo_result import LoResult


class GetGradeType(Enum):
    ON_TRACK = 1
    DEFINITE = 2


class GradeService:
    def __init__(self, context: AutograderContext):
        self.context = context

    def get_grade(self, type: GetGradeType, lo_results_mappings: dict[str, LoResult]) -> str:
        match type:
            case GetGradeType.ON_TRACK:
                return self.get_grade_on_track(lo_results_mappings)
            case GetGradeType.DEFINITE:
                return self.get_definite_grade(lo_results_mappings)
            case _:
                return 'N/A'

    def get_grade_on_track(self, lo_results_mappings: dict[str, LoResult]) -> str:
        """
        Gets the grade that the student is on track to. Useful for when you still
        haven't released all assignments yet.
        """
        _, at_least_count = self._get_counts(lo_results_mappings)
        
        curr_module = self.context.get_int("curr_module")

        if at_least_count[3] >= (curr_module - 1):
            return 'A'
        
        if at_least_count[3] >= (curr_module - 2):
            return 'B'
        
        if at_least_count[2] >= (curr_module - 2):
            return 'C'
        
        if at_least_count[1] >= (curr_module - 2):
            return 'D'
        
        return 'F'
        
    def get_definite_grade(self, lo_results_mappings: dict[str, LoResult]) -> str:
        """
        Gets the student's definite grade. Useful for when you want to tell students
        what their grade would be if they stopped turning anything else in.
        """
        level_count, at_least_count = self._get_counts(lo_results_mappings)
        
        # then, evaluate
        if level_count[4] >= 7 and level_count[0] == 0 and level_count[1] == 0:
            return 'A'
        
        if at_least_count[3] >= 7 and level_count[0] == 0 and level_count[1] == 0:
            return 'B'
        
        if at_least_count[2] == 9:
            return 'C'
        
        if at_least_count[1] >= 5:
            return 'D'

        # if level_count[0] > 5:
        return 'F'
    
    def _get_counts(self, lo_results_mappings: dict[str, LoResult]):
        # map each level from 0-4. Counts how many LOs are at each level
        level_count = [0 for _ in range(5)]

        # counts at least how many of that level (by index) the student has achieved
        at_least_count = [0 for _ in range(5)]
        
        # first, count
        for _, lo_result in lo_results_mappings.items():
            level_count[lo_result.level_score] += 1
        
        # - then, accumulate for "at least"
        # - we always look at elements in level_count
        # - start at one element before the last then work backwards,
        # because we look at the one after to accumulate
        # - stop at 1 (before we reach 0) because technically everything
        # is at least 0, so that's pointless
        # - basically, prefix sum
        for i in range(len(level_count) - 2, 0, -1):
            at_least_count[i] = level_count[i] + level_count[i+1]

        return level_count, at_least_count