import json

from pathlib import Path
from utils.paths import BASE_DIR


class FileManager:
    def __init__(self):
        pass

    def create_directory(self, dir_name):
        """Create a new directory in the filesystem."""
        dir_path = Path(dir_name)

        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        return dir_path
    
    def load_json(self, file_path):
        """Load data from a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    # TODO: possibly generalize this to just save?
    def save_students(self, students, course_name):
        """
        Save student data to a file named 'students.json' in the corresponding
        course directory.
        
        Args:
            students: List of student dictionaries from Canvas API
            course_name: The course name
        """
        # Create directory if doesn't exist
        dir_path = BASE_DIR / "user_data" / "courses" / course_name
        self.create_directory(dir_path)

        # Extract only name and id from students
        students_data = [
            {
                "id": student.get("id"),
                "name": student.get("name"),
                "sortable_name": student.get("sortable_name")
            }
            for student in students
        ]

        file_path = dir_path / "students.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(students_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(students_data)} students to {file_path}")
        return file_path