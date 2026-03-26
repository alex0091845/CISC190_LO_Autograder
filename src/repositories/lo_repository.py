from yaml import Loader, load
from context.autograder_context import AutograderContext
from managers.file_manager import FileManager
from models.level import Level
from models.lo import Lo
from models.requirements.lo_result import LoResult
from models.requirements.requirement_result import RequirementResult
from utils.naming import get_student_folder_name


class LoRepository:
    def __init__(self,
                 context: AutograderContext,
                 file_manager: FileManager):
        self.context = context
        self.file_manager = file_manager
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
            raise ValueError("The parameter 'lo' is required in LoRepository.evaluate()")
        
        lo_name = lo.name
        student = params.get("student")
        use_cache = params.get("use_cache", False)

        # If caching is enabled, check for an existing result before evaluating.
        if use_cache:
            if not student:
                raise ValueError("The parameter 'student' is required when use_cache=True")

            cache_file = (self.context.path_config.students_eval_cache_dir() /
                          get_student_folder_name(student.name))
            cached_data = self.file_manager.load_json(file_path=cache_file)

            if cached_data and lo_name in cached_data:
                print(f"Using cached result for LO {lo_name} for student {student.name}")
                lo_result = LoResult.from_dict(cached_data[lo_name])
                self.lo_results[lo_name] = lo_result
                return lo_result

        # Evaluate all levels otherwise.
        print(f"Evaluating LO: {lo_name}")
        level_results: dict[str, RequirementResult | None] = {}
        for level_name, level in lo.levels.items():
            result = level.evaluate(**params)
            level_results[level_name] = result
            print(f"  Level: {level_name}, Result: {result}")

        lo_result = LoResult(level_results)
        self.lo_results[lo_name] = lo_result

        # Persist to the student's cache file, merging with any existing LO results.
        if student:
            cache_dir = self.context.path_config.students_eval_cache_dir()
            cache_filename = get_student_folder_name(student.name)
            existing_data = self.file_manager.load_json(
                file_path=cache_dir / cache_filename
            ) or {}
            existing_data[lo_name] = lo_result.to_dict()
            self.file_manager.save_json(        # automatically merges
                dir_path=cache_dir,
                filename=cache_filename,
                data=existing_data,
            )

        return lo_result

    def evaluate_multiple(self,
                          student,
                          lo_list: list,
                          use_cache: bool = False,
                          **params) -> dict[str, LoResult]:
        """Evaluate all LOs for a single student.

        Loads the student's cache file once, evaluates any LOs not already
        cached, then writes everything back in a single save.

        Returns:
            A dict mapping LO name -> LoResult for this student.
        """
        cache_dir = self.context.path_config.students_eval_cache_dir()
        cache_filename = get_student_folder_name(student.name)

        # Load the student's existing cache once.
        cached_data = self.file_manager.load_json(
            file_path=cache_dir / cache_filename
        ) or {}

        results: dict[str, LoResult] = {}
        evaluated_new = False

        for lo in lo_list:
            if lo is None:
                continue
            lo_name = lo.name

            if use_cache and lo_name in cached_data:
                print(f"Using cached result for LO {lo_name} for student {student.name}")
                lo_result = LoResult.from_dict(cached_data[lo_name])
            else:
                print(f"Evaluating LO: {lo_name}")
                level_results: dict[str, RequirementResult | None] = {}
                for level_name, level in lo.levels.items():
                    result = level.evaluate(student=student,
                                            student_id=student.student_id,
                                            lo=lo,
                                            **params)
                    level_results[level_name] = result
                    print(f"  Level: {level_name}, Result: {result}")
                lo_result = LoResult(level_results)
                cached_data[lo_name] = lo_result.to_dict()
                evaluated_new = True

            self.lo_results[lo_name] = lo_result
            results[lo_name] = lo_result

        # Write back only if something new was evaluated.
        if evaluated_new:
            self.file_manager.save_json(
                dir_path=cache_dir,
                filename=cache_filename,
                data=cached_data,
            )

        return results
    
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
    
    def load_cached_results(self, student) -> dict[str, LoResult]:
        """Load all cached LO results for a student from disk without any network calls.

        Returns:
            A dict mapping LO name -> LoResult, or an empty dict if no cache exists.
        """
        cache_dir = self.context.path_config.students_eval_cache_dir()
        cached_data = self.file_manager.load_json(
            file_path=cache_dir / get_student_folder_name(student.name)
        ) or {}

        results: dict[str, LoResult] = {}
        for lo_name, lo_data in cached_data.items():
            lo_result = LoResult.from_dict(lo_data)
            self.lo_results[lo_name] = lo_result
            results[lo_name] = lo_result

        return results

    def get_lo_result_by_name(self, lo_name: str):
        return self.lo_results[lo_name]
    
    def get_lo_id_by_name(self, lo_name: str):
        lo = self.get_lo_by_name(lo_name)

        if lo is None:
            return "-1"
        
        return lo.id