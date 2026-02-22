from yaml import Loader, load
from context.autograder_context import AutograderContext
from models.level import Level
from models.lo import Lo
from models.requirements.lo_result import LoResult
from models.requirements.requirement_result import RequirementResult


class LoRepository:
    def __init__(self, context: AutograderContext):
        self.context = context
        self.los: dict[str, Lo] = {}  # Mapping of LO names to Lo objects
        self.lo_results: dict[str, LoResult] = {}
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

    def evaluate(self, **params) -> LoResult:
        lo = params.get("lo")
        if not lo:
            raise Warning("The parameter 'lo' should be passed into LoService.evaluate() as an Lo object")
        
        lo_name = lo.name
        level_results: dict[str, RequirementResult | None] = {}

        print(f"Evaluating LO: {lo_name}")

        for level_name, level in lo.levels.items():
            result = level.evaluate(**params)
            level_results[level_name] = result
            print(f"  Level: {level_name}, Result: {result}")
        
        lo_result = LoResult(level_results)
        self.lo_results[lo_name] = lo_result

        return lo_result
    
    def get_lo_by_name(self, lo_name: str, exact_match: bool=False) -> Lo | None:
        if exact_match:
            return self.los.get(lo_name)
        else:
            for name, lo in self.los.items():
                if lo_name in name:
                    return lo
    
    def is_initialized(self) -> bool:
        return self._initialized
    
    def _initialize_los(self, los_data: dict):
        """
        A helper method to initialize Lo objects from the provided data.

        Args:
            los_data: A dictionary containing LO definitions.
        Returns:
            None
        """
        lo_list = los_data.get("learning_outcomes", [])

        for lo_data in lo_list:
            lo_name = list(lo_data.keys())[0]
            lo_module = lo_data[lo_name].get("module", -1)

            lo = Lo(id=-1, name=lo_name, module=lo_module)

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
    
    def get_lo_result_by_name(self, lo_name: str):
        return self.lo_results[lo_name]
    
    def get_lo_id_by_name(self, lo_name: str):
        lo = self.get_lo_by_name(lo_name)

        if lo is None:
            return "-1"
        
        return lo.id