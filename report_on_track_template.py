# This is the template for reports sent to students during the course progression.
_in_progress_template = f"""Hi {first_name},

This is a progress message to let you know you're on track to {a_or_an} {grade_on_track}. {progress_statement}

We're on module {CURR_MODULE}.

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

# This is the template for final reports sent to students at the end of the course.
# This is currently used in `student_report.py`.
_final_template = f"""Hi {first_name},

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