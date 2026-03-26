import json

from pathlib import Path


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
        """Load data from a JSON file. Returns None if the file does not exist."""
        path = Path(str(file_path) + ".json")
        if not path.exists():
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def save_json(self, dir_path, filename, data):
        """
        Save data to a json file in the corresponding course directory.
        
        Args:
            dir_path: The path to the directory where the file will be saved
            filename: The name of the file to save (without the extension)
            data: The data to save
        """
        # Create directory if doesn't exist
        self.create_directory(dir_path)

        # Extract only name and id from students
        # students_data = [
        #     {
        #         "id": student.get("id"),
        #         "name": student.get("name"),
        #         "sortable_name": student.get("sortable_name")
        #     }
        #     for student in students
        # ]

        file_path = dir_path / (filename + ".json")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved data to {file_path}")
        return file_path