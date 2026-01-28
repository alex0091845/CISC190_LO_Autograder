# --- Configuration ---
# You MUST replace these placeholders with your actual values
CANVAS_DOMAIN = "sdccd.instructure.com"
CANVAS_TOKEN = "YOUR_API_ACCESS_TOKEN"
COURSE_ID = "YOUR_COURSE_ID"          # The Course ID (e.g., 12345)

# ---------------------

# Headers for all API calls
HEADERS = {
    "Authorization": f"Bearer {CANVAS_TOKEN}",
    # Note: We do NOT explicitly set Content-Type: application/json here.
    # The 'requests' library will correctly set it to 'application/x-www-form-urlencoded'
    # when we use the 'data' parameter in the POST request.
}
API_BASE_URL = f"https://{CANVAS_DOMAIN}/api/v1"
INSTRUCTOR_SIGNOFF = "YOUR NAME"
CURR_MODULE = 1     # Current module number for LO grading. Could be 1, 2, ...