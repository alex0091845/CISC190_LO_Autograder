from api.api import CanvasApi
from context.autograder_context import AutograderContext
from repositories.assignment_repository import AssignmentRepository


class AssignmentService:
    """
    Provides services related to assignments:

    - Retrieving assignments by name
    - Checks whether an assignment is complete
    - 
    """
    def __init__(self, assignment_repository: AssignmentRepository, 
                 context: AutograderContext,
                 api: CanvasApi):
        self.assignment_repository = assignment_repository
        self.context = context
        self.api = api
    
    def get_assignment(self, name: str, refresh=False):
        """
        Retrieve an assignment by name.

        Args:
            name: Name of the assignment.

        Returns:
            The Assignment object, or None if not found.
        """
        
        if not self.assignment_repository.has_assignment(name) or refresh:
            self.init_repository(refresh)

        return self.assignment_repository.get_assignment_by_name(name)

    def get_assignment_id(self, name: str) -> int:
        self.init_repository()
        return self.assignment_repository.get_assignment_id_by_name(name)
    
    def get_criterion_id(self, assignment_name: str, criterion_description: str) -> str | None:
        """
        Retrieve the ID of a rubric criterion by its description for a given assignment.

        Args:
            assignment_name: Name of the assignment.
            criterion_description: Description of the rubric criterion.
        Returns:
            The criterion ID as a string, or None if not found.
        """
        # print(f'criterion id for {assignment_name=} and {criterion_description=}')
        assignment = self.get_assignment(assignment_name)

        if not assignment: return None

        # print(f"{assignment['rubric']=}")

        criterion = list(filter(lambda criterion:   (not criterion['description'] is None and criterion_description in criterion['description']) or 
                                                    (not criterion['long_description'] is None and criterion_description in criterion['long_description']),
                                assignment['rubric']))
        
        criterion_id = criterion[0]['id'] if criterion else None
        # print(f"Found criterion ID: {criterion_id}")
        return criterion_id
    
    def init_repository(self, forced_refresh=False):
        if not self.assignment_repository.has_data() or forced_refresh:
            result = self.api.fetch_all_assignments(self.context.course_id)
            self.assignment_repository.cache_assignments(result)