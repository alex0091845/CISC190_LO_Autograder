from pathlib import Path
from managers.file_manager import FileManager
from models.course import Course
from models.student import Student


class StudentRepository:
    def __init__(self, file_manager: FileManager, course: Course) -> None:
        self.students: dict[int, Student] = {}
        self.course = course
        self.file_manager = file_manager
        self._load_if_saved_locally()

    def get_student(self, student_id: int) -> Student:
        """Retrieve a Student object by its ID, creating it if it doesn't exist."""
        if student_id not in self.students:
            self.create_student(student_id)
        return self.students[student_id]
    
    def create_student(self, student_id: int, name: str="") -> Student:
        """Create a new Student object and store it in the repository."""
        student = Student(student_id, name)
        self.students[student_id] = student
        return student

    def _load_if_saved_locally(self):
        """Load students from local filesystem if available."""

        course_name = self.course.name
        file_path = Path("courses") / course_name / "students.json"
        if file_path.exists():
            students_data = self.file_manager.load_json(file_path)
            for student_dict in students_data:
                student_id = student_dict.get("id")
                name = student_dict.get("name", "")
                student = self.create_student(student_id, name)

                self.students[student_id] = student
            print(f"Loaded {len(self.students)} students from {file_path}")