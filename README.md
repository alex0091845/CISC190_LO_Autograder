# CISC 190 LO Autograder for Mesa College

I'll have a link to the repository for the CISC 191 version once I have a working program.

I put together this program hastily to help:
- Automatically grade and mark Learning Outcomes (LOs) rubric criteria so you don't have to
    - You still have to manually grade their assignments, of course
- Generate and send personalized email reports to students about their LO performance

The first commit is a barebones version that worked for me, but I'm planning to re-architect it
and then improve it over time.

## Quick(? Setup
1. Clone this repository to your local machine.
2. Create a `config.py` file in the root directory based on the provided `config_template.py`.
   Fill in your Canvas API token, course ID, and other necessary configurations.
3. Install the required dependencies using pip:
   ```bash
   pip install -r requirements.txt
   ```
   or
   ```bash
   pip3 install -r requirements.txt
   ```
   or whatever version you're working with (for me, that's Python 3.11).
4. Once configured, run the application using:
   ```bash
   python gui_app.py
   ```
   or
    ```bash
    python3 gui_app.py
    ```
    or whatever version you're working with.
5. Press "Refresh All" on the bottom right to load and cache students from the specified course.
6. Go to `lo.py` and customize the LOs, the assignment names, and LO assignment IDs. Notably:
    - Update each LOx variable with the correct names
    - Update the MODULE_NUM_TO_LO_NUM and LO_TO_MODULE_NUM dictionaries
    - Update the LOs.reqs dictionary. This is where you define the requirements to satisfy each LO
    - Update each LO's IDs in LOs.lo_name_to_id
7. Go to `levels.py` and change the INTERN, JUNIOR, etc., levels to the correct
names. The program will search for assignments that have these strings in them.
8. To generate the reports, you'll want to look at `report_on_track_template.py` and choose the one you want to use. Then, replace the `_template` variable in `student_report.py` with your chosen template string.