from typing import Any

import requests
from config import API_BASE_URL, HEADERS

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

def fetch_assignment_rubric(course_id, assignment_id):
    """
    Get the rubric for a specific assignment.
    
    Args:
        course_id: The Canvas course ID
        lo_id: The Canvas learning outcome (LO) assignment ID
        
    Returns:
        A list of dictionary containing the rubric data, or None if no rubric exists
    """
    url = f"{API_BASE_URL}/courses/{course_id}/assignments/{assignment_id}"
    params = {
        'include[]': ['rubric', 'rubric_assessment']
    }

    print(f"{url=}")
    
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    
    assignment = response.json()

    return assignment.get('rubric')

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

def update_assignment_score_and_rubric(
        course_id: str,
        assignment_id: int,
        user_id: int,
        score: float,
        rubric_criteria_scores: dict[str, dict[str, Any]]
    ) -> dict[str, Any] | None:
    """
    Updates the overall grade and the scores for individual rubric criteria
    for a specific user's submission on a target assignment.

    Args:
        course_id: The ID of the course.
        assignment_id: The ID of the assignment to grade.
        user_id: The ID of the student whose submission is being graded.
        score: The total score to post (e.g., 85.0).
        rubric_criteria_scores: A dictionary mapping the rubric criterion ID (string)
                                to the score awarded for that criterion (float).
                                Example: {'<crit1_id>': {'points': 3, 'rating_id': 'rat1'},
                                            '<crit2_id>': {'points': 5, 'rating_id': 'rat2', 'comments': 'Well Done'}}
                                Note: We transform this dictionary into the following reference string format:
                                    rubric_assessment[crit1][points]=3&rubric_assessment[crit1][rating_id]=rat1&
                                    rubric_assessment[crit2][points]=5&rubric_assessment[crit2][rating_id]=rat2&
                                    rubric_assessment[crit2][comments]=Well%20Done.

    Returns:
        The JSON response object from the API upon success, or None on failure.
    """
    print(f"\n--- Updating Submission for User {user_id} on Assignment {assignment_id} ---")

    url = f"{API_BASE_URL}/courses/{course_id}/assignments/{assignment_id}/submissions/{user_id}"

    # Build the payload as form data with the nested rubric assessment structure
    payload = {
        "submission[posted_grade]": str(score)
    }
    
    # Transform rubric_criteria_scores into the form-encoded format Canvas expects
    for criterion_id, crit_data in rubric_criteria_scores.items():
        payload[f"rubric_assessment[{criterion_id}][points]"] = str(crit_data['points'])
        payload[f"rubric_assessment[{criterion_id}][rating_id]"] = crit_data['rating_id']
        if 'comments' in crit_data:
            payload[f"rubric_assessment[{criterion_id}][comments]"] = crit_data['comments']

    try:
        # Note: Canvas requires a PUT request for grading submissions.
        # Use 'data' parameter (not json) to send as form-encoded
        response = requests.put(url, headers=HEADERS, data=payload)
        response.raise_for_status() # Check for bad status code
        
        print(f"Successfully posted grade: {score} and updated {len(rubric_criteria_scores)} rubric criteria.")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error updating submission: {e}")
        print(f"Status Code: {e.response.status_code}")
        print(f"Response content: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None