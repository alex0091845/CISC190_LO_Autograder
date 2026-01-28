import copy
import requests
from config import API_BASE_URL, COURSE_ID, HEADERS


class Assignments:
    """Class to handle fetching and caching of assignments and their submissions."""
    _student_id: int = -1
    _submission_cache: dict = {}
    _user_submissions_cache: set = set()

    @staticmethod
    def _clean_assignment_name(name: str) -> str:
        # remove any prefix from the assignment name
        try:
            if name.index(')') > -1:
                name = name[name.index(')') + 1 :]
        except ValueError:
            pass
        return name.strip()

    @staticmethod
    def fetch_submissions(course_id: str, user_id: int, include_history: bool = False) -> list:
        """Fetch all student submissions for a course (all assignments).

        Args:
            course_id: Canvas course ID.
            user_id: Canvas user ID.
            include_history: If True, include submission history.

        Returns:
            List of submission dictionaries. Each includes embedded assignment and user info.
        """
        submissions: list = []
        url = f"{API_BASE_URL}/courses/{course_id}/students/submissions"
        params = {
            'student_ids[]': user_id,
            "per_page": 100,
            "include[]": ["assignment"] + (["submission_history"] if include_history else [])
        }

        print("Retrieving and caching submissions...")
        while url:
            resp = requests.get(url, headers=HEADERS, params=params)
            resp.raise_for_status()
            submissions.extend(resp.json())
            # Handle pagination via Link headers
            if 'next' in resp.links:
                url = resp.links['next']['url']
                params = None  # already encoded in next URL
            else:
                url = None

        # Cache the submissions for potential future use
        Assignments._cache_submissions(submissions)

        return submissions
    

    @staticmethod
    def _cache_submissions(submissions: list) -> None:
        """Cache submissions for quick retrieval later.

        Args:
            submissions: List of submission dictionaries to cache.
        """
        for submission in submissions:
            key = (
                Assignments._clean_assignment_name(submission['assignment']['name']),
                submission['user_id']
            )
            Assignments._submission_cache[key] = submission
            Assignments._user_submissions_cache.add(submission['user_id'])

    @staticmethod
    def get_submission(assignment_name: str, user_id: int) -> dict | None:
        """Retrieve a submission by assignment name and user ID. If not cached,
        then fetch all submissions for the user (see :py:meth:`Assignments.fetch_submissions`).

        Args:
            assignment_name: Name of the assignment.
            user_id: Canvas user ID.

        Returns:
            The cached submission dictionary, or None if not found.
        """
        if not Assignments._submission_cache or user_id not in Assignments._user_submissions_cache:
            print(f"Submission cache empty or missing entry for student '{user_id}', fetching submissions for user ID {user_id}...")
            Assignments.fetch_submissions(COURSE_ID, user_id)

        result = Assignments._submission_cache.get((assignment_name, user_id), None)
        # print(f"Retrieved submission for '{assignment_name}', user ID {user_id}: {result is not None}")
        return result
    

    @staticmethod
    def get_grade(assignment_name: str, user_id: int) -> str:
        """Retrieve the grade for a specific assignment and student.
        Args:
            assignment_name: Name of the assignment.
            user_id: The Canvas user ID of the student.
        Returns:
            The grade as a string, or "N/A" if not graded.
        """
        submission = Assignments.get_submission(assignment_name, user_id)
        if submission is None:
            return "N/A"
        
        grade = submission['grade']
        if not grade:
            grade = "N/A"

        return grade
    
    @staticmethod
    def get_points(assignment_name: str, student_id: int) -> float:
        """Retrieve the points earned for a specific assignment and student.
        Args:
            assignment_name: Name of the assignment.
            student_id: The Canvas user ID of the student.
        Returns:
            The points earned as a float, or 0.0 if not graded.
        """
        submission = Assignments.get_submission(assignment_name, student_id)
        if submission is None:
            return 0.0
        
        points = submission['score']
        if points is None:
            points = 0.0

        return float(points)
    

    @staticmethod
    def get_max_points(assignment_name: str, student_id: int) -> float:
        """Retrieve the maximum points possible for a specific assignment.
        Args:
            assignment_name: Name of the assignment.
            student_id: The Canvas user ID of the student.
        Returns:
            The maximum points possible as a float, or 0.0 if not found.
        """
        submission = Assignments.get_submission(assignment_name, student_id)
        if submission is None:
            return 0.0
        
        max_points = submission['assignment']['points_possible']
        if max_points is None:
            max_points = 0.0

        return float(max_points)

    
    @staticmethod
    def is_complete(assignment_name: str, student_id: int) -> bool:
        """Checks if the assignment is marked as "complete" for the given student.
        TODO: If no submissions are made, check if points earned == points possible, not from the submission itself.
        Args:
            assignment_name: Name of the assignment.
            student_id: The Canvas user ID of the student.
        Returns:
            True if the assignment is marked "complete", False otherwise.
        """
        grade = Assignments.get_grade(assignment_name, student_id)
        points = Assignments.get_points(assignment_name, student_id)
        points_possible = Assignments.get_max_points(assignment_name, student_id)
        return (grade and grade.lower() == "complete") or (points >= points_possible and points_possible > 0.0)

    
    @staticmethod
    def grade(student_id: int, reqs: dict) -> dict:
        """Grades the student based on the provided requirements.
        Args:
            student_id: The Canvas user ID of the student.
            reqs: A dictionary mapping LO names to level requirements (functions).
                  See lo.py -> LOs.reqs
        Returns:
            A dictionary mapping LO names to level completion results.
        """
        results = copy.deepcopy(reqs)
        Assignments.set_student_id(student_id)

        for lo, level_reqs in results.items():
            for level, req_func in level_reqs.items():
                # req_func returns (completed: bool, missing: list[str])
                results[lo][level] = req_func()

        return results


    @staticmethod
    def set_student_id(student_id: int) -> None:
        """Sets the student ID for instance methods that require it.
        Args:
            student_id: The Canvas user ID of the student.
        """
        Assignments._student_id = student_id


    @staticmethod
    def _and(assignments: list[str | tuple[bool, list[str]]]) -> tuple[bool, list[str]]:
        """Returns True if all of the assignments are complete for the set student_id.
        Args:
            assignments: List of assignment names to check.
        Returns:
            True if all assignments are complete, False otherwise.
        """
        if Assignments._student_id == -1:
            raise ValueError("student_id not set for AND operation")
        
        completed = False
        missing = []

        for assgn in assignments:
            if isinstance(assgn, tuple):
                if not assgn[0]:
                    missing.extend(assgn[1])
            else:
                if not Assignments.is_complete(assgn, student_id=Assignments._student_id):
                    missing.append(assgn)
        
        completed = len(missing) == 0
        return (completed, missing)


    @staticmethod
    def _or(assignments: list[str | tuple[bool, list[str]]]) -> tuple[bool, list[str]]:
        """Returns True if any of the assignments are complete for the set student_id.
        Args:
            assignments: List of assignment names to check.
        Returns:
            True if any assignment is complete, False otherwise.
        """
        if Assignments._student_id == -1:
            raise ValueError("student_id not set for OR operation")
        
        completed = False
        missing = []

        for assgn in assignments:
            if isinstance(assgn, tuple):
                if assgn[0]:
                    completed = True
                else:
                    missing.extend(assgn[1])
            else:
                if Assignments.is_complete(assgn, student_id=Assignments._student_id):
                    completed = True
                else:
                    missing.append(assgn)
        
        return (completed, missing)