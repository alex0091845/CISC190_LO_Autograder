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

        file_path = self.context.get("lo_requirements_file_path", "")

        if not file_path: return

        self.lo_repository.initialize_from_yaml(file_path)
    
    def evaluate(self, **params) -> LoResult:
        return self.lo_repository.evaluate(**params)
    
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