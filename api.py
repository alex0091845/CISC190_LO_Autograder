import requests
from config import API_BASE_URL, HEADERS


def get_course_info(course_id):
    """Retrieve course information by course ID by sending a GET request to the Canvas API."""
    url = f"{API_BASE_URL}/courses/{course_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Raise an error for bad responses
    return response.json()