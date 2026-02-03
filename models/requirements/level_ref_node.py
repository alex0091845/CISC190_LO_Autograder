from models.requirements.requirement_node import RequirementNode
from models.requirements.requirement_result import RequirementResult


class LevelRefNode(RequirementNode):
    def __init__(self, level_name: str):
        self.ref_level_name = level_name

    def evaluate(self, **params) -> RequirementResult:
        """
        Parameters:
            lo: The learning object containing levels.
        Returns:
            RequirementResult indicating if the referenced level is satisfied.
        """
        # the lo in which the referenced level exists
        lo = params['lo']
        
        level = lo.get_level(self.ref_level_name)

        if not level is None:
            result = level.evaluate(**params)
            return result
        
        return RequirementResult(False, [self.ref_level_name], [])

    def add_child(self, child: RequirementNode):
        raise NotImplementedError("LevelRefNode cannot have children.")

    def get_all_children(self) -> list[RequirementNode]:
        raise NotImplementedError("LevelRefNode does not have children.")
    
    def __repr__(self) -> str:
        return f"LevelRefNode(reference_level={self.ref_level_name})"

def LevelRef(level_name: str) -> LevelRefNode:
    return LevelRefNode(level_name)