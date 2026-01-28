import requests
import json
import os
from pathlib import Path
from config import API_BASE_URL, COURSE_ID, HEADERS


class Students:
    def __init__(self) -> None:
        self.students = get_all_students(COURSE_ID)
        
def get_all_students(course_id, save_cache=True):
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
    
    if save_cache:
        # cache; students rarely change. If needed, can refresh
        save_students_to_json(students, course_id)
    
    return students

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
    response.raise_for_status()
    return response.json()

def save_students_to_json(students, course_id):
    """
    Save student names and IDs to a JSON file in courses/<COURSE_ID - COURSE_NAME>/students.json
    
    Args:
        students: List of student dictionaries from Canvas API
        course_id: The Canvas course ID
    """
    # Get course information to get the course name
    course_info = get_course_info(course_id)
    course_name = course_info.get('name', 'Unknown Course')
    
    # Sanitize course name for use in directory name (remove special characters)
    safe_course_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in course_name)
    safe_course_name = safe_course_name.strip().replace(' ', '_')
    
    # Create directory path: courses/<COURSE_ID - COURSE_NAME>
    dir_name = f"{course_id} - {safe_course_name}"
    dir_path = Path("courses") / dir_name
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Extract only name and id from students
    students_data = [
        {
            "id": student.get("id"),
            "name": student.get("name"),
            "sortable_name": student.get("sortable_name")
        }
        for student in students
    ]
    
    # Save to JSON file
    file_path = dir_path / "students.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(students_data, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(students_data)} students to {file_path}")
    return file_path