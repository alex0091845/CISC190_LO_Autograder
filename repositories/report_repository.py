from pathlib import Path


class ReportRepository:
    def __init__(self, context):
        self.context = context
    
    def get_latest_report(self, student_name):
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