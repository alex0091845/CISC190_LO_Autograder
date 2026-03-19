from api.api import CanvasApi
from context.autograder_context import AutograderContext


class SubmissionRepository:
    def __init__(self, context: AutograderContext, api: CanvasApi):
        # key: (assignment_id, user_id), value: Submission
        self.submissions: dict[tuple[int, int], dict] = {}
        self.user_submissions_cache: set[int] = set()
        self.context = context
        self.api = api
    
    def cache_submissions(self, submissions: list) -> None:
        """Cache submissions for quick retrieval later.

        Args:
            submissions: List of submission dictionaries to cache.
        """
        print("Caching submissions...")
        for submission in submissions:
            key = (
                int(submission['assignment']['id']),
                submission['user_id']
            )
            self.submissions[key] = submission
            self.user_submissions_cache.add(submission['user_id'])

    def has_submission(self, user_id: int, assignment_id: int) -> bool:
        """
        Checks whether a submission for some assignment name and by a user has been made.
        
        :param self: Description
        :param assignment_name: Description
        :type assignment_name: str
        :param user_id: Description
        :type user_id: int
        :return: Description
        :rtype: bool
        """
        return (assignment_id, user_id) in self.submissions

    def get_submission(self, user_id: int, assignment_id: int) -> dict | None:
        """Retrieve a submission by assignment name and user ID. If not cached,
        then fetch all submissions for the user (see :py:meth:`Assignments.fetch_submissions`).

        Args:
            assignment_name: Name of the assignment.
            user_id: Canvas user ID.

        Returns:
            The cached submission dictionary, or None if not found.
        """
        if not self.submissions or user_id not in self.user_submissions_cache:
            print(f"Submission cache empty or missing entry for student '{user_id}', fetching submissions for user ID {user_id}...")
            submissions = self.api.fetch_submissions(self.context.course_id, user_id)
            self.cache_submissions(submissions)

        result = self.submissions.get((assignment_id, user_id), None)
        
        return result

    def is_complete(self, assignment_id: int, student_id: int) -> bool:
        """Checks if the assignment is marked as "complete" for the given student.
        TODO: If no submissions are made, check if points earned == points possible, not from the submission itself.
        Args:
            assignment_name: Name of the assignment.
            student_id: The Canvas user ID of the student.
        Returns:
            True if the assignment is marked "complete", False otherwise.
        """
        grade = self.get_grade(assignment_id, student_id)
        points = self.get_points(assignment_id, student_id)
        points_possible = self.get_max_points(assignment_id, student_id)
        return (grade and grade.lower() == "complete") or (points >= points_possible and points_possible > 0.0)
    
    def get_grade(self, assignment_id: int, user_id: int) -> str:
        """Retrieve the grade for a specific assignment and student.
        Args:
            assignment_id: ID of the assignment.
            user_id: The Canvas user ID of the student.
        Returns:
            The grade as a string, or "N/A" if not graded.
        """
        submission = self.get_submission(user_id, assignment_id)
        if submission is None:
            return "N/A"
        
        grade = submission['grade']
        if not grade:
            grade = "N/A"

        return grade
    
    def get_points(self, assignment_id: int, student_id: int) -> float:
        """Retrieve the points earned for a specific assignment and student.
        Args:
            assignment_id: ID of the assignment.
            student_id: The Canvas user ID of the student.
        Returns:
            The points earned as a float, or 0.0 if not graded.
        """
        submission = self.get_submission(student_id, assignment_id)
        if submission is None:
            return 0.0
        
        points = submission['score']
        if points is None:
            points = 0.0

        return float(points)

    def get_max_points(self, assignment_id: int, student_id: int) -> float:
        """Retrieve the maximum points possible for a specific assignment.
        Args:
            assignment_id: ID of the assignment.
            student_id: The Canvas user ID of the student.
        Returns:
            The maximum points possible as a float, or 0.0 if not found.
        """
        submission = self.get_submission(student_id, assignment_id)
        if submission is None:
            return 0.0
        
        max_points = submission['assignment']['points_possible']
        if max_points is None:
            max_points = 0.0

        return float(max_points)