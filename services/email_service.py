from api import send_canvas_message
from services.student_service import StudentService


class EmailService:
    def __init__(self, context, student_service: StudentService):
        self.context = context
        self.student_service = student_service

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
        
        # sent_count = 0
        # failed_count = 0
        
        # for student in roster:
        student_id = student.student_id
        
        # Skip if filtering by student_ids and this student isn't in the list
        # if student_ids and str(student_id) not in student_ids:
        #     continue
        
        student_name = student.name
        
        print(f"Processing {student_name} (ID: {student_id})...")
        
        # Get the latest report
        # content = get_latest_report(student_name)
        
        # if not report_content:
        #     print(f"  No report found for {student_name}")
            # failed_count += 1
            # continue
        
        # Prepare the message        
        # Send the message
        if send_canvas_message(student_id, subject, body):
            print(f"  Successfully sent report to {student_name}")
            # sent_count += 1
        else:
            print(f"  Failed to send report to {student_name}")
            # failed_count += 1

        # Print summary
        # print("\n" + "="*50)
        # print(f"Email Summary:")
        # print(f"  Sent: {sent_count}")
        # print(f"  Failed: {failed_count}")
        # print("="*50)
        
        # return sent_count, failed_count

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
