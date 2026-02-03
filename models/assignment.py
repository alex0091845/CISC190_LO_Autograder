from dataclasses import dataclass

from models.rubric import Rubric
from models.submission import Submission

@dataclass
class Assignment:
    id: int
    rubric: Rubric
    name: str = ""
    # rubric_settings: dict = {}

    @staticmethod
    def from_dict(data: dict) -> 'Assignment':
        """
        Creates an Assignment object from a dictionary.
        
        :param data: Description
        :type data: dict
        :return: Description
        :rtype: Assignment
        """
        object = Assignment(
            id=data.get('id', 0),
            name=data.get('name', ""),
            # rubric_settings=data.get('rubric_settings', {}),
            rubric=Rubric(
                id=data.get('rubric', {}).get('id', 0),
                title=data.get('rubric', {}).get('title', ""),
                data=data.get('rubric', {}).get('data', [])
            )
        )

        return object