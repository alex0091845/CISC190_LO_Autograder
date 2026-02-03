from context.config_alex import COURSE_ID
from context.autograder_context import AutograderContext
from repositories.assignment_repository import AssignmentRepository
from repositories.lo_repository import LoRepository
from repositories.submission_repository import SubmissionRepository
from services.assignment_service import AssignmentService
from services.lo_service import LoService
from services.submission_service import SubmissionService


def test_submission(context):
    # manages submissions
    # submission_repository = SubmissionRepository(context)
    # submission_service = SubmissionService(submission_repository, context)

    # STUDENT_ID = 12345

    # submission = submission_service.get_submission(
    #     "Create Your Own Final Project Submission (Used for Checkpoints and Final Submission)",
    #     STUDENT_ID)
    # print(submission)
    pass

def test_assignment(context):
    # manages assignments
    assignment_repository = AssignmentRepository(context)
    assignment_service = AssignmentService(assignment_repository, context)

    criterion_id = assignment_service.get_criterion_id(
        "Create Your Own Final Project Submission (Used for Checkpoints and Final Submission)",
        "LO 1 - Variables")
    
    print(criterion_id)

def test_los(context):
    lo_repository = LoRepository(context)
    lo_service = LoService(lo_repository, context)
    lo_service.initialize()

    assignment_repository = AssignmentRepository(context)
    assignment_service = AssignmentService(assignment_repository, context)

    submission_repository = SubmissionRepository(context)
    submission_service = SubmissionService(submission_repository, context, assignment_service)

    lo1 = lo_service.get_lo_by_name("LO1 - Variables", exact_match=False)

    STUDENT_ID = 12345

    lo_service.evaluate(
        assignment_service=assignment_service,
        submission_service=submission_service,
        student_id=STUDENT_ID,
        course_id=COURSE_ID,    # TODO: get from context
        lo=lo1
    )


if __name__ == "__main__":
    context = AutograderContext(COURSE_ID)
    context.set("lo_requirements_file_path", "courses/requirements.yaml")
    # test_submission(context)
    # test_assignment(context)
    test_los(context)