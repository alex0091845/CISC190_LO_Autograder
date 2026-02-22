from typing import override

from models.requirements.requirement_node import RequirementNode
from models.requirements.requirement_result import RequirementResult


class AndNode(RequirementNode):
    def __init__(self, *children: RequirementNode):
        self.children: list = list(children)
    
    @override
    def evaluate(self, **params) -> RequirementResult:
        """Returns True if all of the assignments are complete for the set student_id.
        Args:
            completed_assignments: Set of completed assignments.
        Returns:
            True if all assignments are complete, False otherwise.
        """
        missing_list = []
        completed_list = []
        all_satisfied = True

        for child in self.children:
            result = child.evaluate(**params)

            if not result.satisfied:
                all_satisfied = False

            completed_list.extend(result.completed)
            missing_list.extend(result.missing)

        return RequirementResult(all_satisfied, missing_list, completed_list)
    
    @override
    def add_child(self, child: 'RequirementNode'):
        self.children.append(child)

    def __repr__(self) -> str:
        return f"AndNode(children={self.children})"

    def get_all_children(self) -> list[RequirementNode]:
        return self.children

            
def AND(*children: RequirementNode) -> AndNode:
    return AndNode(*children)