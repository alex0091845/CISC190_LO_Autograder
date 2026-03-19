from utils.enums import GetGradeType


class AutograderContext:
    def __init__(self):
        self.course_id: str = ""
        self.lo_requirements_file_path: str = ""
        self.lo_list = []
        self.student_list = []
        self.curr_module: int = 0
        self.should_mark_rubric: bool = False
        self.grade_type: GetGradeType = GetGradeType.ON_TRACK
        self.should_grade: bool = True
        self.should_generate_report: bool = True
        self.should_email_report: bool = False