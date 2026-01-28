import copy
import requests

from typing import Dict, Any
from config import *
from levels import Levels
from lo import LOs
# from api.api import fetch_assignment_rubric


class Rubric:
    def __init__(self):
        self.lo_to_rubric: dict = {}

    def update_assignment_score_and_rubric(
        self,
        course_id: str,
        assignment_id: int,
        user_id: int,
        score: float,
        rubric_criteria_scores: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any] | None:
        """
        Updates the overall grade and the scores for individual rubric criteria
        for a specific user's submission on a target assignment.

        Args:
            course_id: The ID of the course.
            assignment_id: The ID of the assignment to grade.
            user_id: The ID of the student whose submission is being graded.
            score: The total score to post (e.g., 85.0).
            rubric_criteria_scores: A dictionary mapping the rubric criterion ID (string)
                                    to the score awarded for that criterion (float).
                                    Example: {'<crit1_id>': {'points': 3, 'rating_id': 'rat1'},
                                              '<crit2_id>': {'points': 5, 'rating_id': 'rat2', 'comments': 'Well Done'}}
                                    Note: We transform this dictionary into the following reference string format:
                                        rubric_assessment[crit1][points]=3&rubric_assessment[crit1][rating_id]=rat1&
                                        rubric_assessment[crit2][points]=5&rubric_assessment[crit2][rating_id]=rat2&
                                        rubric_assessment[crit2][comments]=Well%20Done.

        Returns:
            The JSON response object from the API upon success, or None on failure.
        """
        print(f"\n--- Updating Submission for User {user_id} on Assignment {assignment_id} ---")

        url = f"{API_BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"

        # Build the payload as form data with the nested rubric assessment structure
        payload = {
            "submission[posted_grade]": str(score)
        }
        
        # Transform rubric_criteria_scores into the form-encoded format Canvas expects
        for criterion_id, crit_data in rubric_criteria_scores.items():
            payload[f"rubric_assessment[{criterion_id}][points]"] = str(crit_data['points'])
            payload[f"rubric_assessment[{criterion_id}][rating_id]"] = crit_data['rating_id']
            if 'comments' in crit_data:
                payload[f"rubric_assessment[{criterion_id}][comments]"] = crit_data['comments']

        try:
            # Note: Canvas requires a PUT request for grading submissions.
            # Use 'data' parameter (not json) to send as form-encoded
            response = requests.put(url, headers=HEADERS, data=payload)
            response.raise_for_status() # Check for bad status code
            
            print(f"Successfully posted grade: {score} and updated {len(rubric_criteria_scores)} rubric criteria.")
            return response.json()

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error updating submission: {e}")
            print(f"Status Code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

    def get_rubric(self, lo_name: str) -> dict | None:
        """Retrieve the cached rubric for a specific LO, fetching it if not already cached.
        Args:
            lo_name: The name of the learning outcome (LO).
        Returns:
            The rubric dictionary for the LO, or None if not found.
        """
        if lo_name not in self.lo_to_rubric:
            self.fetch_assignment_rubric(COURSE_ID, lo_name)
        
        return self.lo_to_rubric.get(lo_name, None)

    def update_rubric_assessment(self, reqs: dict, lo_name: str, student_id: int) -> None:
        """Update the rubric assessment for a specific LO and student based on completed levels
        and missing assignments.
        Args:
            reqs: A dictionary mapping level names to tuples of (completed: bool, missing: list[str]).
            lo_name: The name of the learning outcome (LO).
            student_id: The Canvas user ID of the student.
        Returns:
            None
        """
        lo_reqs = reqs.get(lo_name, {})
        if not lo_reqs:
            print(f"No requirements found for LO {lo_name}, skipping rubric update.")
            return
        
        rubric = self.get_rubric(lo_name)
        if not rubric:
            print(f"No rubric found for LO {lo_name}, cannot update assessment.")
            return
        
        assessment = copy.deepcopy(rubric)
        
        # Overall level grade
        level_grade = Levels.calculate_level_grade(lo_reqs)
        print(f"Calculated level grade: {level_grade} for LO {lo_name}")
        # Find the criterion description for 4.0 points.
        # e.g., "1. Declare and use variables for data persistence within a program."
        # HACK...
        # But this will get the last criterion, which is the overall level grade,
        # a.k.a. Intern, Junior, Middle, Senior.
        criterion = self._find_criterion_by_points(assessment, 4.0)
        if criterion:
            assessment[criterion]['points'] = level_grade
        
        # # FOR EACH LEVEL IN ONE LO
        # # All ratings start out at max points. If something is incomplete,
        # # then set them to 0.0
        for level, (completed, missing) in lo_reqs.items():
            if not completed:
                assessment[level]['points'] = 0.0
            
            for assignment in missing:
                assessment[assignment]['points'] = 0.0
        
        assessment = self._transform_to_payload_format(assessment)

        self.update_assignment_score_and_rubric(
            COURSE_ID,
            LOs.lo_name_to_id.get(lo_name, -1), # lo_id
            student_id,
            level_grade, # overall score
            assessment
        )

    def fetch_assignment_rubric(self, course_id, lo_name):
        """
        Get the rubric for a specific assignment.
        
        Args:
            course_id: The Canvas course ID
            lo_id: The Canvas learning outcome (LO) assignment ID
            
        Returns:
            A list of dictionary containing the rubric data, or None if no rubric exists
        """
        lo_id = LOs.lo_name_to_id.get(lo_name, -1)
        url = f"{API_BASE_URL}/courses/{course_id}/assignments/{lo_id}"
        params = {
            'include[]': ['rubric', 'rubric_assessment']
        }
        
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        
        assignment = response.json()
        
        # Return the rubric if it exists
        self._process_and_cache_rubric(assignment.get('rubric', None), lo_name)
        return self.lo_to_rubric[lo_name]
    
    def _process_and_cache_rubric(self, rubric_data: list | None, lo_name: str) -> None:
        """Process and cache the rubric data for a specific learning outcome (LO).
        Each is formatted as:
        ```
        {
            'LO Name': {
                'Criterion Description': {
                    'id': criterion_id,
                    'points': max_points,
                    'ratings': {
                        points_0: 'rating_id_0',
                        points_1: 'rating_id_1', 
                    }                     
                }
            },
        }
        ```
        For example:
        ```
        {
            'LO 1: Variables': {
                'M1 Draw My Name': {
                    'id': '12345',
                    'points': 5,
                    'ratings': {
                        0: 'rat1',
                        3: 'rat2',
                        5: 'rat3'
                    }
                },
                'M1 Share: Draw My Name': {
                    'id': '67890',
                    'points': 5,
                    'ratings': {
                        0: 'rat4',
                        3: 'rat5',
                        5: 'rat6'
                    }
                },
                ...
            }
        }
        ```
        The reason for this format is so that when updating the rubric assessment,
        it's easy to look up each field and value. Specifically, we need the LO name,
        the criterion id, the points, and the rating ID for each criterion.
        
        It's easy to look up each criterion by the LO name and criterion description,
        like: `self.lo_to_rubric[lo_name][criterion_desc]`. This is because the criterion
        description happens to be the assignment name. We then can also easily get the
        grade (complete, incomplete, N/A) via the assignment name in `Assignments.py`.

        Once looked up, since an assignment is either complete or incomplete, and we know
        the max points for that criterion/assignment, we can directly set the points to either
        max points (complete) or 0 (incomplete). Then, based on how many points we set, we can
        get the rating ID from the `ratings` key. This allows us to get the points and the rating ID.

        Args:
            rubric_data: The list of rubric criteria dictionaries from the assignment.
            lo_name: The name of the learning outcome (LO).
        Returns:
            None
        """
        for criterion in rubric_data or []:
            criterion_id = criterion.get('id', '')
            desc = criterion.get('description', '')
            points = criterion.get('points', 0)
            criterion_ratings = criterion.get('ratings', [])

            ratings = {rating['points']: rating['id'] for rating in criterion_ratings}

            # if not there, create one
            if self.lo_to_rubric.get(lo_name) is None:
                self.lo_to_rubric[lo_name] = {}
            
            # add description to points map
            self.lo_to_rubric[lo_name][desc] = {
                'id': criterion_id,
                'points': points,
                'ratings': ratings
            }
    
    def _find_criterion_by_points(self, rubric: dict, points: float) -> str | None:
        """
        Find the criterion name in the rubric that matches the given points.
        Args:
            rubric: The rubric dictionary.
            points: The points to search for.
        Returns:
            The criterion name if found, else None.
        """
        for desc, crit in rubric.items():
            if crit['points'] == points:
                return desc
        return None
    
    def _transform_to_payload_format(self, assessment: dict) -> dict:
        """Transform the assessment dictionary into the format required for the API payload.
        Reference format:
        ```
        rubric_assessment[crit1][points]=3&rubric_assessment[crit1][rating_id]=rat1&
        rubric_assessment[crit2][points]=5&rubric_assessment[crit2][rating_id]=rat2&
        rubric_assessment[crit2][comments]=Well%20Done.
        ```
        Args:
            assessment: The assessment dictionary mapping criterion descriptions to their data.
        Returns:
            A dictionary formatted for the API payload.
        """
        
        copy = {}

        for _, crit in assessment.items():
            crit_id = crit['id']
            pts = crit['points']
            rating_id = crit['ratings'][pts]

            copy[crit_id] = {'points': pts, 'rating_id': rating_id}

        return copy