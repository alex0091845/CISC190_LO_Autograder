from context.autograder_context import AutograderContext


class AssignmentRepository:
    def __init__(self, context: AutograderContext):
        # key: assignment name, value: Assignment
        # Map strings to ids. Search for names, get the
        # ids, then map ids to actual assignments
        self.assignment_names_to_id: dict[str, int] = {}
        self.assignment_ids_to_obj: dict[int, dict] = {}
        self.context = context
        self._has_data = False
    
    def has_data(self):
        return self._has_data

    def init(self, assignments: list[dict]):
        self.cache_assignments(assignments)
    
    def has_assignment(self, name: str) -> bool:
        assignments = self._get_assignment_list_with_name(name)
        return len(assignments) > 1
    
    def cache_assignments(self, assignments: list[dict]) -> None:
        """Cache assignments for quick retrieval later.

        Args:
            assignments: List of assignment dictionaries to cache.
        """
        print("----- CACHING ASSIGNMENTS -----")
        for assignment_data in assignments:
            name = assignment_data["name"]
            id = assignment_data["id"]

            self.assignment_names_to_id[name] = id
            self.assignment_ids_to_obj[id] = assignment_data
        self._has_data = True    # stop from continuing to retrieve from API
    
    def get_assignment_by_name(self, name: str) -> dict:
        """
        Searches an assignment by name
        
        :param self: Description
        :param name: Description
        """
        assignment_id = self.get_assignment_id_by_name(name)
        assignment = self.assignment_ids_to_obj[assignment_id]

        # print(f"Looked for: {name}; Retrieved assignment: {assignment['name'] if assignment else None}")
        return assignment

    def get_assignment_id_by_name(self, name: str) -> int:
        assignments = self._get_assignment_list_with_name(name)
        
        return int(assignments[0]["id"])

    def _get_assignment_list_with_name(self, name: str) -> list[dict]:            
        assignments = list(filter(lambda item: name in item, self.assignment_names_to_id))

        if len(assignments) == 0:
            raise UserWarning(f"No assignment found named {name}")

        if len(assignments) > 1:
            raise UserWarning(f"More than one result is returned, but taking the first one: {assignments=}")

        return list(map(lambda name: self.assignment_ids_to_obj[
            self.assignment_names_to_id[name]
        ], assignments))