import argparse
from config import *
from repositories.student_repository import *
from assignments import Assignments
from lo import LOs
from rubric import *
from student_report import generate_report, save

class GradeSync:
    def __init__(self, student_names=None, student_ids=None, los=None, 
                 generate_reports=True, save_reports=True) -> None:
        self.roster = Students()
        self.los = LOs()
        self.rubric = Rubric()
        self.student_names = student_names
        self.student_ids = student_ids
        self.los_to_grade = los
        self.generate_reports = generate_reports
        self.save_reports = save_reports

    def _should_process_student(self, student):
        """Determine if this student should be processed based on filters."""
        # If no filters specified, process all students
        if not self.student_names and not self.student_ids:
            return True
        
        # Check if student matches name filter
        if self.student_names:
            for name_filter in self.student_names:
                if name_filter.lower() in student['name'].lower():
                    return True
        
        # Check if student matches ID filter
        if self.student_ids:
            if str(student['id']) in self.student_ids:
                return True
        
        return False

    def _get_los_to_process(self):
        """Determine which LOs to process based on filters."""
        if self.los_to_grade:
            # Filter to only requested LOs
            return [lo for lo in LOs.LO_NAMES[0:LOs.MODULE_NUM_TO_LO_NUM[CURR_MODULE]] 
                    if lo in self.los_to_grade]
        else:
            # Process all LOs up to current module
            return LOs.LO_NAMES[0:LOs.MODULE_NUM_TO_LO_NUM[CURR_MODULE]]

    def sync(self):
        # for each student
        for student in self.roster.students:
            if not self._should_process_student(student):
                continue
            
            student_id = student['id']

            print(f"--- Syncing grades for student {student['name']} (ID: {student_id}) ---")

            # "grades" the student for this LO and return a dictionary of whether they completed
            # the levels and also what assignments they're missing (incomplete)
            lo_results = Assignments.grade(student_id, LOs.reqs)

            # Get LOs to process
            los_to_process = self._get_los_to_process()
            for lo in los_to_process:
                # update rubric ratings and points assessment for this student & LO
                self.rubric.update_rubric_assessment(lo_results, lo, student_id)

            # take lo_results and generate a progress report
            if self.generate_reports:
                report = generate_report(student['name'], lo_results)
                if self.save_reports:
                    save(report, student['name'])
                else:
                    print("\n" + report)

    class GradeSyncBuilder:
        def _init(self):
            return self


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Sync grades for students based on learning outcomes.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Grade all students
  python sync_grades.py
  
  # Grade specific students by name
  python sync_grades.py --names "Alex" "Tasha"
  
  # Grade specific students by ID
  python sync_grades.py --ids 12345 67890
  
  # Grade specific LOs only
  python sync_grades.py --los "LO1" "LO2"
  
  # Generate reports but don't save them
  python sync_grades.py --no-save
  
  # Don't generate reports at all
  python sync_grades.py --no-report
  
  # Combine filters
  python sync_grades.py --names "Alex" --los "LO1" "LO3" --no-save
        """
    )
    
    parser.add_argument(
        '--names', '-n',
        nargs='+',
        help='Filter by student names (partial matches allowed). Example: --names "Alex" "Tasha"'
    )
    
    parser.add_argument(
        '--ids', '-i',
        nargs='+',
        help='Filter by student IDs. Example: --ids 12345 67890'
    )
    
    parser.add_argument(
        '--los', '-l',
        nargs='+',
        help='Specify which LOs to grade. Example: --los "LO1" "LO2" "LO3"'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Do not generate progress reports'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Generate reports but do not save them (print to console instead)'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    
    app = GradeSync(
        student_names=args.names,
        student_ids=args.ids,
        los=args.los,
        generate_reports=not args.no_report,
        save_reports=not args.no_save
    )
    app.sync()
    