import requests
from pathlib import Path
from config import API_BASE_URL, COURSE_ID, HEADERS, INSTRUCTOR_SIGNOFF
from students import Students


def get_latest_report(student_name):
    """
    Retrieve the latest progress report for a student.
    
    Args:
        student_name: The student's name
        
    Returns:
        The content of the latest report file, or None if not found
    """
    reports_dir = Path("reports")
    
    # Create sanitized name for directory lookup
    student_name_parts = student_name.split()
    if len(student_name_parts) >= 2:
        sanitized_name = f"{student_name_parts[0]}_{student_name_parts[-1]}"
        student_dir = reports_dir / sanitized_name
        
        if student_dir.exists():
            # Find the latest report
            report_files = sorted(student_dir.glob("progress_report_*.txt"), reverse=True)
            if report_files:
                latest_report = report_files[0]
                try:
                    with open(latest_report, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading report for {student_name}: {str(e)}")
                    return None
    
    return None


def send_canvas_message(user_id, subject, body):
    """
    Send a message to a student via Canvas Inbox.
    
    Args:
        user_id: The Canvas user ID of the recipient
        subject: The subject line of the message
        body: The message body
        
    Returns:
        True if successful, False otherwise
    """
    url = f"{API_BASE_URL}/conversations"
    
    payload = {
        "recipients[]": [user_id],
        "subject": subject,
        "body": body,
        "group_conversation": False
    }
    
    try:
        response = requests.post(url, headers=HEADERS, data=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to user {user_id}: {str(e)}")
        return False


def send_emails(student_ids=None):
    """
    Send each student's latest progress report to them via Canvas Inbox.
    
    Args:
        student_ids: Optional list of student IDs to send emails to. If None, sends to all students.
                     Can be a list of integers or strings.
    """
    # Get all students
    roster = Students()
    
    # Convert student_ids to strings if provided
    if student_ids:
        student_ids = [str(sid) for sid in student_ids]
    
    sent_count = 0
    failed_count = 0
    
    for student in roster.students:
        student_id = student['id']
        
        # Skip if filtering by student_ids and this student isn't in the list
        if student_ids and str(student_id) not in student_ids:
            continue
        
        student_name = student['name']
        
        print(f"Processing {student_name} (ID: {student_id})...")
        
        # Get the latest report
        report_content = get_latest_report(student_name)
        
        if not report_content:
            print(f"  No report found for {student_name}")
            failed_count += 1
            continue
        
        # Prepare the message
        subject = f"Your Progress Report - {student_name}"
        body = report_content
        
        # Send the message
        if send_canvas_message(student_id, subject, body):
            print(f"  Successfully sent report to {student_name}")
            sent_count += 1
        else:
            print(f"  Failed to send report to {student_name}")
            failed_count += 1
    
    # Print summary
    print("\n" + "="*50)
    print(f"Email Summary:")
    print(f"  Sent: {sent_count}")
    print(f"  Failed: {failed_count}")
    print("="*50)
    
    return sent_count, failed_count


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Send student progress reports via Canvas Inbox'
    )
    parser.add_argument(
        '--ids', '-i',
        nargs='+',
        help='Send to specific student IDs only. Example: --ids 12345 67890'
    )
    
    args = parser.parse_args()
    
    send_emails(student_ids=args.ids)
