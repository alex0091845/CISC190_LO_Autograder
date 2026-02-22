from typing import override
from models.requirements.requirement_node import RequirementNode
from models.requirements.requirement_result import RequirementResult
from models.requirements.requirement_tree import RequirementTree


class LevelNode(RequirementNode):
    """A node representing a level requirement in the requirements tree."""
    def __init__(self, level_name: str, other_level_tree: RequirementTree):
        self.level_name = level_name
        self.other_level_tree = other_level_tree

    @override
    def evaluate(self, **params) -> RequirementResult:
        """Evaluates the level requirement by evaluating its child node.
        Args:
            course_id: The ID of the course.
            student_id: The ID of the student.
            submission_service: The submission service to use for evaluation.
        Returns:
            The result of evaluating the child node.
        """
        
        if self.other_level_tree.root is None:
            return RequirementResult(False, [], [])
        
        return self.other_level_tree.root.evaluate(**params)
    
    @override
    def add_child(self, child: 'RequirementNode'):
        raise NotImplementedError("LevelNode can only have one child.")

    def __repr__(self) -> str:
        return f"LevelNode(level_name={self.level_name}, level_to_be_satisfied={self.other_level_tree})"

    def get_all_children(self) -> list[RequirementNode]:
        return []