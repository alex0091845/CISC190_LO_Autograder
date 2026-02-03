from overrides import override
from models.requirements.requirement_node import RequirementNode
from models.requirements.requirement_result import RequirementResult
from services.submission_service import SubmissionService


class AssignmentNode(RequirementNode):
    def __init__(self, assignment_name: str,
                 completed_type: str = "complete", 
                 score_threshold: float = 0.0):
        self.assignment_name = assignment_name
        self.completed_type = completed_type
        self.score_threshold = score_threshold

    @override
    def evaluate(self, **params) -> RequirementResult:
        """Returns True if all of the assignments are complete for the set student_id.
        Args:
            completed_assignments: Set of completed assignments.
        Returns:
            RequirementResult where satisfied is True if the assignment is complete, False otherwise.
        """
        student_id, submission_service = params["student_id"], params["submission_service"]
        missing_list = []
        completed_list = []
        satisfied = False

        completed_callback = self.get_completed_callback(submission_service)
        satisfied = completed_callback(student_id)

        if satisfied:
            completed_list.append(self.assignment_name)
        else:
            missing_list.append(self.assignment_name)

        return RequirementResult(satisfied, missing_list, completed_list)
    
    def get_completed_callback(self, submission_service: SubmissionService):
        if self.completed_type == "complete":
            return lambda student_id: submission_service.is_complete(student_id, assignment_name=self.assignment_name)
        elif self.completed_type == "scored higher than":
            return lambda student_id: submission_service.scored_higher_than(student_id, self.score_threshold, assignment_name=self.assignment_name)
        else:
            raise ValueError(f"Unknown completed_type: {self.completed_type}")

    @override
    def add_child(self, child: 'RequirementNode'):
        raise NotImplementedError("AssignmentNode cannot have children.")

    def __repr__(self) -> str:
        return f"AssignmentNode(assignment_name={self.assignment_name})"
    
    def get_all_children(self) -> list[RequirementNode]:
        return []

def Assignment(assignment_name: str, 
               completed_type: str = "complete", 
               score_threshold: float = 0.0) -> AssignmentNode:
    return AssignmentNode(assignment_name,
                          completed_type=completed_type, 
                          score_threshold=score_threshold)