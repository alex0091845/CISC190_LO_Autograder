from datetime import datetime
import os
from levels import Levels
from config import INSTRUCTOR_SIGNOFF, CURR_MODULE
from lo import LOs

class _ReportHelper:
    @staticmethod
    def _get_grade_on_track(lo_results: dict) -> str:
        completed_intern_dev_los = 0
        completed_junior_dev_los = 0
        completed_middle_dev_los = 0
        
        for _, results in lo_results.items():
            for level, [completed, _] in results.items():
                if level == Levels.INTERN and completed:
                    completed_intern_dev_los += 1
                elif level == Levels.JUNIOR and completed:
                    completed_junior_dev_los += 1
                elif level == Levels.MIDDLE and completed:
                    completed_middle_dev_los += 1
        
        if completed_middle_dev_los >= (CURR_MODULE - 1):
            return 'A'
        elif completed_middle_dev_los >= (CURR_MODULE - 2):
            return 'B'
        elif completed_junior_dev_los >= (CURR_MODULE - 2):
            return 'C'
        elif completed_intern_dev_los >= (CURR_MODULE - 2):
            return 'D'
        else:
            return 'F'

    @staticmethod
    def _get_progress_statement(letter_grade):
        if letter_grade == 'A':
            return 'Nice job! Keep it up.'
        elif letter_grade == 'B':
            return 'You might need to pick some things up but overall you\'re in a good shape!'
        elif letter_grade == 'C':
            return 'You might want to complete some of the explain videos!'
        else:
            return 'Please make up the work you\'ve fallen behind on!'
        
    @staticmethod
    def _list_assignments_or_status(lo_results: dict, target_level: str) -> str:
        result_lines = []
        
        for lo, results in lo_results.items():
            if LOs.LO_TO_MODULE_NUM[lo] > CURR_MODULE:
                break
                
            if target_level in results:
                completed, missing = results[target_level]
                if completed:
                    result_lines.append(f"- {lo}: Completed")
                else:
                    missing_list = ', '.join(missing)
                    result_lines.append(f"- {lo}: Incomplete assignments - {missing_list}")
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def _get_a_or_an(grade_on_track: str) -> str:
        return 'an' if grade_on_track == 'A' else 'a'
    
    @staticmethod
    def _get_overall_los(lo_results: dict) -> str:
        result_lines = []
        
        for lo, results in lo_results.items():
            level_grade = Levels.calculate_level_grade(results)
            result_lines.append(f"{lo}: Level {level_grade}")
        
        return '\n'.join(result_lines)

    @staticmethod
    def _get_grade(lo_results: dict) -> str:
        completed_intern_dev_los = 0
        completed_junior_dev_los = 0
        completed_middle_dev_los = 0
        completed_senior_dev_los = 0
        level_0s = 0
        level_1s = 0

        for _, results in lo_results.items():
            level_grade = Levels.calculate_level_grade(results)
            if level_grade == 0:
                level_0s += 1
            elif level_grade == 1:
                level_1s += 1

            for level, [completed, _] in results.items():
                if level == Levels.SENIOR and completed:
                    completed_senior_dev_los += 1
                elif level == Levels.MIDDLE and completed:
                    completed_middle_dev_los += 1
                elif level == Levels.JUNIOR and completed:
                    completed_junior_dev_los += 1
                elif level == Levels.INTERN and completed:
                    completed_intern_dev_los += 1
        
        if completed_senior_dev_los >= 7 and level_1s == 0 and level_0s == 0:
            return 'A'
        if completed_middle_dev_los >= 7 and level_1s == 0 and level_0s == 0:
            return 'B'
        if completed_junior_dev_los == 9:
            return 'C'
        if completed_intern_dev_los >= 6:
            return 'D'
        return 'F'


def generate_report(student_name, lo_results: dict, ) -> str:
    grade = _ReportHelper._get_grade(lo_results)
    a_or_an = _ReportHelper._get_a_or_an(grade)
    grade_on_track = _ReportHelper._get_grade_on_track(lo_results)
    a_or_an_on_track = _ReportHelper._get_a_or_an(grade_on_track)    # grammar lol
    # progress_statement = _ReportHelper._get_progress_statement(grade_on_track)
    list_assgn_or_status_c = _ReportHelper._list_assignments_or_status(lo_results, Levels.JUNIOR)
    list_assgn_or_status_b = _ReportHelper._list_assignments_or_status(lo_results, Levels.MIDDLE)
    overall_los = _ReportHelper._get_overall_los(lo_results)
    first_name = student_name.split()[0]

    _template = f"""Hi {first_name},

This is a progress message to let you know that your grade is at {a_or_an} {grade} ONLY if you don't submit any more assignments.

If you continue to (re)submit incomplete assignments, you're likely on track to {a_or_an_on_track} {grade_on_track}.

We're done with all modules and are now on the Final Project.

If you're looking to get a C, please complete all the following junior level assignments:
{list_assgn_or_status_c}

If you're looking to get a B, please complete some of the middle level assignments so that you complete 7 out of the 9 learning outcomes (LOs):
{list_assgn_or_status_b}

If you're looking to get an A, please complete the middle level assignments as listed above and also complete the final project.

Overall, your LOs look like this:
{overall_los}

Please let me know if you have any questions!

Best,
{INSTRUCTOR_SIGNOFF}
"""

    return _template

def save(report: str, student_name: str):
    # create a folder called reports if it doesn't exist
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # inside the reports folder, create another folder with the student's name
    student_folder = f"reports/{student_name.replace(' ', '_')}"
    if not os.path.exists(student_folder):
        os.makedirs(student_folder)

    # inside the student's folder, save the report as progress_report_<name>_<date>.txt
    date_str = datetime.now().strftime("%Y-%m-%d")

    filename = f"{student_folder}/progress_report_{student_name.lower().replace(' ', '_')}_{date_str}.txt"

    with open(filename, 'w') as file:
        file.write(report)