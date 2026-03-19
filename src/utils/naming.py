def get_student_folder_name(student_name: str) -> str:
    """
    Convert a student's name into a sanitized folder name for storing reports.
    For example, "John Doe" becomes "John_Doe".
    
    Args:
        student_name: The full name of the student
        
    Returns:
        A sanitized folder name based on the student's name
    """
    # Replace spaces with underscores and remove any leading/trailing whitespace
    sanitized_name = student_name.strip().replace(' ', '_')
    return sanitized_name