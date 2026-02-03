from overrides import override
from models.requirements.requirement_node import RequirementNode
from models.requirements.requirement_result import RequirementResult


class OrNode(RequirementNode):
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
        any_satisfied = False

        for child in self.children:
            result = child.evaluate(**params)

            if result.satisfied:
                any_satisfied = True

            completed_list.extend(result.completed)
            missing_list.extend(result.missing)

        return RequirementResult(any_satisfied, missing_list, completed_list)
    
    @override
    def add_child(self, child: 'RequirementNode'):
        self.children.append(child)
    
    def __repr__(self):
        return f"OrNode(children={self.children})"
    
    def get_all_children(self) -> list[RequirementNode]:
        return self.children
            
def OR(*children: RequirementNode) -> OrNode:
    return OrNode(*children)
