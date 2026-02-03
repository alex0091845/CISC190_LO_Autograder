from repositories.assignment_repository import AssignmentRepository
from repositories.submission_repository import SubmissionRepository
from repositories.lo_repository import LoRepository
from services.assignment_service import AssignmentService
from services.submission_service import SubmissionService
from services.lo_service import LoService


if __name__ == "__main__":
    context_manager = ContextManager()
    context_manager.initialize()
    context_manager.load_config()

    context = context_manager.get_context()

    # manages assignments
    assignment_repository = AssignmentRepository(context)
    assignment_service = AssignmentService(assignment_repository, context)

    # manages submissions
    submission_repository = SubmissionRepository(context, assignment_service)
    submission_service = SubmissionService(submission_repository, context)

    # set up LOs and requirements
    lo_repository = LoRepository(context)
    lo_service = LoService(lo_repository, context)
    lo_service.initialize(assignment_service, submission_service)

    # manages rubrics
    rubric_repository = RubricRepository(context)
    rubric_service = RubricService(rubric_repository, context)

    # manages reports
    report_repository = ReportRepository(context)
    report_service = ReportService(report_repository, context)

    # email doesn't need repository; just send emails
    email_service = EmailService(context)

    context.get("lo_ids", [])

    student_ids = []    # list of student IDs to evaluate
    for student_id in student_ids:
        lo_list = []    # list of LOs to evaluate for this student
        lo_results = lo_service.evaluate(student_id, submission_service, lo_list)

        # update rubrics or not
        rubric_service.update_server(lo_results)

        # generate reports or not
        report = report_service.generate_report(lo_results)

        # send emails or not
        email_service.send_report(student_id, report)