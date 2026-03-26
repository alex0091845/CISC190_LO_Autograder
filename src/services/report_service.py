from datetime import datetime
from string import Template

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
                        lo_results_mappings: dict[str, LoResult],
                        max_module: int) -> str:
        grade_type = GetGradeType(self.context.grade_type)
        grade = self.grade_service.get_grade(grade_type, lo_results_mappings)
        first_name = student_name.split()[0]

        a_or_an = self._get_a_or_an(grade)
        progress_statement = self._get_progress_statement(grade)
        list_assgn_or_status_c = self._list_assignments_or_status(lo_results_mappings, Level.JUNIOR)
        list_assgn_or_status_b = self._list_assignments_or_status(lo_results_mappings, Level.MIDDLE)
        list_assgn_or_status_a = self._list_assignments_or_status(lo_results_mappings, Level.SENIOR)
        overall_los = self._get_overall_los(lo_results_mappings, max_module)

        template_file = (
            "report_definite_template.txt"
            if grade_type == GetGradeType.DEFINITE
            else "report_on_track_template.txt"
        )
        with open(str(BASE_DIR / "user_data" / template_file)) as f:
            template = Template(f.read())

        return template.safe_substitute(
            first_name=first_name,
            a_or_an=a_or_an,
            curr_module=self.context.curr_module,
            grade=grade,
            progress_statement=progress_statement,
            list_assgn_or_status_c=list_assgn_or_status_c,
            list_assgn_or_status_b=list_assgn_or_status_b,
            list_assgn_or_status_a=list_assgn_or_status_a,
            overall_los=overall_los,
            instructor_signoff=self.instructor_signoff,
        )
    
    def generate_reports(self,
                         student_list: list[Student],
                         lo_results_mappings: dict[int, dict[str, LoResult]],
                         max_module: int):
        """
        Generate and save progress reports for each student based on their LO results.
        
        Args:
            student_list: List of Student objects to generate reports for.
            lo_results_mappings: Dictionary mapping LO names to their evaluation results for each student.
        Returns:
            None
        """
        for student in student_list:
            report = self.generate_report(student.name,
                                          lo_results_mappings.get(student.student_id, {}),
                                          max_module)
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
        :param target_level: The level to list the assignments for (Intern, Junior, etc.)
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
    
    def _get_overall_los(self,
                         lo_results_mappings: dict[str, LoResult],
                         max_module: int) -> str:
        '''
        Get the overall LO levels for each level.
        
        :param self: Description
        :param lo_results_mappings: Description
        :type lo_results_mappings: dict[str, LoResult]
        :return: Description
        :rtype: str
        '''
        result_lines = []
        
        for lo_name, results in lo_results_mappings.items():
            lo = self.lo_service.get_lo_by_name(lo_name)

            if lo and lo.module <= max_module:
                result_lines.append(f"{lo_name}: Level {results.level_score}")
        
        return '\n'.join(result_lines)