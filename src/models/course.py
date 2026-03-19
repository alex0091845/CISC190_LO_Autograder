from dataclasses import dataclass

from api.api import CanvasApi


@dataclass
class Course:
    id: str
    name: str = ""

    def fetch_name(self, api: CanvasApi):
        if self.name == "":
            self._init_default_course_name(api)

    def _init_default_course_name(self, api: CanvasApi):
        '''
        A private helper method to initialize the course name as:
        COURSE_ID - COURSE_NAME

        Where all special characters are replaced with underscores.
        '''
        # Get course information to get the course name
        course_info = api.get_course_info(self.id)
        course_name = course_info.get('name', 'Unknown Course')
        
        # Sanitize course name for use in directory name (remove special characters)
        safe_course_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in course_name)
        safe_course_name = safe_course_name.strip().replace(' ', '_')
        
        self.name = f"{self.id} - {safe_course_name}"