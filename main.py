from config import COURSE_ID, CURR_MODULE
from context.autograder_context import AutograderContext
from managers.file_manager import FileManager
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

def sync(context):
    context.set("course_id", COURSE_ID)
    context.set("lo_requirements_file_path", "courses/cisc191_requirements.yaml")

    file_manager = FileManager()

    course = Course(context.get("course_id"))

    lo_repository = LoRepository(context)
    lo_service = LoService(lo_repository, context)

    assignment_repository = AssignmentRepository(context)
    assignment_service = AssignmentService(assignment_repository, context)

    submission_repository = SubmissionRepository(context)
    submission_service = SubmissionService(submission_repository, context, assignment_service)

    student_repository = StudentRepository(file_manager, course)
    student_service = StudentService(student_repository)

    grade_service = GradeService(context)

    rubric_repository = RubricRepository()
    rubric_rating_service = RubricService(context, rubric_repository, lo_service)

    report_repository = ReportRepository(context)
    report_service = ReportService(context, report_repository, grade_service, lo_service)
    email_service = EmailService(context, student_service)

    ### options
    context.set("lo_list", lo_service.get_lo_names())
    context.set("student_list", student_service.get_student_ids())
    context.set("curr_module", CURR_MODULE)
    context.set("grade_type", GetGradeType.ON_TRACK.value)
    context.set("should_mark_rubric", False)
    context.set("should_generate_report", True)
    context.set("should_email_report", False)

    ### core behavior
    for student_id in context.get("student_list"):    # can allow user to customize student list
        student = student_service.get_student(student_id)

        # LO name to LoResult objects
        lo_name_to_result: dict[str, LoResult] = {}

        # evaluate each LO in lo list. Doing this here because this gives user greater
        # control. Considering to create a LoService.evaluate_multiple later.
        for lo_name in context.get("lo_list"):     # can allow user to customize lo list
            lo = lo_service.get_lo_by_name(lo_name, exact_match=False)

            lo_result = lo_service.evaluate(
                assignment_service=assignment_service,
                submission_service=submission_service,
                student_id=student_id,
                course_id=context.get("course_id"),
                lo=lo
            )

            lo_name_to_result[lo_name] = lo_result

            if context.get("should_mark_rubric"):
                rubric_rating_service.update_rubric_assessment(lo_result,
                                                               assignment_service.get_assignment_id(lo_name),
                                                               student_id)
        
        if context.get("should_generate_report"):
            report = report_service.generate_report(student.name, lo_name_to_result)
            report_service.save(report, student.name)
            # print(report)
    
    if not context.get("should_email_report"):
        return
    
    answer = input("Email students now? (y/n): ")
    while answer not in ['y', 'n']:
        answer = input("Email students now? (y/n): ")

    if answer == 'n':
        return

    for student_id in context.get("student_list"):    # can allow user to customize student list
        student = student_service.get_student(student_id)
        subject = f"Your Progress Report - {student.name}"
        report = report_service.get_latest_report(student.name)
        email_service.send_email(student.student_id, subject, report)

if __name__ == "__main__":
    context = AutograderContext()
    sync(context)