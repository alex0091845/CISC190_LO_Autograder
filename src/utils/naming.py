from api.api import CanvasApi


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

def get_default_course_name(course_id: str, api: CanvasApi):
    '''
    A private helper method to initialize the course name as:
    COURSE_ID - COURSE_NAME

    Where all special characters are replaced with underscores.
    '''
    # Get course information to get the course name
    course_info = api.get_course_info(course_id)
    course_name = course_info.get('name', 'Unknown Course')
    
    # Sanitize course name for use in directory name (remove special characters)
    safe_course_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in course_name)
    safe_course_name = safe_course_name.strip().replace(' ', '_')
    
    return f"{course_id} - {safe_course_name}"