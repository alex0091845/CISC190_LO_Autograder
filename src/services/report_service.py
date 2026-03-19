from datetime import datetime
from models.student import Student
from utils.naming import get_student_folder_name
from utils.paths import BASE_DIR
from context.autograder_context import AutograderContext
from models.level import Level
from models.requirements.lo_result import LoResult
from repositories.report_repository import ReportRepository
from services.grade_service import GetGradeType, GradeService
from services.lo_service import LoService


class ReportService:
    def __init__(self,
                 context: AutograderContext,
                 report_repository: ReportRepository,
                 grade_service: GradeService,
                 lo_service: LoService,
                 instructor_signoff: str = "N/A"):
        self.context = context
        self.report_repository = report_repository
        self.grade_service = grade_service
        self.lo_service = lo_service
        self.instructor_signoff = instructor_signoff

    def generate_report(self,
                        student_name: str,
                        lo_results_mappings: dict[str, LoResult]) -> str:
        grade_type = GetGradeType(self.context.grade_type)
        grade = self.grade_service.get_grade(grade_type, lo_results_mappings)
        first_name = student_name.split()[0]

        a_or_an = self._get_a_or_an(grade)
        list_assgn_or_status_c = self._list_assignments_or_status(lo_results_mappings, Level.JUNIOR)
        list_assgn_or_status_b = self._list_assignments_or_status(lo_results_mappings, Level.MIDDLE)
        list_assgn_or_status_a = self._list_assignments_or_status(lo_results_mappings, Level.SENIOR)
        overall_los = self._get_overall_los(lo_results_mappings)

        curr_module = self.context.curr_module

        match grade_type:
            case GetGradeType.DEFINITE:
                return f"""Hi {first_name},

This is a progress message to let you know that your grade is at {a_or_an} {grade} ONLY if you don't submit any more assignments.

If you continue to (re)submit incomplete assignments, you're likely on track to {a_or_an} {grade}.

We're done with all modules and are now on the Final Project.

If you're looking to get a C, please complete all the following junior level assignments:
{list_assgn_or_status_c}

If you're looking to get a B, please complete some of the middle level assignments so that you complete 7 out of the 9 learning outcomes (LOs):
{list_assgn_or_status_b}

If you're looking to get an A, please complete the middle level assignments as listed above AND demonstrate any 7 out of the 9 Senior developer level assignments (most of them are from the final project).
{list_assgn_or_status_a}

Overall, your LOs look like this:
{overall_los}

Please let me know if you have any questions!

Best,
{self.instructor_signoff}
"""
            
            case _:  # default too
                progress_statement = self._get_progress_statement(grade)

                return f"""Hi {first_name},

This is a progress message to let you know you're on track to {a_or_an} {grade}. {progress_statement}

We're on module {curr_module}.

If you're looking to get a C, please complete all the following junior level assignments:
{list_assgn_or_status_c}

If you're looking to get a B, please complete some of the middle level assignments so that you complete 7 out of the 9 learning outcomes (LOs):
{list_assgn_or_status_b}

If you're looking to get an A, please complete the middle level assignments as listed above AND demonstrate any 7 out of the 9 Senior developer level assignments (most of them are from the final project).
{list_assgn_or_status_a}

Overall, your LOs look like this:
{overall_los}

Please let me know if you have any questions!

Best,
{self.instructor_signoff}
"""
    
    def generate_reports(self, student_list: list[Student], lo_results_mappings: dict[int, dict[str, LoResult]]):
        """
        Generate and save progress reports for each student based on their LO results.
        
        Args:
            student_list: List of Student objects to generate reports for.
            lo_results_mappings: Dictionary mapping LO names to their evaluation results for each student.
        Returns:
            None
        """
        for student in student_list:
            report = self.generate_report(student.name, lo_results_mappings.get(student.student_id, {}))
            self.save(report, student.name)

    def get_latest_report(self, student_name: str):
        return self.report_repository.get_latest_report(student_name)

    def save(self, report: str, student_name: str):
        reports_dir = BASE_DIR / "user_data" / "reports"
        student_folder = reports_dir / get_student_folder_name(student_name)
        student_folder.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = student_folder / f"progress_report_{student_name.lower().replace(' ', '_')}_{date_str}.txt"

        with open(filename, 'w') as file:
            file.write(report)

    def _get_a_or_an(self, grade_on_track: str) -> str:
        '''
        Helper method to get "a" or "an" as prefix to a grade for good grammar.
        
        :param self: Description
        :param grade_on_track: Description
        :type grade_on_track: str
        :return: Description
        :rtype: str
        '''
        return 'an' if grade_on_track == 'A' else 'a'
    
    def _get_progress_statement(self, letter_grade):
        '''
        Returns how well they're doing--some words of encouragement or a bit of a push.
        
        :param self: Description
        :param letter_grade: Description
        '''
        if letter_grade == 'A':
            return 'Nice job! Keep it up.'
        elif letter_grade == 'B':
            return 'You might need to pick some things up but overall you\'re in a good shape!'
        elif letter_grade == 'C':
            return 'You might want to complete some of the explain videos!'
        else:
            return 'Please make up the work you\'ve fallen behind on!'
    
    def _list_assignments_or_status(self, 
                                    lo_results_mappings: dict[str, LoResult],
                                    target_level: str) -> str:
        '''
        Returns a string where, for each LO, list the missing assignments if any,
        or that it's completed.
        
        :param self: Description
        :param lo_results_mappings: Description
        :type lo_results_mappings: dict[str, LoResult]
        :param target_level: Description
        :type target_level: str
        :return: Description
        :rtype: str
        '''
        result_lines = []
        
        for lo_name, results in lo_results_mappings.items():
            lo = self.lo_service.get_lo_by_name(lo_name)

            if not lo: continue
            if lo.module > self.context.curr_module: continue
            if not results.level_results: continue
            if not target_level in results.level_results: continue

            requirement_result = results.level_results[target_level]

            if not requirement_result: continue

            satisfied, missing = requirement_result.satisfied, requirement_result.missing
            if satisfied:
                result_lines.append(f"- {lo_name}: Completed")
            else:
                missing_list = ', '.join(missing)
                result_lines.append(f"- {lo_name}: Incomplete assignments - {missing_list}")
        
        return '\n'.join(result_lines)
    
    def _get_overall_los(self, lo_results_mappings: dict[str, LoResult]) -> str:
        '''
        Get the overall LO levels for each level.
        
        :param self: Description
        :param lo_results_mappings: Description
        :type lo_results_mappings: dict[str, LoResult]
        :return: Description
        :rtype: str
        '''
        result_lines = []
        
        for lo, results in lo_results_mappings.items():
            result_lines.append(f"{lo}: Level {results.level_score}")
        
        return '\n'.join(result_lines)