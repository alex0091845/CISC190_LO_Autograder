class CanvasService:
    def __init__(self, api_client: CanvasAPIClient, cache: CacheManager):
        self.api = api_client
        self.cache = cache
    
    def get_students(self, course_id: str, use_cache: bool = True) -> List[Student]:
        cache_key = f"students_{course_id}"
        if use_cache and self.cache.has(cache_key):
            return self.cache.get(cache_key)
        
        students = self.api.fetch_students(course_id)
        self.cache.set(cache_key, students)
        return students