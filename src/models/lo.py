from models.level import Level


class Lo:
    def __init__(self,
                 id: int,
                 name: str = "",
                 levels: dict[str, Level] = {},
                 module: int = -1):
        self.id = id
        self.name = name
        self.levels = levels
        self.module = module

    def has_level(self, name: str) -> bool:
        for level in self.levels:
            if name in level:
                return True
        return False

    def get_level(self, name: str) -> Level | None:
        for level_name, level in self.levels.items():
            if name in level_name.lower():
                return level
        return None

    def __repr__(self):
        return f"Lo={self.id=}, {self.name=}, {self.levels}"