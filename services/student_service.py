from repositories.student_repository import StudentRepository


class StudentService:
    def __init__(self, student_repository: StudentRepository):
        self.student_repository = student_repository

    def get_all_students(self):
        return self.student_repository.get_students()

    def get_student(self, student_id, name=None):
        """
        Retrieve a Student object by its ID or by their name.
        If name is provided, it will try to find the student by name
        if the ID is not found.
        """
        return self.student_repository.get_student(student_id, name)
    
    def get_student_ids(self):
        return [student.student_id for student in self.student_repository.get_students()]