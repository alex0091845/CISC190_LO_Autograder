from pathlib import Path


## Possibly need to refactor so that the user can choose where to put their files.
class PathConfig:
    def __init__(self, base_dir: Path, course_name: str):
        self.base_dir = base_dir
        self.course_name = course_name

    @property
    def students_file(self) -> Path:
        return self.base_dir / "user_data" / "courses" / self.course_name / "students.json"
    
    def students_dir(self) -> Path:
        return self.base_dir / "user_data" / "courses" / self.course_name
    
    def students_eval_cache_dir(self) -> Path:
        return self.base_dir / "user_data" / "cache" / self.course_name

    @property
    def reports_dir(self) -> Path:
        return self.base_dir / "user_data" / "reports"

    @property
    def lo_requirements_file(self) -> Path:
        return self.base_dir / "user_data" / "requirements" / f"{self.course_name}_requirements.yaml"

    def lo_cache_file(self, student_id: int) -> Path:
        return self.base_dir / "user_data" / "cache" / self.course_name / f"{student_id}.json"

    def report_file(self, student_folder: str, filename: str) -> Path:
        return self.reports_dir / student_folder / filename