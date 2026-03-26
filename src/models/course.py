from dataclasses import dataclass

from api.api import CanvasApi
from utils.naming import get_default_course_name


@dataclass
class Course:
    id: str
    name: str = ""

    def get_name(self, api: CanvasApi):
        if self.name == "":
            self.name = get_default_course_name(self.id, api)