from api.api import CanvasApi
from services.student_service import StudentService


class EmailService:
    def __init__(self, context, student_service: StudentService, api: CanvasApi):
        self.context = context
        self.student_service = student_service
        self.api = api

    def send_email(self, student_id, subject, body):
        """
        Send each student's latest progress report to them via Canvas Inbox.
        
        Args:
            student_ids: Optional list of student IDs to send emails to. If None, sends to all students.
                        Can be a list of integers or strings.
        """
        if student_id is None or subject is None or body is None:
            raise ValueError("EmailService: send_email: student_id and content are None!")
        
        student = self.student_service.get_student(student_id)
        student_id = student.student_id
        
        student_name = student.name
        
        print(f"Processing {student_name} (ID: {student_id})...")
        
        # Send the message
        result = self.api.send_canvas_message(student_id, subject, body)
        if result:
            print(f"  Successfully sent report to {student_name}")
            return True
        else:
            print(f"  Failed to send report to {student_name}")
            return False
    
    def send_emails(self, student_list, report_service):
        for student in student_list:
            subject = f"Your Progress Report - {student.name}"
            report = report_service.get_latest_report(student.name)

            print(f"Emailing report to {student.name} (ID: {student.student_id})...")
            print(f"Subject: {subject}")
            print(f"Report: {report}")

            self.send_email(student.student_id, subject, report)

# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(
#         description='Send student progress reports via Canvas Inbox'
#     )
#     parser.add_argument(
#         '--ids', '-i',
#         nargs='+',
#         help='Send to specific student IDs only. Example: --ids 12345 67890'
#     )
    
#     args = parser.parse_args()
    
#     send_emails(student_ids=args.ids)
