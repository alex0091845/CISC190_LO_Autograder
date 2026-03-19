import tkinter as tk

from api.api import CanvasApi
from context.autograder_context import AutograderContext
from managers.file_manager import FileManager
from utils.paths import BASE_DIR
from models.course import Course
from models.requirements.lo_result import LoResult
from repositories.assignment_repository import AssignmentRepository
from repositories.lo_repository import LoRepository
from repositories.report_repository import ReportRepository
from repositories.rubric_repository import RubricRepository
from repositories.student_repository import StudentRepository
from repositories.submission_repository import SubmissionRepository
from services.assignment_service import AssignmentService
from services.email_service import EmailService
from services.grade_service import GetGradeType, GradeService
from services.lo_service import LoService
from services.report_service import ReportService
from services.rubric_service import RubricService
from services.student_service import StudentService
from services.submission_service import SubmissionService
from views.app_view import AppView


class App:
    def __init__(self, config):
        self.config = config

        self.context = AutograderContext()
        self._setup_context(self.context, self.config)

        self.api = CanvasApi(self.config.API_BASE_URL, self.config.HEADERS)
        
        file_manager = FileManager()

        course = Course(self.context.course_id)
        course.fetch_name(self.api)

        self.lo_repository = LoRepository(self.context)
        self.lo_service = LoService(self.lo_repository, self.context)

        self.assignment_repository = AssignmentRepository(self.context)
        self.assignment_service = AssignmentService(self.assignment_repository, self.context, self.api)

        self.submission_repository = SubmissionRepository(self.context, self.api)
        self.submission_service = SubmissionService(self.submission_repository, self.context, self.assignment_service, self.api)

        self.student_repository = StudentRepository(file_manager, course, self.api)
        self.student_service = StudentService(self.student_repository)

        self.grade_service = GradeService(self.context)

        self.rubric_repository = RubricRepository()
        self.rubric_rating_service = RubricService(self.context, self.rubric_repository, self.lo_service, self.api)

        self.report_repository = ReportRepository(self.context)
        self.report_service = ReportService(self.context, self.report_repository, self.grade_service, self.lo_service)
        self.email_service = EmailService(self.context, self.student_service, self.api)

        # the rest of the contexts
        # settings
        self.context.lo_list = list(self.lo_service.get_lo_names())
        self.context.student_list = list(self.student_service.get_student_ids())
        self.context.curr_module = config.CURR_MODULE
        self.context.grade_type = GetGradeType.ON_TRACK

        # workflow options
        self.context.should_mark_rubric = False
        self.context.should_grade = True
        self.context.should_generate_report = True
        self.context.should_email_report = False

        # GUI
        root = tk.Tk()
        self.view = AppView(root, self)
        root.mainloop()

    def sync(self):
        student_obj_list = [self.student_service.get_student(student_id)
                            for student_id in self.context.student_list]
        lo_name_to_result: dict[str, LoResult] = {}

        if self.context.should_grade:
            lo_name_to_result = self.lo_service.evaluate_multiple(
                student_obj_list,
                course_id=self.context.course_id,
                lo_list=self.context.lo_list
            )

        if self.context.should_mark_rubric:
            self.rubric_rating_service.update_rubric_assessments(
                lo_name_to_result,
                self.assignment_service,
                student_list=student_obj_list
            )

        if self.context.should_generate_report:
            self.report_service.generate_reports(
                student_obj_list,
                lo_name_to_result
            )
        
        if self.context.should_email_report:
            self.email_service.send_emails(
                student_obj_list,
                self.report_service
            )

    def _setup_context(self, context: AutograderContext, config):
        '''
        Set up the context with necessary information and options from the config object.
        '''
        context.course_id = config.COURSE_ID
        context.lo_requirements_file_path = str(BASE_DIR / "user_data" / "requirements" / "cisc191_requirements.yaml")