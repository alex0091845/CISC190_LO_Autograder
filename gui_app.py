import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
# import os
import json
from pathlib import Path
from threading import Thread
from datetime import datetime
from repositories.student_repository import get_all_students
from sync_grades import GradeSync
from lo import LOs
from config import CURR_MODULE, COURSE_ID
from services.email_service import send_emails
from api import get_course_info

class GradesSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LO Autograder - Grade Sync")
        self.root.geometry("1200x700")
        
        # Data storage
        self.courses = []
        self.current_course = None
        self.students = []
        self.student_checkboxes = {}
        self.lo_checkboxes = {}
        self.selected_student = None
        
        # Create main layout
        self.create_widgets()
        self.load_courses()
        
    def create_widgets(self):
        # Top bar - Course selector
        top_frame = tk.Frame(self.root, bg="#f0f0f0", height=60)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, text="Select Course:", font=("Arial", 12), bg="#f0f0f0").pack(side=tk.LEFT, padx=(20, 10))
        
        self.course_var = tk.StringVar()
        self.course_dropdown = ttk.Combobox(
            top_frame, 
            textvariable=self.course_var,
            state="readonly",
            width=50,
            font=("Arial", 10)
        )
        self.course_dropdown.pack(side=tk.LEFT, padx=10)
        self.course_dropdown.bind("<<ComboboxSelected>>", self.on_course_selected)
        
        # Main content area with three panels
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Left panel - Students list with checkboxes
        left_frame = tk.LabelFrame(main_frame, text="Students", font=("Arial", 11, "bold"), padx=5, pady=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        left_frame.config(width=250)
        
        # Search bar for students + refresh
        search_frame = tk.Frame(left_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.student_search_var = tk.StringVar()
        self.student_search_var.trace('w', self.filter_students)
        search_entry = tk.Entry(search_frame, textvariable=self.student_search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        tk.Button(search_frame, text="Refresh", command=self.refresh_students, font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        
        # Select all/none buttons
        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0, 5))
        tk.Button(btn_frame, text="Select All", command=self.select_all_students, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Select None", command=self.select_no_students, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        
        # Scrollable student list
        student_canvas = tk.Canvas(left_frame, width=230)
        student_scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=student_canvas.yview)
        self.student_list_frame = tk.Frame(student_canvas)
        
        self.student_list_frame.bind(
            "<Configure>",
            lambda e: student_canvas.configure(scrollregion=student_canvas.bbox("all"))
        )
        
        student_canvas.create_window((0, 0), window=self.student_list_frame, anchor="nw")
        student_canvas.configure(yscrollcommand=student_scrollbar.set)
        
        student_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        student_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Middle panel - Latest report
        middle_frame = tk.LabelFrame(main_frame, text="Latest Report", font=("Arial", 11, "bold"), padx=5, pady=5)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Report control buttons
        report_top_frame = tk.Frame(middle_frame)
        report_top_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        tk.Button(report_top_frame, text="Save", command=self.save_report, font=("Arial", 8), bg="#4CAF50", fg="white").pack(side=tk.RIGHT, padx=2)
        tk.Button(report_top_frame, text="Refresh", command=self.refresh_report, font=("Arial", 8)).pack(side=tk.RIGHT, padx=2)

        self.report_text = scrolledtext.ScrolledText(
            middle_frame,
            wrap=tk.WORD,
            font=("Courier New", 9)
        )
        self.report_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - LOs to sync
        right_frame = tk.LabelFrame(main_frame, text="Learning Outcomes", font=("Arial", 11, "bold"), padx=5, pady=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(5, 0))
        right_frame.config(width=200)
        
        # Select all/none buttons for LOs
        lo_btn_frame = tk.Frame(right_frame)
        lo_btn_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0, 5))
        tk.Button(lo_btn_frame, text="Select All", command=self.select_all_los, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(lo_btn_frame, text="Select None", command=self.select_no_los, font=("Arial", 8)).pack(side=tk.LEFT, padx=2)
        tk.Button(lo_btn_frame, text="Refresh", command=self.refresh_los, font=("Arial", 8)).pack(side=tk.RIGHT, padx=2)
        
        # Scrollable LO list
        lo_canvas = tk.Canvas(right_frame, width=180)
        lo_scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=lo_canvas.yview)
        self.lo_list_frame = tk.Frame(lo_canvas)
        
        self.lo_list_frame.bind(
            "<Configure>",
            lambda e: lo_canvas.configure(scrollregion=lo_canvas.bbox("all"))
        )
        
        lo_canvas.create_window((0, 0), window=self.lo_list_frame, anchor="nw")
        lo_canvas.configure(yscrollcommand=lo_scrollbar.set)
        
        lo_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lo_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom bar - Status and Sync button
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0", height=50)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        bottom_frame.pack_propagate(False)
        
        # Status label (left)
        self.status_label = tk.Label(
            bottom_frame,
            text="Ready",
            font=("Arial", 10),
            bg="#f0f0f0",
            anchor="w"
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Send Email button
        self.email_button = tk.Button(
            bottom_frame,
            text="Send Emails",
            font=("Arial", 10, "bold"),
            bg="#FF9800",
            fg="white",
            command=self.send_emails_to_selected,
            width=12,
            height=1
        )
        self.email_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Global Refresh button (right of status, left of Sync)
        self.refresh_all_button = tk.Button(
            bottom_frame,
            text="Refresh All",
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            command=self.refresh_all,
            width=12,
            height=1
        )
        self.refresh_all_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Sync button (far right)
        self.sync_button = tk.Button(
            bottom_frame,
            text="Sync Grades",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self.start_sync,
            width=15,
            height=1
        )
        self.sync_button.pack(side=tk.RIGHT, padx=20, pady=5)

    def refresh_students(self):
        """Refresh the students list from students.json for the selected course."""
        self.update_status("Refreshing students...")
        self.load_students(network_load=True)
        self.update_status("Students refreshed")

    def refresh_report(self):
        """Refresh the report view for the currently selected student."""
        if self.selected_student:
            self.update_status(f"Refreshing report for {self.selected_student['name']}...")
            self.show_student_report(self.selected_student)
            self.update_status("Report refreshed")
        else:
            self.update_status("No student selected to refresh report")

    def refresh_los(self):
        """Refresh the list of LOs."""
        self.update_status("Refreshing learning outcomes...")
        self.load_los()
        self.update_status("Learning outcomes refreshed")

    def refresh_all(self):
        """Refresh courses list, students, LOs, and current report."""
        self.update_status("Refreshing all data...")
        # Reload courses list values (in case new courses were added)
        self.load_courses()
        # Reload students and LOs for current course
        if self.current_course:
            self.refresh_students()            # self.load_students()
            self.refresh_los()                 # self.load_los()
        # Refresh current report
        if self.selected_student:
            self.show_student_report(self.selected_student)
        self.update_status("All data refreshed")
        
    def load_courses(self):
        """Load available courses from the courses directory."""
        courses_dir = Path("courses")
        if not courses_dir.exists():
            os.makedirs(courses_dir)
            self.update_status("No courses directory found; created new directory.")
        
        self.courses = []
        for course_dir in courses_dir.iterdir():
            if course_dir.is_dir():
                self.courses.append({
                    'path': course_dir,
                    'name': course_dir.name
                })
        
        # if courses list is empty, load the course with COURSE_ID by sending
        # a GET request to Canvas API, retrieving the name of the course,
        # then creating a course folder inside the courses directory.
        if not self.courses:
            course_info = get_course_info(COURSE_ID)
            if course_info:
                course_name = course_info.get('name', f"Course_{COURSE_ID}")

                # Sanitize course name for use in directory name (remove special characters)
                safe_course_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in course_name)
                safe_course_name = safe_course_name.strip().replace(' ', '_')
                
                # Create directory path: courses/<COURSE_ID - COURSE_NAME>
                dir_name = f"{COURSE_ID} - {safe_course_name}"
                dir_path = Path("courses") / dir_name
                dir_path.mkdir(parents=True, exist_ok=True)

                self.courses.append({
                    'path': dir_path,
                    'name': dir_name
                })
                self.update_status(f"Added course: {course_name}")

        
        if self.courses:
            course_names = [course['name'] for course in self.courses]
            self.course_dropdown['values'] = course_names
            self.course_dropdown.current(0)
            self.on_course_selected(None)
        else:

            self.update_status("No saved courses found")
    
    def on_course_selected(self, event):
        """Handle course selection."""
        selected_name = self.course_var.get()
        if not selected_name:
            return
        
        # Find the course
        for course in self.courses:
            if course['name'] == selected_name:
                self.current_course = course
                self.load_students()
                self.load_los()
                self.update_status(f"Loaded course: {selected_name}")
                break
    
    def load_students(self, network_load=False):
        """Load students from the selected course."""
        if not self.current_course:
            return
        
        students_file = self.current_course['path'] / "students.json"
        try:
            if network_load:
                # If network load is requested, re-fetch students from Canvas API
                get_all_students(COURSE_ID)
            
            with open(students_file, 'r', encoding='utf-8') as f:
                self.students = json.load(f)
            
            self.populate_student_list()
        except Exception as e:
            self.update_status(f"Error loading students: {str(e)}")
    
    def populate_student_list(self):
        """Populate the student list with checkboxes."""
        # Clear existing
        for widget in self.student_list_frame.winfo_children():
            widget.destroy()
        
        self.student_checkboxes.clear()
        
        search_term = self.student_search_var.get().lower()
        
        for student in self.students:
            student_name = student['name']
            
            # Apply search filter
            if search_term and search_term not in student_name.lower():
                continue
            
            frame = tk.Frame(self.student_list_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            var = tk.BooleanVar(value=True)
            self.student_checkboxes[student['id']] = var
            
            checkbox = tk.Checkbutton(frame, variable=var)
            checkbox.pack(side=tk.LEFT)
            
            label = tk.Label(
                frame,
                text=student_name,
                anchor="w",
                cursor="hand2",
                font=("Arial", 9)
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Click to view report
            label.bind("<Button-1>", lambda e, s=student: self.show_student_report(s))
    
    def filter_students(self, *args):
        """Filter students based on search term."""
        self.populate_student_list()
    
    def load_los(self):
        """Load learning outcomes."""
        # Clear existing
        for widget in self.lo_list_frame.winfo_children():
            widget.destroy()
        
        self.lo_checkboxes.clear()
        
        # Get LO names from LOs class
        lo_names = LOs.LO_NAMES[0:LOs.MODULE_NUM_TO_LO_NUM[CURR_MODULE]]
        
        for lo_name in lo_names:
            frame = tk.Frame(self.lo_list_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            var = tk.BooleanVar(value=True)
            self.lo_checkboxes[lo_name] = var
            
            checkbox = tk.Checkbutton(
                frame,
                text=lo_name,
                variable=var,
                font=("Arial", 9)
            )
            checkbox.pack(anchor=tk.W)
    
    def show_student_report(self, student):
        """Display the latest report for the selected student."""
        self.selected_student = student
        
        # Find the student's reports directory
        reports_dir = Path("reports")
        
        # Create sanitized name for directory lookup
        student_name_parts = student['name'].split()
        if len(student_name_parts) >= 2:
            sanitized_name = f"{student_name_parts[0]}_{student_name_parts[-1]}"
            student_dir = reports_dir / sanitized_name
            
            if student_dir.exists():
                # Find the latest report
                report_files = sorted(student_dir.glob("progress_report_*.txt"), reverse=True)
                if report_files:
                    latest_report = report_files[0]
                    try:
                        with open(latest_report, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        self.report_text.delete(1.0, tk.END)
                        self.report_text.insert(1.0, report_content)
                        return
                    except Exception as e:
                        self.update_status(f"Error reading report: {str(e)}")
        
        # No report found
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, f"No report found for {student['name']}")
    
    def select_all_students(self):
        """Select all student checkboxes."""
        for var in self.student_checkboxes.values():
            var.set(True)
    
    def select_no_students(self):
        """Deselect all student checkboxes."""
        for var in self.student_checkboxes.values():
            var.set(False)
    
    def select_all_los(self):
        """Select all LO checkboxes."""
        for var in self.lo_checkboxes.values():
            var.set(True)
    
    def select_no_los(self):
        """Deselect all LO checkboxes."""
        for var in self.lo_checkboxes.values():
            var.set(False)
    
    def start_sync(self):
        """Start the grade sync process in a background thread."""
        # Get selected students
        selected_student_ids = [
            str(student_id) for student_id, var in self.student_checkboxes.items()
            if var.get()
        ]
        
        if not selected_student_ids:
            self.update_status("No students selected")
            return
        
        # Get selected LOs
        selected_los = [
            lo_name for lo_name, var in self.lo_checkboxes.items()
            if var.get()
        ]
        
        if not selected_los:
            self.update_status("No LOs selected")
            return
        
        # Disable sync button
        self.sync_button.config(state=tk.DISABLED)
        self.update_status("Syncing grades...")
        
        # Run sync in background thread
        thread = Thread(target=self.run_sync, args=(selected_student_ids, selected_los))
        thread.daemon = True
        thread.start()
    
    def run_sync(self, student_ids, los):
        """Run the grade sync process."""
        try:
            app = GradeSync(
                student_ids=student_ids,
                los=los,
                generate_reports=True,
                save_reports=True
            )
            app.sync()
            
            # Update UI on completion
            self.root.after(0, self.sync_complete, True)
        except Exception as e:
            self.root.after(0, self.sync_complete, False, str(e))
    
    def sync_complete(self, success, error_msg=None):
        """Handle sync completion."""
        self.sync_button.config(state=tk.NORMAL)
        
        if success:
            self.update_status("Sync completed successfully!")
            # Refresh the report for selected student if any
            if self.selected_student:
                self.show_student_report(self.selected_student)
        else:
            self.update_status(f"Sync failed: {error_msg}")
    
    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)
    
    def save_report(self):
        """Save the edited report for the currently selected student."""
        if not self.selected_student:
            messagebox.showwarning("No Student Selected", "Please select a student first.")
            return
        
        student_name = self.selected_student['name']
        
        # Get the edited report content
        report_content = self.report_text.get(1.0, tk.END).strip()
        
        if not report_content:
            messagebox.showwarning("Empty Report", "Cannot save an empty report.")
            return
        
        # Create sanitized name for directory
        student_name_parts = student_name.split()
        if len(student_name_parts) >= 2:
            sanitized_name = f"{student_name_parts[0]}_{student_name_parts[-1]}"
            reports_dir = Path("reports") / sanitized_name
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d")
            filename = f"progress_report_{sanitized_name.lower()}_{timestamp}.txt"
            filepath = reports_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                self.update_status(f"Report saved for {student_name}")
                # messagebox.showinfo("Success", f"Report saved successfully to {filepath}")
            except Exception as e:
                self.update_status(f"Error saving report: {str(e)}")
                messagebox.showerror("Error", f"Failed to save report: {str(e)}")
        else:
            messagebox.showerror("Error", "Invalid student name format.")
    
    def send_emails_to_selected(self):
        """Send emails to all selected students in a background thread."""
        # Get selected students
        selected_student_ids = [
            str(student_id) for student_id, var in self.student_checkboxes.items()
            if var.get()
        ]
        
        if not selected_student_ids:
            messagebox.showwarning("No Students Selected", "Please select at least one student to send emails.")
            return
        
        # Confirm action
        result = messagebox.askyesno(
            "Confirm Send",
            f"Send progress reports to {len(selected_student_ids)} selected student(s)?\n\nThis will send via Canvas Inbox."
        )
        
        if not result:
            return
        
        # Disable email button
        self.email_button.config(state=tk.DISABLED)
        self.update_status(f"Sending emails to {len(selected_student_ids)} students...")
        
        # Run email sending in background thread
        thread = Thread(target=self.run_send_emails, args=(selected_student_ids,))
        thread.daemon = True
        thread.start()
    
    def run_send_emails(self, student_ids):
        """Run the email sending process in background."""
        try:
            sent_count, failed_count = send_emails(student_ids=student_ids)
            
            # Update UI on completion
            self.root.after(0, self.email_complete, True, sent_count, failed_count)
        except Exception as e:
            self.root.after(0, self.email_complete, False, 0, 0, str(e))
    
    def email_complete(self, success, sent_count=0, failed_count=0, error_msg=None):
        """Handle email sending completion."""
        self.email_button.config(state=tk.NORMAL)
        
        if success:
            message = f"Emails sent successfully!\n\nSent: {sent_count}\nFailed: {failed_count}"
            self.update_status(f"Email complete: {sent_count} sent, {failed_count} failed")
            messagebox.showinfo("Email Complete", message)
        else:
            self.update_status(f"Email failed: {error_msg}")
            messagebox.showerror("Email Failed", f"Error sending emails: {error_msg}")


def main():
    root = tk.Tk()
    app = GradesSyncApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
