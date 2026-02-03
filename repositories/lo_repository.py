from yaml import Loader, load
from context.autograder_context import AutograderContext
from models.level import Level
from models.lo import Lo


class LoRepository:
    def __init__(self, context: AutograderContext):
        self.context = context
        self.los: dict[str, Lo] = {}  # Mapping of LO names to their details
        self._initialized = False

    def initialize_from_yaml(self, file_path: str):
        """Initialize the repository with a set of LOs.

        Args:
            los: A dictionary mapping LO names to Lo objects.
        """
        with open(file_path) as file:
            data = load(file, Loader=Loader)
            self._initialize_los(data)
            
        self._initialized = True

    def evaluate(self, **params):
        for lo_name, lo in self.los.items():
            print(f"Evaluating LO: {lo_name}")
            for level_name, level in lo.levels.items():
                result = level.evaluate(**params)
                print(f"  Level: {level_name}, Result: {result}")
    
    def get_lo_by_name(self, lo_name: str, exact_match: bool=True) -> Lo | None:
        if exact_match:
            return self.los.get(lo_name)
        else:
            for name, lo in self.los.items():
                if lo_name in name:
                    return lo
    
    def is_initialized(self) -> bool:
        return self._initialized
    
    def _initialize_los(self, los_data: dict):
        lo_list = los_data.get("learning_outcomes", [])

        for lo_data in lo_list:
            lo_name = list(lo_data.keys())[0]

            lo = Lo(id=-1, name=lo_name)

            levels = self._initialize_levels(lo_data[lo_name].get("levels", []))
            lo.levels = levels

            self.los[lo_name] = lo
        
        print(f"Initialized LOs: {list(self.los.keys())}")

    def _initialize_levels(self, levels_data: dict) -> dict[str, Level]:
        levels = {}
        for level_data in levels_data:
            level = Level.from_yaml(level_data)
            print(f"{level=}")
            levels[level.name] = level
        
        return levels