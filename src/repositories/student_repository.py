from api.api import CanvasApi
from managers.file_manager import FileManager
from utils.paths import BASE_DIR
from models.course import Course
from models.student import Student


class StudentRepository:
    def __init__(self, file_manager: FileManager, course: Course, api: CanvasApi) -> None:
        # id to students
        self.students: dict[int, Student] = {}
        self.course = course
        self.file_manager = file_manager
        self.api = api
        self._load_if_saved_locally()

    def get_students(self) -> list[Student]:
        """Retrieve a list of all Student objects."""
        return list(self.students.values())

    def get_student(self, student_id: int, name: str | None) -> Student:
        """Retrieve a Student object by its ID or by their name."""
        if not student_id in self.students:
            # If student_id is not in self.students, try to find student by name
            for student in self.students.values():
                if student.name == name:
                    return student
            raise ValueError(f"No student found with id: {student_id} or name: {name}")
        return self.students[student_id]
    
    def create_student(self, student_id: int, name: str) -> Student:
        """Create a new Student object and add it to the repository."""
        student = Student(student_id, name)
        self.students[student_id] = student
        return student
    
    def _load_students_from_canvas(self):
        """Load students from Canvas API."""
        students_data = self.api.get_all_students(self.course.id)
        for student_dict in students_data:
            student_id = student_dict.get("id")
            name = student_dict.get("name", "")
            student = self.create_student(student_id, name)
            self.students[student_id] = student

    def _load_if_saved_locally(self) -> bool:
        """Load students from local filesystem if available."""

        course_name = self.course.name
        file_path = BASE_DIR / "user_data" / "courses" / course_name / "students.json"
        if file_path.exists():
            students_data = self.file_manager.load_json(file_path)
            for student_dict in students_data:
                student_id = student_dict.get("id")
                name = student_dict.get("name", "")
                student = self.create_student(student_id, name)

                self.students[student_id] = student
            print(f"Loaded {len(self.students)} students from {file_path}")
            return True
        
        # If not saved locally, load from Canvas API and save locally for next time
        self._load_students_from_canvas()
        return False