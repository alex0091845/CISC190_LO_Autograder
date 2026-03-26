from context.autograder_context import AutograderContext
from models.requirements.lo_result import LoResult
from repositories.lo_repository import LoRepository
from services.assignment_service import AssignmentService
from services.submission_service import SubmissionService


class LoService:
    def __init__(self,
                 lo_repository: LoRepository,
                 context: AutograderContext):
        self.lo_repository = lo_repository
        self.context = context
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
                          lo_names_list: list[str],
                          assignment_service: AssignmentService,
                          submission_service: SubmissionService,
                          use_cache: bool = True
                          ) -> dict[int, dict[str, LoResult]]:  # {student_id -> {lo_name -> LoResult}}
        # Resolve LO names to Lo objects once — same for every student.
        lo_list = [self.get_lo_by_name(lo_name, exact_match=False) for lo_name in lo_names_list]

        results: dict[int, dict[str, LoResult]] = {}

        for student in student_list:
            student_results = self.lo_repository.evaluate_multiple(
                student=student,
                lo_list=lo_list,
                use_cache=use_cache,
                course_id=course_id,
                assignment_service=assignment_service,
                submission_service=submission_service,
            )
            results[student.student_id] = student_results

        return results
    
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