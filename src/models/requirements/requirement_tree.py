from models.requirements.and_node import AND
from models.requirements.assignment_node import Assignment
from models.requirements.criteria_node import Criteria
from models.requirements.level_ref_node import LevelRef
from models.requirements.requirement_result import RequirementResult
from models.requirements.or_node import OR
from models.requirements.requirement_node import RequirementNode


class RequirementTree:
    def __init__(self, root: RequirementNode | None):
        self.root = root
    
    def build(self, data: dict) -> RequirementNode | None:
        """
        Builds a RequirementNode tree from a dictionary.

        Args:
            data: Dictionary representing the requirement tree.

        Returns:
            RequirementTree representing the root of the tree.
        """
        if not "requirements" in data:
            raise ValueError("Invalid requirement tree data: 'requirements' key not found.")
        
        requirements = data["requirements"]
        
        self.root = self.build_node(requirements)
        queue = [(self.root, requirements)]  # list of tuples (RequirementNode, dict)

        # BFS
        while queue:
            curr, req_dict = queue.pop(0)

            # go through requirements; add them as nodes to the
            # current node
            reqs = req_dict[self._get_first_key(req_dict)]

            for node in reqs:
                # skip any single assignments
                if not isinstance(node, dict):
                    continue
                
                child_node = self.build_node(node)
                if curr is not None and child_node is not None:
                    curr.add_child(child_node)

                    # add to queue only if the value is a list
                    val = node[self._get_first_key(node)]
                    if isinstance(val, list):
                        queue.append((child_node, node))

        return self.root
    
    def build_node(self, data: dict) -> RequirementNode | None:
        """Builds a RequirementNode from a dictionary.
        Args:
            data: Dictionary representing a requirement node.
        Returns:
            RequirementNode object.
        """
        match self._get_first_key(data):
            case "and":
                return AND()
            case "or":
                return OR()
            case "assignment":
                return Assignment(
                    assignment_name=data["assignment"]
                )
            case "criteria":
                return Criteria(
                    criteria_name=data["criteria"]["description"],
                    assignment_name=data["criteria"]["assignment"]
                )
            case "level_ref":
                return LevelRef(
                    level_name=data["level_ref"]
                )
            case _:
                return None
            
    def evaluate(self, **params) -> RequirementResult:
        """
        Evaluates the requirement tree for the given completed assignments.
        It is the easiest to implement recursion since the evaluation itself is
        recursive by nature. Considering the amount of assignments needed to
        satisfy each level, this is reasonable and is unlikely to cause 
        stack overflow.

        Args:
            course_id: ID of the course.
            student_id: ID of the student.
            submission_service: Service to check submissions.
        Returns:
            RequirementResult object representing the evaluation result.
        """
        if self.root == None:
            return RequirementResult(False, [], [])
        
        return self.root.evaluate(**params)

    @staticmethod
    def _get_first_key(data: dict) -> str:
        """Returns the first key of a dictionary.
        Args:
            data: Dictionary to get the first key from.
        Returns:
            The first key as a string.
        """
        return list(data.keys())[0]
    
    @staticmethod
    def from_yaml(data: dict):
        """Creates a RequirementTree from a YAML file.
        Args:
            data: The yaml data as a dictionary.
        Returns:
            RequirementTree object.
        """
        tree = None

        tree = RequirementTree(None)
        tree.build(data)
        
        return tree
    
    def __repr__(self) -> str:
        return f"RequirementTree(root={self.root})"

if __name__ == "__main__":
    # tree = RequirementTree.from_yaml("requirements/requirements.yaml")
    # print(tree)
    pass