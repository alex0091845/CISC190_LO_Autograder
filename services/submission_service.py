from api import fetch_submissions
from context.autograder_context import AutograderContext
from repositories.submission_repository import SubmissionRepository
from services.assignment_service import AssignmentService


class SubmissionService:
    """
    Defines services related to submissions:
    - Retrieving submissions by assignment name and user id
    - Checking if assignments meet specific criteria
    """
    def __init__(self, submission_repository: SubmissionRepository, 
                 context: AutograderContext,
                 assignment_service: AssignmentService):
        self.submission_repository = submission_repository
        self.context = context
        self.assignment_service = assignment_service

    def get_submission(self, user_id: int, assignment_id: int=-1, assignment_name: str="", refresh=False) -> dict | None:
        """
        Retrieve a submission by assignment name and user ID. If not cached,
        then fetch all submissions for the user (see :py:meth:`Assignments.fetch_submissions`).

        Args:
            assignment_name: Name of the assignment.
            user_id: Canvas user ID.

        Returns:
            The cached submission dictionary, or None if not found.
        """
        result = None

        if not self.has_submission(user_id, assignment_id, assignment_name) or refresh:
            result = fetch_submissions(self.context.get("course_id"), user_id)
            self.submission_repository.cache_submissions(result)

        assignment_id = self._get_assignment_id(assignment_id, assignment_name)
        return self.submission_repository.get_submission(user_id, assignment_id)
    
    def is_complete(self, student_id: int, assignment_id: int=-1, assignment_name: str="") -> bool:
        """
        Checks whether an assignment is complete for a given student.
        
        :param self: Description
        :param assignment_name: Description
        :type assignment_name: str
        :param student_id: Description
        :type student_id: int
        :return: Description
        :rtype: bool
        """
        assignment_id = self._get_assignment_id(assignment_id, assignment_name)
        return self.submission_repository.is_complete(assignment_id, student_id)
    
    def scored_higher_than(self, student_id: int, score_threshold: float, assignment_id: int=-1, assignment_name: str="") -> bool:
        """
        Checks whether an assignment's score is higher than a given threshold for a student.
        
        :param self: Description
        :param assignment_name: Description
        :type assignment_name: str
        :param student_id: Description
        :type student_id: int
        :param score_threshold: Description
        :type score_threshold: float
        :return: Description
        :rtype: bool
        """
        assignment_id = self._get_assignment_id(assignment_id, assignment_name)
        points = self.submission_repository.get_points(assignment_id, student_id)
        return points > score_threshold
    
    def has_submission(self, user_id: int, assignment_id: int=-1, assignment_name: str=""):
        """
        Docstring for has_submission
        
        :param self: Description
        :param user_id: Description
        :param assignment_id: Description
        :param assignment_name: Description
        """
        assignment_id = self._get_assignment_id(assignment_id, assignment_name)
        return self.submission_repository.has_submission(user_id, assignment_id)

    def meets_criteria(self,
                       criteria_description: str,
                       student_id: int,
                       assignment_name: str="",
                       assignment_id=-1
        ) -> bool:
        """
        Checks whether a student meets a specified criteria for an assignment.
        
        :param self: Description
        :param assignment_name: Description
        :type assignment_name: str
        :param student_id: Description
        :type student_id: int
        :param criteria_description: Description
        :type criteria_description: str
        :return: Description
        :rtype: bool
        """
        assignment_id = self._get_assignment_id(assignment_id, assignment_name)
        if assignment_id == -1:
            raise UserWarning(f"No assignment named {assignment_name} exists.")

        # print(f"sub service {assignment_name=}, {criteria_description=}, {student_id=}")
        submission = self.submission_repository.get_submission(student_id, assignment_id)
        # print(f"{submission=}")
        rubric_assessment = submission.get("rubric_assessment", {}) if submission else None
        criteria_id = self.assignment_service.get_criterion_id(assignment_name, criteria_description)

        user_score = rubric_assessment[criteria_id] if rubric_assessment and criteria_id else None
        # print(f"{rubric_assessment=}")
        # print(f"{user_score=}")
        # max_score = rubric_assessment[]

        # .get(criteria_description) if submission else None

        if not rubric_assessment:
            return False

        return True
    
    def _get_assignment_id(self, assignment_id: int=-1, assignment_name: str="") -> int:
        """
        Private helper method to get an assignment's id given either the id or the name
        by accessing the assignment service instance. Handles any parameter errors nicely.
        
        :param self: Description
        :param assignment_id: Description
        :type assignment_id: int
        :param assignment_name: Description
        :type assignment_name: str
        """
        if assignment_id == -1 and assignment_name == "":
            raise ValueError("Please provide either an assignment id or an assignment name.")
        
        if assignment_id > -1:
            return assignment_id
        
        return self.assignment_service.get_assignment_id(assignment_name)