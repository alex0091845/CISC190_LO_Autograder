class Levels:
    INTERN = "🌱 Intern (Level 1)"
    JUNIOR = "🌿🌿 Junior Developer (Level 2)"
    MIDDLE = "🌼🌼🌼 Middle Developer (Level 3)"
    SENIOR = "🌳🌳🌳🌳 Senior Developer (Level 4)"

    @staticmethod
    def calculate_level_grade(completed_levels: dict) -> int:
        """Calculates the numeric level grade based on completed levels.
        Args:
            completed_levels: A dictionary mapping level names to booleans indicating
                              whether the level is complete.
        Returns:
            An integer representing the numeric level grade."""
        if Levels._get_level(completed_levels, Levels.MIDDLE):
            if Levels._get_level(completed_levels, Levels.SENIOR):
                return 4
            return 3
        if Levels._get_level(completed_levels, Levels.JUNIOR):
            return 2
        if Levels._get_level(completed_levels, Levels.INTERN):
            return 1
        
        return 0
    
    @staticmethod
    def _get_level(completed_levels, level_name):
        print(f"Checking level {level_name}: {completed_levels.get(level_name, (False, []))[0]}")
        return completed_levels.get(level_name, (False, []))[0]