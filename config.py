import os
from dotenv import load_dotenv

load_dotenv()

# --- Configuration (values are loaded from .env) ---
CANVAS_DOMAIN = os.getenv("CANVAS_DOMAIN", "sdccd.instructure.com")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN", "")
COURSE_ID = os.getenv("COURSE_ID", "")
INSTRUCTOR_SIGNOFF = os.getenv("INSTRUCTOR_SIGNOFF", "Instructor")
CURR_MODULE = int(os.getenv("CURR_MODULE", "1"))

# ---------------------

# Headers for all API calls
HEADERS = {
    "Authorization": f"Bearer {CANVAS_TOKEN}",
    # Note: We do NOT explicitly set Content-Type: application/json here.
    # The 'requests' library will correctly set it to 'application/x-www-form-urlencoded'
    # when we use the 'data' parameter in the POST request.
}
API_BASE_URL = f"https://{CANVAS_DOMAIN}/api/v1"