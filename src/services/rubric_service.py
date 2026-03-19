import copy
from api.api import CanvasApi
from services.assignment_service import AssignmentService
from context.autograder_context import AutograderContext
from models.requirements.lo_result import LoResult
from models.student import Student
from repositories.rubric_repository import RubricRepository
from services.lo_service import LoService


class RubricService:
    def __init__(self,
                 context: AutograderContext,
                 rubric_repository: RubricRepository,
                 lo_service: LoService,
                 api: CanvasApi):
        self.context = context
        self.rubric_repository = rubric_repository
        self.lo_service = lo_service
        self.api = api
        
    def get_rubric_by_id(self, assignment_id: str) -> dict | None:
        """Retrieve the cached rubric for a specific LO, fetching it if not already cached.
        Args:
            assignment_id: The id of the assignment
        Returns:
            The rubric dictionary for the LO, or None if not found.
        """
        if not self.rubric_repository.has_rubric(assignment_id):
            # Return the rubric if it exists
            rubric = self.api.fetch_assignment_rubric(self.context.course_id, assignment_id)
            self.rubric_repository._process_and_cache_rubric(rubric, assignment_id)
        
        return self.rubric_repository.get_rubric(assignment_id)

    def update_rubric_assessment(self, lo_result: LoResult, assignment_id: int, student_id: int) -> None:
        """Update the rubric assessment for a specific LO and student based on completed levels
        and missing assignments.
        Args:
            lo_result: The LoResult object containing the LO results.
            assignment_id: The id of the assignment.

            student_id: The Canvas user ID of the student.
        Returns:
            None
        """
        # TODO: double check the format of reqs
        # lo_reqs = lo_result.get(lo_name, {})
        # if not lo_reqs:
        #     print(f"No requirements found for LO {lo_name}, skipping rubric update.")
        #     return
        
        rubric = self.rubric_repository.get_rubric(str(assignment_id))
        if not rubric:
            print(f"No rubric found for assignment {assignment_id}, cannot update assessment.")
            return
        
        assessment = copy.deepcopy(rubric)
        
        # Overall level grade
        level_grade = lo_result.level_score
        print(f"Calculated level grade: {level_grade} for assignment {assignment_id}")
        # Find the criterion description for 4.0 points.
        # e.g., "1. Declare and use variables for data persistence within a program."
        # HACK...
        # But this will get the last criterion, which is the overall level grade,
        # a.k.a. Intern, Junior, Middle, Senior.
        criterion = self._find_criterion_by_points(assessment, 4.0)
        if criterion:
            assessment[criterion]['points'] = level_grade
        
        # FOR EACH LEVEL IN ONE LO
        # All ratings start out at max points. If something is incomplete,
        # then set them to 0.0
        for level, req_result in lo_result.level_results.items():
            if req_result is None: 
                continue
            
            completed = req_result.completed
            missing = req_result.missing
            
            if not completed:
                assessment[level]['points'] = 0.0
            
            for assignment in missing:
                assessment[assignment]['points'] = 0.0
        
        assessment = self._transform_to_payload_format(assessment)

        self.api.update_assignment_score_and_rubric(
            self.context.course_id,
            assignment_id, # lo_id
            student_id,
            level_grade, # overall score
            assessment
        )

    def update_rubric_assessments(self,
                                  lo_result_mappings: dict[int, dict[str, LoResult]],
                                  assignment_service: AssignmentService,
                                  student_list: list[Student]):
        for student in student_list:
            # get the lo results for this student
            student_id = student.student_id
            lo_results = lo_result_mappings.get(student_id, {})
            
            for lo_name, lo_result in lo_results.items():
                assignment_id = assignment_service.get_assignment_id(lo_name)

                if not assignment_id:
                    print(f"No assignment found for LO {lo_name}, skipping rubric update.")
                    continue
            
                self.update_rubric_assessment(lo_result, assignment_id, student_id)

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