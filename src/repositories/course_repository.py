from managers.file_manager import FileManager
from models.course import Course


class CourseRepository:
    def __init__(self, file_manager: FileManager) -> None:
        # A dictionary to hold course_id to Course object mapping
        self.courses = {}
        self.file_manager = file_manager
    
    def get_course(self, course_id: str) -> Course:
        """
        Retrieve a Course object by its ID, creating it if it doesn't exist.
        
        Args:
            course_id (str): The unique identifier for the course.
        """
        if course_id not in self.courses:
            self.create_course(course_id)
        return self.courses[course_id]

    def create_course(self, course_id: str, course_name: str="") -> Course:
        """
        Create a new Course object and store it in the repository.
        
        Args:
            course_id (str): The unique identifier for the course.
            course_name (str): The name of the course. If empty, it will be initialized.
        """
        course = Course(course_id, course_name)
        self.courses[course_id] = course
        self.file_manager.create_directory(f"courses/{course.name}")
        return course