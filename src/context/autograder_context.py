from utils.enums import GetGradeType
from utils.path_config import PathConfig
from utils.paths import BASE_DIR


class AutograderContext:
    def __init__(self):
        self._course_id: str = ""
        self.lo_requirements_file_path: str = ""
        self.lo_list = []
        self.student_list = []
        self.curr_module: int = 0
        self.should_mark_rubric: bool = False
        self.grade_type: GetGradeType = GetGradeType.ON_TRACK
        self.should_grade: bool = True
        self.should_generate_report: bool = True
        self.should_email_report: bool = False
        self.path_config = PathConfig(BASE_DIR, self.course_id)
    
    @property
    def course_id(self):
        return self._course_id

    @course_id.setter
    def course_id(self, value: str):
        '''
        Sets the course id, and then also updates the path config with the new course id.
        '''
        self._course_id = value
        self.path_config = PathConfig(BASE_DIR, self.course_id)