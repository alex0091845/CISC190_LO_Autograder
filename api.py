import requests
from context.config_alex import API_BASE_URL, HEADERS

def get_course_info(course_id):
    """
    Get course information including the course name.
    
    Args:
        course_id: The Canvas course ID
        
    Returns:
        Dictionary containing course information
    """
    url = f"{API_BASE_URL}/courses/{course_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()

def get_all_students(course_id):
    """
    Get all students enrolled in a Canvas course.
    
    Args:
        course_id: The Canvas course ID
        
    Returns:
        A list of student dictionaries containing student information
    """
    students = []
    url = f"{API_BASE_URL}/courses/{course_id}/users"
    
    # Parameters to filter for students only
    params = {
        "enrollment_type[]": "student",
        "per_page": 100  # Get 100 students per page (Canvas API max)
    }
    
    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        
        students.extend(response.json())
        
        # Check for pagination - Canvas uses Link header for pagination
        if 'next' in response.links:
            url = response.links['next']['url']
            params = None  # Clear params since they're already in the next URL
        else:
            url = None
    
    return students

def fetch_submissions(course_id: str, user_id: int, include_history: bool = False) -> list:
        """Fetch all student submissions for a course (all assignments).

        Args:
            course_id: Canvas course ID.
            user_id: Canvas user ID.
            include_history: If True, include submission history.

        Returns:
            List of submission dictionaries. Each includes embedded assignment and user info.
        """
        submissions: list = []
        url = f"{API_BASE_URL}/courses/{course_id}/students/submissions"
        params = {
            'student_ids[]': user_id,
            "per_page": 100,
            "include[]": ["assignment", "rubric_assessment"] + (["submission_history"] if include_history else [])
        }

        print("Retrieving submissions...")
        while url:
            resp = requests.get(url, headers=HEADERS, params=params)
            resp.raise_for_status()
            submissions.extend(resp.json())
            # Handle pagination via Link headers
            if 'next' in resp.links:
                url = resp.links['next']['url']
                params = None  # already encoded in next URL
            else:
                url = None

        return submissions

def fetch_all_assignments(course_id: str) -> list:
    """Fetch all assignments for a given course.

    Args:
        course_id: Canvas course ID.
    
    Returns:
        List of assignment dictionaries.
    """
    assignments = []
    url = f"{API_BASE_URL}/courses/{course_id}/assignments"
    params = {
        "per_page": 100
    }

    while url:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        assignments.extend(response.json())
        if 'next' in response.links:
            url = response.links['next']['url']
            params = None
        else:
            url = None

    return assignments