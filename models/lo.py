from models.level import Level
from models.requirements.lo_result import LoResult


class Lo:
    def __init__(self, id: int, name: str = "", levels: dict[str, Level] = {}):
        self.id = id
        self.name = name
        self.levels = levels

    def evaluate(self, course_id, student_id, submission_service) -> LoResult:
        # TODO
        return LoResult()
        # results = []
        # for level in self.levels:
        #     result = level.evaluate(course_id, student_id, submission_service)
        #     if result is not None:
        #         results.append((level, result))
        
        # return results

    def has_level(self, name: str) -> bool:
        for level in self.levels:
            if name in level:
                return True
        return False

    def get_level(self, name: str) -> Level | None:
        for level_name, level in self.levels.items():
            print(f"Looking for {name=} in {level_name=}")
            if name in level_name.lower():
                return level
        return None

    def __repr__(self):
        return f"Lo={self.id=}, {self.name=}, {self.levels}"