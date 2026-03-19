from context.autograder_context import AutograderContext
from models.requirements.lo_result import LoResult
from repositories.lo_repository import LoRepository
from services.assignment_service import AssignmentService
from services.submission_service import SubmissionService


class LoService:
    def __init__(self, lo_repository: LoRepository, context: AutograderContext):
        self.lo_repository = lo_repository
        self.context = context
        self.assignment_service: AssignmentService | None = None
        self.submission_service: SubmissionService | None = None
        self.initialize()

    def initialize(self):
        if self.lo_repository.is_initialized(): return

        file_path = self.context.lo_requirements_file_path

        if not file_path:
            raise Exception(f"LO requirements file path {file_path} not found. Please set 'lo_requirements_file_path' in the context to initialize the LO repository.")

        self.lo_repository.initialize_from_yaml(file_path)
    
    def evaluate(self, **params) -> LoResult:
        return self.lo_repository.evaluate(**params)
    
    def evaluate_multiple(self,
                          student_list: list,
                          course_id: str,
                          lo_list: list[str]
                          ) -> dict[str, LoResult]:
        # LO name to LoResult objects
        lo_name_to_result: dict[str, LoResult] = {}

        for student in student_list:
            # evaluate each LO in lo list. Doing this here because this gives user greater
            # control. Considering to create a LoService.evaluate_multiple later.
            for lo_name in lo_list:     # can allow user to customize lo list
                lo = self.get_lo_by_name(
                    lo_name,
                    exact_match=False
                )

                lo_result = self.evaluate(
                    assignment_service=self.assignment_service,
                    submission_service=self.submission_service,
                    student_id=student.student_id,
                    course_id=course_id,
                    lo=lo
                )

                lo_name_to_result[lo_name] = lo_result
            
        return lo_name_to_result
    
    def get_lo_by_name(self, lo_name: str, exact_match: bool=False):
        lo = self.lo_repository.get_lo_by_name(lo_name, exact_match)
        # print(f"Got {lo_name=}: {lo=} ")
        return lo
    
    def get_lo_id_by_name(self, lo_name: str):
        return self.lo_repository.get_lo_id_by_name(lo_name)

    def get_lo_results_by_name(self, lo_name: str):
        return self.lo_repository.get_lo_result_by_name(lo_name)
    
    def get_lo_names(self):
        return self.lo_repository.los.keys()