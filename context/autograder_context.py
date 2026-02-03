class AutograderContext:
    def __init__(self, course_id: str):
        self.course_id = course_id
        self._context_data = {}

    def set(self, key: str, value):
        self._context_data[key] = value
    
    def get(self, key: str, default=None):
        return self._context_data.get(key, default)