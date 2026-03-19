from models.requirements.requirement_node import RequirementNode
from models.requirements.requirement_result import RequirementResult


class CriteriaNode(RequirementNode):
    """
    A node representing a criteria in the requirements tree.
    """
    def __init__(self, criteria_name: str, assignment_name: str):
        self.criteria_name = criteria_name
        self.assignment_name = assignment_name

    def evaluate(self, **params) -> RequirementResult:
        """Evaluates the criteria requirement.
        Args:
            course_id: The ID of the course.
            student_id: The ID of the student.
            submission_service: The submission service to use for evaluation.
        Returns:
            The result of evaluating the criteria.
        """
        student_id, submission_service = params["student_id"], params["submission_service"]
        satisfied = submission_service.meets_criteria(self.criteria_name, student_id, self.assignment_name)
        missing_list = []
        completed_list = []

        if satisfied:
            completed_list.append(self.assignment_name)
        else:
            missing_list.append(self.assignment_name)

        return RequirementResult(satisfied, missing_list, completed_list)

    def add_child(self, child: RequirementNode):
        raise NotImplementedError("CriteriaNode cannot have children.")

    def get_all_children(self) -> list[RequirementNode]:
        raise NotImplementedError("CriteriaNode does not have children.")
    
    def __repr__(self) -> str:
        return f"CriteriaNode(criteria_name={self.criteria_name}, assignment_name={self.assignment_name})"

    
def Criteria(criteria_name: str, assignment_name: str) -> CriteriaNode:
    return CriteriaNode(criteria_name, assignment_name)