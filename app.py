import streamlit as st
import pandas as pd
import datetime
import time
from sqlalchemy import create_engine, text
import io
import base64
from PIL import Image
import requests
from streamlit_option_menu import option_menu
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Page config
st.set_page_config(
    page_title="Enhanced Employee Management System",
    page_icon="👥",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .stat-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E88E5;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #777;
    }
    
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2.5rem;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
        font-weight: 600;
        height: 2.5rem;
        border-radius: 5px;
    }
    
    .stTextInput > div > div > input {
        height: 2.5rem;
    }
    
    .report-item {
        background-color: #f1f7fe;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    
    .task-item {
        background-color: #f1fff1;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #4CAF50;
    }
    
    .task-item.completed {
        background-color: #f0f0f0;
        border-left: 4px solid #9e9e9e;
    }
    
    .message-item {
        background-color: #fff8e1;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #FF9800;
    }
    
    .profile-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .profile-image {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #1E88E5;
    }
    
    .company-card {
        background-color: #e3f2fd;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .branch-card {
        background-color: #e8f5e9;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .role-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .role-manager {
        background-color: #e3f2fd;
        color: #1565c0;
    }
    
    .role-asst-manager {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    
    .role-employee {
        background-color: #f3e5f5;
        color: #6a1b9a;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    
    .status-active {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    
    .status-inactive {
        background-color: #ffebee;
        color: #c62828;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def init_connection():
    try:
        return create_engine(st.secrets["postgres"]["url"])
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return #------------------------- EMPLOYEE DASHBOARD -------------------------#

def employee_dashboard():
    st.markdown('<h1 class="main-header">Employee Dashboard</h1>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    employee_role = st.session_state.user["role"]
    employee_name = st.session_state.user["full_name"]
    branch_id = st.session_state.user["branch_id"]
    branch_name = st.session_state.user["branch_name"]
    company_name = st.session_state.user["company_name"]
    
    # Employee profile display
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="profile-container">', unsafe_allow_html=True)
        try:
            st.image(st.session_state.user["profile_pic_url"], width=80, clamp=True, output_format="auto", channels="RGB", use_container_width=False)
        except:
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=80, use_container_width=False)
        
        role_class = ""
        if employee_role == "Manager":
            role_class = "role-manager"
        elif employee_role == "Asst. Manager":
            role_class = "role-asst-manager"
        else:
            role_class = "role-employee"
        
        st.markdown(f'''
        <div>
            <h3>{employee_name}</h3>
            <p>{branch_name} - <span class="role-badge {role_class}">{employee_role}</span></p>
            <p>{company_name}</p>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dynamic navigation options based on role
    options = ["Dashboard", "My Tasks", "Submit Report", "My Reports", "My Profile", "Logout"]
    icons = ["house", "list-check", "pencil", "journal-text", "person-circle", "box-arrow-right"]
    
    # Add management options based on role
    if employee_role == "Manager" or employee_role == "Asst. Manager":
        options.insert(4, "Manage Employees")
        icons.insert(4, "people")
        options.insert(4, "Manage Tasks")
        icons.insert(4, "list-task")
        
        if employee_role == "Manager":
            options.insert(4, "View Reports")
            icons.insert(4, "clipboard-data")
    
    # Navigation
    selected = option_menu(
        menu_title=today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        result = conn.execute(text('''
        SELECT COUNT(*) FROM daily_reports 
        WHERE employee_id = :employee_id AND report_date >= :first_day
        '''), {'employee_id': employee_id, 'first_day': first_day_of_month})
        reports_this_month = result.fetchone()[0]
        
        # Total tasks assigned to employee
        result = conn.execute(text('''
        SELECT COUNT(*) FROM tasks
        WHERE assigned_to_type = 'employee' AND assigned_to_id = :employee_id
        '''), {'employee_id': employee_id})
        total_tasks = result.fetchone()[0]
        
        # Pending tasks
        result = conn.execute(text('''
        SELECT COUNT(*) FROM tasks
        WHERE assigned_to_type = 'employee' AND assigned_to_id = :employee_id AND is_completed = FALSE
        '''), {'employee_id': employee_id})
        pending_tasks = result.fetchone()[0]
        
        # Branch tasks (tasks assigned to the branch)
        result = conn.execute(text('''
        SELECT COUNT(*) FROM tasks
        WHERE assigned_to_type = 'branch' AND assigned_to_id = :branch_id AND is_completed = FALSE
        '''), {'branch_id': branch_id})
        branch_pending_tasks = result.fetchone()[0]
        
        # Recent reports
        result = conn.execute(text('''
        SELECT report_date, report_text FROM daily_reports 
        WHERE employee_id = :employee_id 
        ORDER BY report_date DESC LIMIT 3
        '''), {'employee_id': employee_id})
        recent_reports = result.fetchall()
        
        # Pending employee tasks
        result = conn.execute(text('''
        SELECT id, task_description, due_date FROM tasks 
        WHERE assigned_to_type = 'employee' AND assigned_to_id = :employee_id AND is_completed = FALSE 
        ORDER BY due_date ASC NULLS LAST LIMIT 3
        '''), {'employee_id': employee_id})
        pending_employee_tasks = result.fetchall()
        
        # Pending branch tasks
        result = conn.execute(text('''
        SELECT t.id, t.task_description, t.due_date,
               (SELECT COUNT(*) FROM task_completions tc WHERE tc.task_id = t.id AND tc.employee_id = :employee_id) > 0 
               as is_completed_by_me
        FROM tasks t
        WHERE t.assigned_to_type = 'branch' AND t.assigned_to_id = :branch_id AND t.is_completed = FALSE
        ORDER BY t.due_date ASC NULLS LAST LIMIT 3
        '''), {'employee_id': employee_id, 'branch_id': branch_id})
        pending_branch_tasks = result.fetchall()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_reports}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Reports</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{reports_this_month}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Reports This Month</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{pending_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">My Pending Tasks</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{branch_pending_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Branch Pending Tasks</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activity and pending tasks
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">My Recent Reports</h3>', unsafe_allow_html=True)
        if recent_reports:
            for report in recent_reports:
                st.markdown(f'''
                <div class="report-item">
                    <strong>{report[0].strftime('%d %b, %Y')}</strong>
                    <p>{report[1][:100]}{'...' if len(report[1]) > 100 else ''}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No reports submitted yet")
        
        if st.button("Submit New Report", key="quick_submit"):
            st.session_state["selected_tab"] = "Submit Report"
            st.rerun()
    
    with col2:
        st.markdown('<h3 class="sub-header">My Pending Tasks</h3>', unsafe_allow_html=True)
        
        # My individual tasks
        if pending_employee_tasks:
            for task in pending_employee_tasks:
                task_id = task[0]
                task_description = task[1]
                due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                
                st.markdown(f'''
                <div class="task-item">
                    <p><strong>Due: {due_date}</strong> (My Task)</p>
                    <p>{task_description[:100]}{'...' if len(task_description) > 100 else ''}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"Mark as Completed", key=f"quick_complete_{task_id}"):
                    with engine.connect() as conn:
                        conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task_id})
                        conn.commit()
                    st.success("Task marked as completed")
                    st.rerun()
        
        # Branch tasks
        if pending_branch_tasks:
            for task in pending_branch_tasks:
                task_id = task[0]
                task_description = task[1]
                due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                is_completed_by_me = task[3]
                
                st.markdown(f'''
                <div class="task-item" style="background-color: {'#f0f0f0' if is_completed_by_me else '#f1fff1'};">
                    <p><strong>Due: {due_date}</strong> (Branch Task) {' - Completed by you' if is_completed_by_me else ''}</p>
                    <p>{task_description[:100]}{'...' if len(task_description) > 100 else ''}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                if not is_completed_by_me:
                    if st.button(f"Mark as Completed by Me", key=f"quick_complete_branch_{task_id}"):
                        with engine.connect() as conn:
                            # Add to task completions
                            conn.execute(text('''
                            INSERT INTO task_completions (task_id, employee_id)
                            VALUES (:task_id, :employee_id)
                            '''), {'task_id': task_id, 'employee_id': employee_id})
                            
                            # Check if all employees in the branch have completed the task
                            result = conn.execute(text('''
                            SELECT 
                                (SELECT COUNT(*) FROM employees WHERE branch_id = :branch_id AND is_active = TRUE) as total_employees,
                                (SELECT COUNT(*) FROM task_completions tc 
                                 JOIN employees e ON tc.employee_id = e.id 
                                 WHERE tc.task_id = :task_id AND e.branch_id = :branch_id) as completed_count
                            '''), {'task_id': task_id, 'branch_id': branch_id})
                            counts = result.fetchone()
                            
                            # If manager or all employees completed the task, mark it as completed
                            if employee_role == "Manager" or counts[0] == counts[1]:
                                conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task_id})
                            
                            conn.commit()
                        st.success("Task marked as completed by you")
                        st.rerun()
        
        if not pending_employee_tasks and not pending_branch_tasks:
            st.info("No pending tasks")

# View Employee Tasks
def view_employee_tasks():
    st.markdown('<h2 class="sub-header">My Tasks</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    employee_role = st.session_state.user["role"]
    branch_id = st.session_state.user["branch_id"]
    
    tab1, tab2 = st.tabs(["My Individual Tasks", "Branch Tasks"])
    
    with tab1:
        # Status filter
        status_options = ["All Tasks", "Pending", "Completed"]
        status_filter = st.selectbox("Show", status_options, key="employee_task_status_filter")
        
        # Build query
        query = '''
        SELECT id, task_description, due_date, is_completed, created_at,
               (SELECT e.full_name FROM employees e WHERE e.id = assigned_by_id) as assigned_by_name
        FROM tasks
        WHERE assigned_to_type = 'employee' AND assigned_to_id = :employee_id
        '''
        
        params = {'employee_id': employee_id}
        
        if status_filter == "Pending":
            query += ' AND is_completed = FALSE'
        elif status_filter == "Completed":
            query += ' AND is_completed = TRUE'
        
        query += ' ORDER BY due_date ASC NULLS LAST, created_at DESC'
        
        # Execute query
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            tasks = result.fetchall()
        
        # Display tasks
        if not tasks:
            st.info("No tasks found")
        else:
            st.write(f"Found {len(tasks)} tasks")
            
            for task in tasks:
                task_id = task[0]
                task_description = task[1]
                due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                is_completed = task[3]
                created_at = task[4]
                assigned_by = task[5]
                
                status_class = "completed" if is_completed else ""
                
                st.markdown(f'''
                <div class="task-item {status_class}">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>Due: {due_date}</strong>
                        <span style="font-weight: 600; color: {'#9e9e9e' if is_completed else '#4CAF50'};">
                            {"Completed" if is_completed else "Pending"}
                        </span>
                    </div>
                    <p>{task_description}</p>
                    <div style="display: flex; justify-content: space-between; color: #777; font-size: 0.8rem;">
                        <span>Assigned by: {assigned_by}</span>
                        <span>Created: {created_at.strftime('%d %b, %Y')}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                if not is_completed:
                    if st.button(f"Mark as Completed", key=f"complete_task_{task_id}"):
                        with engine.connect() as conn:
                            conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task_id})
                            conn.commit()
                        st.success("Task marked as completed")
                        st.rerun()
    
    with tab2:
        # Status filter for branch tasks
        branch_status_options = ["All Tasks", "Pending", "Completed by Me", "Not Completed by Me", "Completed by Branch"]
        branch_status_filter = st.selectbox("Show", branch_status_options, key="branch_task_status_filter")
        
        # Build query
        query = '''
        SELECT t.id, t.task_description, t.due_date, t.is_completed, t.created_at,
               (SELECT COUNT(*) FROM task_completions tc WHERE tc.task_id = t.id AND tc.employee_id = :employee_id) > 0 
               as is_completed_by_me,
               (SELECT COUNT(*) FROM employees WHERE branch_id = :branch_id AND is_active = TRUE) as total_employees,
               (SELECT COUNT(*) FROM task_completions tc 
                JOIN employees e ON tc.employee_id = e.id 
                WHERE tc.task_id = t.id AND e.branch_id = :branch_id) as completion_count
        FROM tasks t
        WHERE t.assigned_to_type = 'branch' AND t.assigned_to_id = :branch_id
        '''
        
        params = {'employee_id': employee_id, 'branch_id': branch_id}
        
        if branch_status_filter == "Pending":
            query += ' AND t.is_completed = FALSE'
        elif branch_status_filter == "Completed by Me":
            query += ' AND (SELECT COUNT(*) FROM task_completions tc WHERE tc.task_id = t.id AND tc.employee_id = :employee_id) > 0'
        elif branch_status_filter == "Not Completed by Me":
            query += ' AND (SELECT COUNT(*) FROM task_completions tc WHERE tc.task_id = t.id AND tc.employee_id = :employee_id) = 0'
        elif branch_status_filter == "Completed by Branch":
            query += ' AND t.is_completed = TRUE'
        
        query += ' ORDER BY t.due_date ASC NULLS LAST, t.created_at DESC'
        
        # Execute query
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            branch_tasks = result.fetchall()
        
        # Display branch tasks
        if not branch_tasks:
            st.info("No branch tasks found")
        else:
            st.write(f"Found {len(branch_tasks)} branch tasks")
            
            for task in branch_tasks:
                task_id = task[0]
                task_description = task[1]
                due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                is_completed = task[3]
                created_at = task[4]
                is_completed_by_me = task[5]
                total_employees = task[6]
                completion_count = task[7]
                
                # Status style
                status_class = "completed" if is_completed else ""
                
                # Progress percentage
                progress_percentage = int((completion_count / total_employees) * 100) if total_employees > 0 else 0
                
                st.markdown(f'''
                <div class="task-item {status_class}">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>Due: {due_date}</strong>
                        <span style="font-weight: 600; color: {'#9e9e9e' if is_completed else '#4CAF50'};">
                            {"Completed" if is_completed else "Pending"}
                        </span>
                    </div>
                    <p>{task_description}</p>
                    <div style="margin: 10px 0;">
                        <div style="background-color: #e0e0e0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="background-color: #4CAF50; height: 100%; width: {progress_percentage}%;"></div>
                        </div>
                        <div style="text-align: center; font-size: 0.8rem; margin-top: 5px;">
                            {completion_count}/{total_employees} completed
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; color: #777; font-size: 0.8rem;">
                        <span>{created_at.strftime('%d %b, %Y')}</span>
                        <span>{'' if is_completed_by_me else 'Not completed by you'}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Action buttons
                if not is_completed and not is_completed_by_me:
                    if st.button(f"Mark as Completed by Me", key=f"complete_branch_task_{task_id}"):
                        with engine.connect() as conn:
                            # Add to task completions
                            conn.execute(text('''
                            INSERT INTO task_completions (task_id, employee_id)
                            VALUES (:task_id, :employee_id)
                            '''), {'task_id': task_id, 'employee_id': employee_id})
                            
                            # Check if all employees in the branch have completed the task or if manager is marking it
                            if employee_role == "Manager":
                                conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task_id})
                            else:
                                # Check if all employees completed it
                                result = conn.execute(text('''
                                SELECT 
                                    (SELECT COUNT(*) FROM employees WHERE branch_id = :branch_id AND is_active = TRUE) as total_employees,
                                    (SELECT COUNT(*) FROM task_completions tc 
                                     JOIN employees e ON tc.employee_id = e.id 
                                     WHERE tc.task_id = :task_id AND e.branch_id = :branch_id) + 1 as completed_count
                                '''), {'task_id': task_id, 'branch_id': branch_id})
                                counts = result.fetchone()
                                
                                if counts[0] == counts[1]:
                                    conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task_id})
                            
                            conn.commit()
                        st.success("Task marked as completed by you")
                        st.rerun()
                elif not is_completed and is_completed_by_me:
                    st.info("You have already completed this task. Waiting for others to complete it.")

# Submit Employee Report
def submit_employee_report():
    st.markdown('<h2 class="sub-header">Submit Daily Report</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    
    with st.form("submit_report_form"):
        report_date = st.date_input("Report Date", datetime.date.today())
        
        # Check if a report already exists for this date
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id FROM daily_reports 
            WHERE employee_id = :employee_id AND report_date = :report_date
            '''), {'employee_id': employee_id, 'report_date': report_date})
            existing_report = result.fetchone()
        
        if existing_report:
            st.warning(f"You already have a report for {report_date.strftime('%d %b, %Y')}. Submitting will update your existing report.")
        
        report_text = st.text_area("What did you work on today?", height=200)
        
        submitted = st.form_submit_button("Submit Report")
        if submitted:
            if not report_text:
                st.error("Please enter your report")
            else:
                try:
                    with engine.connect() as conn:
                        if existing_report:
                            # Update existing report
                            conn.execute(text('''
                            UPDATE daily_reports 
                            SET report_text = :report_text, created_at = CURRENT_TIMESTAMP
                            WHERE id = :id
                            '''), {'report_text': report_text, 'id': existing_report[0]})
                            success_message = "Report updated successfully"
                        else:
                            # Insert new report
                            conn.execute(text('''
                            INSERT INTO daily_reports (employee_id, report_date, report_text)
                            VALUES (:employee_id, :report_date, :report_text)
                            '''), {
                                'employee_id': employee_id,
                                'report_date': report_date,
                                'report_text': report_text
                            })
                            success_message = "Report submitted successfully"
                        
                        conn.commit()
                    st.success(success_message)
                except Exception as e:
                    st.error(f"Error submitting report: {e}")

# View Employee Reports
def view_employee_reports():
    st.markdown('<h2 class="sub-header">My Reports</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    
    # Date range filter
    col1, col2 = st.columns(2)
    
    with col1:
        today = datetime.date.today()
        date_options = [
            "All Reports",
            "This Week",
            "This Month",
            "This Year",
            "Custom Range"
        ]
        date_filter = st.selectbox("Date Range", date_options, key="employee_reports_date_filter")
    
    with col2:
        # Custom date range if selected
        if date_filter == "Custom Range":
            start_date = st.date_input("Start Date", today - datetime.timedelta(days=30))
            end_date = st.date_input("End Date", today)
        else:
            # Set default dates based on filter
            if date_filter == "This Week":
                start_date = today - datetime.timedelta(days=today.weekday())
                end_date = today
            elif date_filter == "This Month":
                start_date = today.replace(day=1)
                end_date = today
            elif date_filter == "This Year":
                start_date = today.replace(month=1, day=1)
                end_date = today
            else:  # All Reports
                start_date = datetime.date(2000, 1, 1)
                end_date = today
    
    # Fetch reports
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT id, report_date, report_text
        FROM daily_reports
        WHERE employee_id = :employee_id
        AND report_date BETWEEN :start_date AND :end_date
        ORDER BY report_date DESC
        '''), {'employee_id': employee_id, 'start_date': start_date, 'end_date': end_date})
        reports = result.fetchall()
    
    # Export options
    if reports:
        if st.button("Export as PDF"):
            pdf = create_employee_report_pdf(reports, st.session_state.user["full_name"])
            st.download_button(
                label="Download PDF",
                data=pdf,
                file_name=f"my_reports_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    
    # Display reports
    if not reports:
        st.info("No reports found for the selected period")
    else:
        st.write(f"Found {len(reports)} reports")
        
        # Group by month/year for better organization
        reports_by_period = {}
        for report in reports:
            period = report[1].strftime('%B %Y')
            if period not in reports_by_period:
                reports_by_period[period] = []
            reports_by_period[period].append(report)
        
        for period, period_reports in reports_by_period.items():
            with st.expander(f"{period} ({len(period_reports)} reports)", expanded=True):
                for report in period_reports:
                    report_id = report[0]
                    report_date = report[1]
                    report_text = report[2]
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f'''
                        <div class="report-item">
                            <strong>{report_date.strftime('%A, %d %b %Y')}</strong>
                            <p>{report_text}</p>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("Edit", key=f"edit_report_{report_id}"):
                            st.session_state.edit_report = {
                                'id': report_id,
                                'date': report_date,
                                'text': report_text
                            }
                            st.rerun()
        
    # Edit report if selected
    if hasattr(st.session_state, 'edit_report'):
        st.markdown('<h3 class="sub-header">Edit Report</h3>', unsafe_allow_html=True)
        
        with st.form("edit_report_form"):
            report_date = st.date_input("Report Date", st.session_state.edit_report['date'])
            report_text = st.text_area("Report Text", st.session_state.edit_report['text'], height=200)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Update Report")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submitted:
                if not report_text:
                    st.error("Please enter your report")
                else:
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            UPDATE daily_reports 
                            SET report_text = :report_text, report_date = :report_date, created_at = CURRENT_TIMESTAMP
                            WHERE id = :id
                            '''), {
                                'report_text': report_text, 
                                'report_date': report_date, 
                                'id': st.session_state.edit_report['id']
                            })
                            conn.commit()
                        st.success("Report updated successfully")
                        del st.session_state.edit_report
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating report: {e}")
            
            if cancel:
                del st.session_state.edit_report
                st.rerun()

# Create PDF for employee reports
def create_employee_report_pdf(reports, employee_name):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    elements.append(Paragraph(f"Work Reports: {employee_name}", title_style))
    elements.append(Spacer(1, 12))
    
    # Date range
    date_style = ParagraphStyle(
        'DateRange',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.gray
    )
    min_date = min(report[1] for report in reports).strftime('%d %b %Y')
    max_date = max(report[1] for report in reports).strftime('%d %b %Y')
    elements.append(Paragraph(f"Period: {min_date} to {max_date}", date_style))
    elements.append(Spacer(1, 20))
    
    # Group reports by month
    reports_by_month = {}
    for report in reports:
        month_year = report[1].strftime('%B %Y')
        if month_year not in reports_by_month:
            reports_by_month[month_year] = []
        reports_by_month[month_year].append(report)
    
    # Add each month's reports
    for month, month_reports in reports_by_month.items():
        # Month header
        month_style = ParagraphStyle(
            'Month',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        )
        elements.append(Paragraph(month, month_style))
        
        # Reports for the month
        for report in month_reports:
            # Date
            date_style = ParagraphStyle(
                'Date',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.blue
            )
            elements.append(Paragraph(report[1].strftime('%A, %d %b %Y'), date_style))
            
            # Report text
            text_style = ParagraphStyle(
                'ReportText',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=10
            )
            elements.append(Paragraph(report[2], text_style))
            elements.append(Spacer(1, 12))
        
        elements.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# Manage Branch Employees (for Manager and Asst. Manager)
def manage_branch_employees():
    st.markdown('<h2 class="sub-header">Manage Branch Employees</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    employee_role = st.session_state.user["role"]
    branch_id = st.session_state.user["branch_id"]
    branch_name = st.session_state.user["branch_name"]
    
    st.markdown(f'<p>Managing employees for <strong>{branch_name}</strong></p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Employee List", "Add New Employee"])
    
    with tab1:
        # Fetch and display all employees in the branch
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, full_name, username, profile_pic_url, role, is_active
            FROM employees
            WHERE branch_id = :branch_id
            ORDER BY role, full_name
            '''), {'branch_id': branch_id})
            branch_employees = result.fetchall()
        
        if not branch_employees:
            st.info("No employees found in this branch. Add employees using the 'Add New Employee' tab.")
        else:
            # Filter options
            col1, col2 = st.columns(2)
            
            with col1:
                # Role filter
                role_options,
        options=options,
        icons=icons,
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6", "border-radius": "10px", "margin-bottom": "20px"},
            "icon": {"color": "#1E88E5", "font-size": "16px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "padding": "10px", "border-radius": "5px"},
            "nav-link-selected": {"background-color": "#1E88E5", "color": "white", "font-weight": "600"},
        }
    )
    
    if selected == "Dashboard":
        display_employee_dashboard()
    elif selected == "My Tasks":
        view_employee_tasks()
    elif selected == "Submit Report":
        submit_employee_report()
    elif selected == "My Reports":
        view_employee_reports()
    elif selected == "Manage Employees" and (employee_role == "Manager" or employee_role == "Asst. Manager"):
        manage_branch_employees()
    elif selected == "Manage Tasks" and (employee_role == "Manager" or employee_role == "Asst. Manager"):
        manage_branch_tasks()
    elif selected == "View Reports" and employee_role == "Manager":
        view_branch_reports()
    elif selected == "My Profile":
        edit_employee_profile()
    elif selected == "Logout":
        logout()

# Employee Dashboard Overview
def display_employee_dashboard():
    st.markdown('<h2 class="sub-header">My Overview</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    employee_role = st.session_state.user["role"]
    branch_id = st.session_state.user["branch_id"]
    
    # Statistics
    with engine.connect() as conn:
        # Total reports
        result = conn.execute(text('SELECT COUNT(*) FROM daily_reports WHERE employee_id = :employee_id'), 
                             {'employee_id': employee_id})
        total_reports = result.fetchone()[0]
        
        # Reports this month
        today = datetime.date.today()
        first_day_of_month = today.replace(day=

# Initialize DB tables if they don't exist
def init_db():
    with engine.connect() as conn:
        conn.execute(text('''
        -- Companies table
        CREATE TABLE IF NOT EXISTS companies (
            id SERIAL PRIMARY KEY,
            company_name VARCHAR(100) NOT NULL,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            profile_pic_url TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Branches table
        CREATE TABLE IF NOT EXISTS branches (
            id SERIAL PRIMARY KEY,
            company_id INTEGER REFERENCES companies(id),
            branch_name VARCHAR(100) NOT NULL,
            is_main_branch BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Enhanced employees table
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            branch_id INTEGER REFERENCES branches(id),
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            profile_pic_url TEXT,
            role VARCHAR(50) NOT NULL CHECK (role IN ('Manager', 'Asst. Manager', 'General Employee')),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Messages table (for admin to company communication)
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender_type VARCHAR(20) NOT NULL CHECK (sender_type IN ('admin', 'company')),
            sender_id INTEGER NOT NULL,
            receiver_type VARCHAR(20) NOT NULL CHECK (receiver_type IN ('admin', 'company')),
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Updated tasks table to support branch-level tasks
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            assigned_by_type VARCHAR(20) NOT NULL CHECK (assigned_by_type IN ('admin', 'company', 'employee')),
            assigned_by_id INTEGER NOT NULL,
            assigned_to_type VARCHAR(20) NOT NULL CHECK (assigned_to_type IN ('company', 'branch', 'employee')),
            assigned_to_id INTEGER NOT NULL,
            task_description TEXT NOT NULL,
            due_date DATE,
            is_completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Task completion tracking for branch-level tasks
        CREATE TABLE IF NOT EXISTS task_completions (
            id SERIAL PRIMARY KEY,
            task_id INTEGER REFERENCES tasks(id),
            employee_id INTEGER REFERENCES employees(id),
            completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            comments TEXT
        );
        
        -- Daily reports table (enhanced)
        CREATE TABLE IF NOT EXISTS daily_reports (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER REFERENCES employees(id),
            report_date DATE NOT NULL,
            report_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''))
        conn.commit()

# Authentication function
def authenticate(username, password, user_type='any'):
    # Check if admin credentials are properly set in Streamlit secrets
    if "admin_username" not in st.secrets or "admin_password" not in st.secrets:
        st.warning("Admin credentials are not properly configured in Streamlit secrets. Please set admin_username and admin_password in .streamlit/secrets.toml")
        return role_options = ["All Roles"]
                # Add role options based on current user's role
                if employee_role == "Manager":
                    role_options.extend(["Asst. Manager", "General Employee"])
                else:  # Asst. Manager
                    role_options.append("General Employee")
                
                role_filter = st.selectbox("Role", role_options, key="branch_employee_role_filter")
            
            with col2:
                # Status filter
                status_options = ["All", "Active", "Inactive"]
                status_filter = st.selectbox("Status", status_options, key="branch_employee_status_filter")
            
            # Apply filters
            filtered_employees = branch_employees
            if role_filter != "All Roles":
                filtered_employees = [e for e in filtered_employees if e[4] == role_filter]
            
            if status_filter == "Active":
                filtered_employees = [e for e in filtered_employees if e[5]]  # is_active is True
            elif status_filter == "Inactive":
                filtered_employees = [e for e in filtered_employees if not e[5]]  # is_active is False
            
            st.write(f"Found {len(filtered_employees)} employees")
            
            for emp in filtered_employees:
                emp_id = emp[0]
                emp_name = emp[1]
                emp_username = emp[2]
                emp_pic_url = emp[3]
                emp_role = emp[4]
                is_active = emp[5]
                
                # Skip showing self in the list
                if emp_id == employee_id:
                    continue
                
                # Check if current user can manage this employee based on roles
                can_manage = False
                if employee_role == "Manager":
                    can_manage = True  # Manager can manage any role
                elif employee_role == "Asst. Manager" and emp_role == "General Employee":
                    can_manage = True  # Asst. Manager can only manage General Employees
                
                if can_manage:
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            try:
                                st.image(emp_pic_url, width=100, use_container_width=False)
                            except:
                                st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
                        
                        with col2:
                            role_class = ""
                            if emp_role == "Manager":
                                role_class = "role-manager"
                            elif emp_role == "Asst. Manager":
                                role_class = "role-asst-manager"
                            else:
                                role_class = "role-employee"
                            
                            status_class = "status-active" if is_active else "status-inactive"
                            
                            st.markdown(f'''
                            <div>
                                <h4>{emp_name} 
                                <span class="role-badge {role_class}">{emp_role}</span>
                                <span class="status-badge {status_class}">{"Active" if is_active else "Inactive"}</span></h4>
                                <p><strong>Username:</strong> {emp_username}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                            
                            # Action buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if is_active:  # If active
                                    if st.button(f"Deactivate", key=f"manager_deactivate_{emp_id}"):
                                        with engine.connect() as conn:
                                            conn.execute(text('UPDATE employees SET is_active = FALSE WHERE id = :id'), {'id': emp_id})
                                            conn.commit()
                                        st.success(f"Deactivated employee: {emp_name}")
                                        st.rerun()
                                else:  # If inactive
                                    if st.button(f"Activate", key=f"manager_activate_{emp_id}"):
                                        with engine.connect() as conn:
                                            conn.execute(text('UPDATE employees SET is_active = TRUE WHERE id = :id'), {'id': emp_id})
                                            conn.commit()
                                        st.success(f"Activated employee: {emp_name}")
                                        st.rerun()
                            
                            with col2:
                                if st.button(f"Reset Password", key=f"manager_reset_{emp_id}"):
                                    new_password = "employee123"  # Default reset password
                                    with engine.connect() as conn:
                                        conn.execute(text('UPDATE employees SET password = :password WHERE id = :id'), 
                                                    {'id': emp_id, 'password': new_password})
                                        conn.commit()
                                    st.success(f"Password reset to '{new_password}' for {emp_name}")
    
    with tab2:
        # Form to add new employee
        # Only add employees with lower role than current user
        with st.form("manager_add_employee_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username", help="Username for employee login")
            password = st.text_input("Password", type="password", help="Initial password")
            profile_pic_url = st.text_input("Profile Picture URL", help="Link to employee profile picture")
            
            # Role selection based on current user's role
            role_options = []
            if employee_role == "Manager":
                role_options = ["Asst. Manager", "General Employee"]
            else:  # Asst. Manager
                role_options = ["General Employee"]
            
            role = st.selectbox("Role", role_options)
            
            submitted = st.form_submit_button("Add Employee")
            if submitted:
                if not full_name or not username or not password:
                    st.error("Please fill all required fields")
                else:
                    # Check if username already exists
                    with engine.connect() as conn:
                        result = conn.execute(text('SELECT COUNT(*) FROM employees WHERE username = :username'), 
                                             {'username': username})
                        count = result.fetchone()[0]
                        
                        if count > 0:
                            st.error(f"Username '{username}' already exists")
                        else:
                            # Check if branch already has a manager if adding a manager
                            if role == "Manager":
                                result = conn.execute(text('''
                                SELECT COUNT(*) FROM employees 
                                WHERE branch_id = :branch_id AND role = 'Manager' AND is_active = TRUE
                                '''), {'branch_id': branch_id})
                                manager_count = result.fetchone()[0]
                                
                                if manager_count > 0:
                                    st.error(f"Branch already has an active manager. Please deactivate the current manager first or select a different role.")
                                    st.stop()
                            
                            # Insert new employee
                            try:
                                conn.execute(text('''
                                INSERT INTO employees (branch_id, username, password, full_name, profile_pic_url, role, is_active)
                                VALUES (:branch_id, :username, :password, :full_name, :profile_pic_url, :role, TRUE)
                                '''), {
                                    'branch_id': branch_id,
                                    'username': username,
                                    'password': password,
                                    'full_name': full_name,
                                    'profile_pic_url': profile_pic_url if profile_pic_url else "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y",
                                    'role': role
                                })
                                conn.commit()
                                st.success(f"Successfully added employee: {full_name} as {role}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding employee: {e}")

# Manage Branch Tasks (for Manager and Asst. Manager)
def manage_branch_tasks():
    st.markdown('<h2 class="sub-header">Manage Branch Tasks</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    employee_role = st.session_state.user["role"]
    branch_id = st.session_state.user["branch_id"]
    branch_name = st.session_state.user["branch_name"]
    
    st.markdown(f'<p>Managing tasks for <strong>{branch_name}</strong></p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["View Tasks", "Assign New Task"])
    
    with tab1:
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Status filter
            status_options = ["All Tasks", "Pending", "Completed"]
            status_filter = st.selectbox("Status", status_options, key="manager_task_status_filter")
        
        with col2:
            # Assignment filter
            assignment_options = ["All Tasks", "Branch Tasks", "Employee Tasks"]
            assignment_filter = st.selectbox("Assigned To", assignment_options, key="manager_task_assigned_filter")
        
        # Build query
        query = '''
        SELECT t.id, t.assigned_by_type, t.assigned_by_id, t.assigned_to_type, t.assigned_to_id,
               t.task_description, t.due_date, t.is_completed, t.created_at,
               CASE 
                   WHEN t.assigned_to_type = 'employee' THEN 
                       (SELECT e.full_name FROM employees e WHERE e.id = t.assigned_to_id)
                   ELSE 'Branch'
               END as assigned_to_name,
               CASE 
                   WHEN t.assigned_by_type = 'employee' THEN 
                       (SELECT e.full_name FROM employees e WHERE e.id = t.assigned_by_id)
                   WHEN t.assigned_by_type = 'company' THEN 
                       'Company'
                   ELSE 'Unknown'
               END as assigned_by_name,
               CASE 
                   WHEN t.assigned_to_type = 'branch' THEN 
                       (SELECT COUNT(*) FROM employees e WHERE e.branch_id = t.assigned_to_id AND e.is_active = TRUE)
                   ELSE 0
               END as employee_count,
               CASE 
                   WHEN t.assigned_to_type = 'branch' THEN 
                       (SELECT COUNT(*) FROM task_completions tc 
                        JOIN employees e ON tc.employee_id = e.id
                        WHERE tc.task_id = t.id AND e.branch_id = t.assigned_to_id)
                   ELSE 0
               END as completion_count
        FROM tasks t
        WHERE (
            (t.assigned_by_type = 'employee' AND t.assigned_by_id = :employee_id)
            OR (t.assigned_to_type = 'branch' AND t.assigned_to_id = :branch_id)
            OR (t.assigned_to_type = 'employee' AND t.assigned_to_id IN 
                (SELECT id FROM employees WHERE branch_id = :branch_id))
        )
        '''
        
        params = {'employee_id': employee_id, 'branch_id': branch_id}
        
        # Apply filters
        if status_filter == "Pending":
            query += ' AND t.is_completed = FALSE'
        elif status_filter == "Completed":
            query += ' AND t.is_completed = TRUE'
        
        if assignment_filter == "Branch Tasks":
            query += ' AND t.assigned_to_type = \'branch\''
        elif assignment_filter == "Employee Tasks":
            query += ' AND t.assigned_to_type = \'employee\''
        
        query += ' ORDER BY t.due_date ASC NULLS LAST, t.created_at DESC'
        
        # Execute query
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            tasks = result.fetchall()
        
        # Display tasks
        if not tasks:
            st.info("No tasks found for the selected criteria")
        else:
            st.write(f"Found {len(tasks)} tasks")
            
            for task in tasks:
                task_id = task[0]
                assigned_by_type = task[1]
                assigned_to_type = task[3]
                assigned_to_id = task[4]
                task_description = task[5]
                due_date = task[6].strftime('%d %b, %Y') if task[6] else "No due date"
                is_completed = task[7]
                created_at = task[8]
                assigned_to_name = task[9]
                assigned_by_name = task[10]
                
                # For branch tasks, check completion status
                employee_count = task[11] if assigned_to_type == 'branch' else 0
                completion_count = task[12] if assigned_to_type == 'branch' else 0
                
                # Status style
                status_class = "completed" if is_completed else ""
                
                # Progress percentage for branch tasks
                progress_percentage = int((completion_count / employee_count) * 100) if employee_count > 0 else 0
                
                with st.container():
                    st.markdown(f'''
                    <div class="task-item {status_class}">
                        <div style="display: flex; justify-content: space-between;">
                            <h4>Task for: {assigned_to_name}</h4>
                            <span style="font-weight: 600; color: {'#9e9e9e' if is_completed else '#4CAF50'};">
                                {"Completed" if is_completed else "Pending"}
                            </span>
                        </div>
                        <p><strong>Due:</strong> {due_date}</p>
                        <p>{task_description}</p>
                        {f"""
                        <div style="margin: 10px 0;">
                            <div style="background-color: #e0e0e0; height: 10px; border-radius: 5px; overflow: hidden;">
                                <div style="background-color: #4CAF50; height: 100%; width: {progress_percentage}%;"></div>
                            </div>
                            <div style="text-align: center; font-size: 0.8rem; margin-top: 5px;">
                                {completion_count}/{employee_count} completed
                            </div>
                        </div>
                        """ if assigned_to_type == 'branch' else ""}
                        <div style="display: flex; justify-content: space-between; color: #777; font-size: 0.8rem;">
                            <span>Assigned by: {assigned_by_name}</span>
                            <span>Created: {created_at.strftime('%d %b, %Y')}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Action buttons (only allow actions on tasks assigned by the current user or for branch tasks)
                    if (assigned_by_type == 'employee' and not is_completed) or (assigned_to_type == 'branch' and employee_role == "Manager" and not is_completed):
                        if st.button(f"Mark as Completed", key=f"manager_complete_task_{task_id}"):
                            with engine.connect() as conn:
                                # Mark task as completed
                                conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task_id})
                                conn.commit()
                            st.success("Task marked as completed")
                            st.rerun()
    
    with tab2:
        # Form to assign new task
        with st.form("manager_assign_task_form"):
            # Select assignment type
            assignment_type = st.selectbox("Assign Task To", ["Employee", "Branch"])
            
            # If assigning to employee, select employee from branch
            if assignment_type == "Employee":
                # Get employees from this branch that can be managed by current user
                with engine.connect() as conn:
                    query = '''
                    SELECT id, full_name, role FROM employees 
                    WHERE branch_id = :branch_id AND is_active = TRUE
                    '''
                    
                    # If not manager, can only assign to general employees
                    if employee_role != "Manager":
                        query += " AND role = 'General Employee'"
                    
                    # Exclude self
                    query += " AND id != :employee_id"
                    
                    query += " ORDER BY full_name"
                    
                    result = conn.execute(text(query), {'branch_id': branch_id, 'employee_id': employee_id})
                    branch_employees = result.fetchall()
                
                if not branch_employees:
                    st.error("No employees available to assign tasks to")
                    submitted = st.form_submit_button("Assign Task", disabled=True)
                else:
                    employee_options = [f"{e[1]} - {e[2]} (ID: {e[0]})" for e in branch_employees]
                    selected_employee = st.selectbox("Select Employee", employee_options)
                    employee_assign_id = int(selected_employee.split("(ID: ")[1].split(")")[0])
                    assigned_to_id = employee_assign_id
                    assigned_to_type = 'employee'
            else:
                # Assign to branch
                assigned_to_id = branch_id
                assigned_to_type = 'branch'
            
            # Task details
            task_description = st.text_area("Task Description")
            due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=7))
            
            submitted = st.form_submit_button("Assign Task")
            if submitted:
                if not task_description:
                    st.error("Please enter a task description")
                else:
                    # Insert new task
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            INSERT INTO tasks (assigned_by_type, assigned_by_id, assigned_to_type, assigned_to_id, 
                                              task_description, due_date, is_completed)
                            VALUES ('employee', :employee_id, :assigned_to_type, :assigned_to_id, 
                                   :task_description, :due_date, FALSE)
                            '''), {
                                'employee_id': employee_id,
                                'assigned_to_type': assigned_to_type,
                                'assigned_to_id': assigned_to_id,
                                'task_description': task_description,
                                'due_date': due_date
                            })
                            conn.commit()
                        
                        success_message = f"Successfully assigned task to {assignment_type.lower()}"
                        if assignment_type == "Employee":
                            employee_name = selected_employee.split(" - ")[0]
                            success_message += f": {employee_name}"
                        else:
                            success_message += f": {branch_name}"
                        
                        st.success(success_message)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error assigning task: {e}")

# View Branch Reports (only for Manager)
def view_branch_reports():
    st.markdown('<h2 class="sub-header">View Branch Reports</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    branch_id = st.session_state.user["branch_id"]
    branch_name = st.session_state.user["branch_name"]
    
    st.markdown(f'<p>Viewing reports for <strong>{branch_name}</strong></p>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Employee filter
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, full_name, role FROM employees 
            WHERE branch_id = :branch_id
            ORDER BY role, full_name
            '''), {'branch_id': branch_id})
            branch_employees = result.fetchall()
        
        employee_options = ["All Employees"] + [f"{e[1]} - {e[2]} (ID: {e[0]})" for e in branch_employees]
        employee_filter = st.selectbox("Employee", employee_options, key="branch_report_employee_filter")
    
    with col2:
        # Role filter
        role_options = ["All Roles", "Asst. Manager", "General Employee"]
        role_filter = st.selectbox("Role", role_options, key="branch_report_role_filter")
    
    with col3:
        # Date range filter
        today = datetime.date.today()
        date_options = [
            "All Time",
            "Today",
            "This Week",
            "This Month",
            "This Year",
            "Custom Range"
        ]
        date_filter = st.selectbox("Date Range", date_options, key="branch_report_date_filter")
    
    # Custom date range if selected
    if date_filter == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", today - datetime.timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", today)
    else:
        # Set default dates based on filter
        if date_filter == "Today":
            start_date = today
            end_date = today
        elif date_filter == "This Week":
            start_date = today - datetime.timedelta(days=today.weekday())
            end_date = today
        elif date_filter == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif date_filter == "This Year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        else:  # All Time
            start_date = datetime.date(2000, 1, 1)
            end_date = today
    
    # Build query based on filters
    query = '''
    SELECT dr.id, dr.employee_id, dr.report_date, dr.report_text, dr.created_at,
           e.full_name, e.role
    FROM daily_reports dr
    JOIN employees e ON dr.employee_id = e.id
    WHERE e.branch_id = :branch_id
    AND dr.report_date BETWEEN :start_date AND :end_date
    '''
    
    params = {'branch_id': branch_id, 'start_date': start_date, 'end_date': end_date}
    
    if employee_filter != "All Employees":
        employee_id_filter = int(employee_filter.split("(ID: ")[1].split(")")[0])
        query += ' AND dr.employee_id = :employee_id_filter'
        params['employee_id_filter'] = employee_id_filter
    
    if role_filter != "All Roles":
        query += ' AND e.role = :role'
        params['role'] = role_filter
    
    query += ' ORDER BY dr.report_date DESC, e.full_name'
    
    # Execute query
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        reports = result.fetchall()
    
    # Display reports
    if not reports:
        st.info("No reports found for the selected criteria")
    else:
        st.write(f"Found {len(reports)} reports")
        
        # Export options
        if st.button("Export Reports as PDF"):
            pdf = create_manager_report_pdf(reports, branch_name, start_date, end_date)
            st.download_button(
                label="Download PDF",
                data=pdf,
                file_name=f"{branch_name}_reports_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        
        # Group by employee for organization
        reports_by_employee = {}
        for report in reports:
            employee_id = report[1]
            employee_name = report[5]
            employee_role = report[6]
            
            if employee_id not in reports_by_employee:
                reports_by_employee[employee_id] = {
                    "name": employee_name,
                    "role": employee_role,
                    "reports": []
                }
            reports_by_employee[employee_id]["reports"].append(report)
        
        # Display reports by employee
        for employee_data in reports_by_employee.values():
            employee_name = employee_data["name"]
            employee_role = employee_data["role"]
            employee_reports = employee_data["reports"]
            
            role_class = ""
            if employee_role == "Manager":
                role_class = "role-manager"
            elif employee_role == "Asst. Manager":
                role_class = "role-asst-manager"
            else:
                role_class = "role-employee"
            
            with st.expander(f"{employee_name} - {employee_role} ({len(employee_reports)} reports)", expanded=True):
                # Export options for this employee
                if st.button(f"Export {employee_name} Reports as PDF", key=f"export_{employee_name}"):
                    pdf = create_manager_report_pdf(employee_reports, f"{branch_name} - {employee_name}", start_date, end_date)
                    st.download_button(
                        label=f"Download {employee_name} PDF",
                        data=pdf,
                        file_name=f"{employee_name}_reports_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                
                # Group by month/year for better organization
                reports_by_period = {}
                for report in employee_reports:
                    period = report[2].strftime('%B %Y')
                    if period not in reports_by_period:
                        reports_by_period[period] = []
                    reports_by_period[period].append(report)
                
                for period, period_reports in reports_by_period.items():
                    st.markdown(f"##### {period}")
                    for report in period_reports:
                        report_date = report[2]
                        report_text = report[3]
                        
                        st.markdown(f'''
                        <div class="report-item">
                            <span style="color: #777;">{report_date.strftime('%A, %d %b %Y')}</span>
                            <p>{report_text}</p>
                        </div>
                        ''', unsafe_allow_html=True)

# Create PDF for manager branch reports
def create_manager_report_pdf(reports, title, start_date, end_date):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    elements.append(Paragraph(f"Branch Reports: {title}", title_style))
    elements.append(Spacer(1, 12))
    
    # Date range
    date_style = ParagraphStyle(
        'DateRange',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.gray
    )
    elements.append(Paragraph(f"Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}", date_style))
    elements.append(Spacer(1, 20))
    
    # Group reports by employee, then by month
    reports_by_employee = {}
    for report in reports:
        employee_name = report[5]
        employee_role = report[6]
        
        if employee_name not in reports_by_employee:
            reports_by_employee[employee_name] = {
                "role": employee_role,
                "reports": []
            }
        reports_by_employee[employee_name]["reports"].append(report)
    
    # Add each employee's reports
    for employee_name, employee_data in reports_by_employee.items():
        # Employee header
        employee_style = ParagraphStyle(
            'Employee',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.blue,
            spaceAfter=10
        )
        elements.append(Paragraph(f"{employee_name} - {employee_data['role']}", employee_style))
        
        # Group by month
        reports_by_month = {}
        for report in employee_data["reports"]:
            month_year = report[2].strftime('%B %Y')
            if month_year not in reports_by_month:
                reports_by_month[month_year] = []
            reports_by_month[month_year].append(report)
        
        # Add each month's reports
        for month, month_reports in reports_by_month.items():
            # Month header
            month_style = ParagraphStyle(
                'Month',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=6
            )
            elements.append(Paragraph(month, month_style))
            
            # Reports for the month
            for report in month_reports:
                # Date
                date_style = ParagraphStyle(
                    'Date',
                    parent=styles['Normal'],
                    fontSize=11,
                    textColor=colors.darkblue
                )
                elements.append(Paragraph(report[2].strftime('%A, %d %b %Y'), date_style))
                
                # Report text
                text_style = ParagraphStyle(
                    'ReportText',
                    parent=styles['Normal'],
                    fontSize=10,
                    leftIndent=10
                )
                elements.append(Paragraph(report[3], text_style))
                elements.append(Spacer(1, 12))
            
            elements.append(Spacer(1, 8))
        
        elements.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# Edit Employee Profile
def edit_employee_profile():
    st.markdown('<h2 class="sub-header">Edit My Profile</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    
    # Fetch current employee data
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT username, full_name, profile_pic_url
        FROM employees
        WHERE id = :employee_id
        '''), {'employee_id': employee_id})
        employee_data = result.fetchone()
    
    if not employee_data:
        st.error("Could not retrieve your profile information. Please try again later.")
        return
    
    username, current_full_name, current_pic_url = employee_data
    
    # Display current profile picture
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<p>Current Profile Picture:</p>", unsafe_allow_html=True)
        try:
            st.image(current_pic_url, width=150, use_container_width=False)
        except:
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=150, use_container_width=False)
    
    with col2:
        st.markdown(f"<p><strong>Username:</strong> {username}</p>", unsafe_allow_html=True)
        st.info("Username cannot be changed as it is used for login purposes.")
    
    # Form for updating profile
    with st.form("update_employee_profile_form"):
        st.subheader("Update Your Information")
        
        # Full name update
        new_full_name = st.text_input("Full Name", value=current_full_name)
        
        # Profile picture URL update
        new_profile_pic_url = st.text_input("Profile Picture URL", value=current_pic_url or "")
        
        # Password update section
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Update Profile")
        if submitted:
            updates_made = False
            
            # Check if any changes were made to name or picture URL
            if new_full_name != current_full_name or new_profile_pic_url != current_pic_url:
                with engine.connect() as conn:
                    conn.execute(text('''
                    UPDATE employees
                    SET full_name = :full_name, profile_pic_url = :profile_pic_url
                    WHERE id = :employee_id
                    '''), {
                        'full_name': new_full_name,
                        'profile_pic_url': new_profile_pic_url,
                        'employee_id': employee_id
                    })
                    conn.commit()
                
                # Update session state with new values
                st.session_state.user["full_name"] = new_full_name
                st.session_state.user["profile_pic_url"] = new_profile_pic_url
                
                updates_made = True
                st.success("Profile information updated successfully.")
            
            # Handle password change if attempted
            if current_password or new_password or confirm_password:
                if not current_password:
                    st.error("Please enter your current password to change it.")
                elif not new_password:
                    st.error("Please enter a new password.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                else:
                    # Verify current password
                    with engine.connect() as conn:
                        result = conn.execute(text('''
                        SELECT COUNT(*)
                        FROM employees
                        WHERE id = :employee_id AND password = :current_password
                        '''), {'employee_id': employee_id, 'current_password': current_password})
                        is_valid = result.fetchone()[0] > 0
                    
                    if not is_valid:
                        st.error("Current password is incorrect.")
                    else:
                        # Update password
                        with engine.connect() as conn:
                            conn.execute(text('''
                            UPDATE employees
                            SET password = :new_password
                            WHERE id = :employee_id
                            '''), {'new_password': new_password, 'employee_id': employee_id})
                            conn.commit()
                        
                        updates_made = True
                        st.success("Password updated successfully.")
            
            if updates_made:
                time.sleep(1)  # Give the user time to read the success message
                st.rerun()

# Main function
def main():
    global engine
    engine = init_connection()
    
    if engine:
        # Initialize database tables
        init_db()
        
        # Check if user is logged in
        if "user" not in st.session_state:
            display_login()
        else:
            # Show appropriate dashboard based on user type
            user_type = st.session_state.user.get("user_type", "")
            
            if user_type == "admin":
                admin_dashboard()
            elif user_type == "company":
                company_dashboard()
            elif user_type == "employee":
                employee_dashboard()
            else:
                st.error("Invalid user type. Please log out and log in again.")
                if st.button("Logout"):
                    logout()
    else:
        st.error("Failed to connect to the database. Please check your database configuration.")

if __name__ == "__main__":
    main()
    
    # Check if credentials match admin in Streamlit secrets
    admin_username = st.secrets["admin_username"]
    admin_password = st.secrets["admin_password"]
    
    if username == admin_username and password == admin_password and (user_type == 'any' or user_type == 'admin'):
        return {
            "id": 0,  # Special ID for admin
            "username": username, 
            "full_name": "Administrator", 
            "user_type": "admin", 
            "profile_pic_url": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        }
    
    # If not admin and looking for company
    if user_type == 'any' or user_type == 'company':
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, username, company_name, profile_pic_url
            FROM companies
            WHERE username = :username AND password = :password AND is_active = TRUE
            '''), {'username': username, 'password': password})
            company = result.fetchone()
        
        if company:
            return {
                "id": company[0], 
                "username": company[1], 
                "full_name": company[2], 
                "user_type": "company", 
                "profile_pic_url": company[3]
            }
    
    # If not admin or company and looking for employee
    if user_type == 'any' or user_type == 'employee':
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT e.id, e.username, e.full_name, e.profile_pic_url, e.role, e.branch_id, b.branch_name, b.company_id, c.company_name
            FROM employees e
            JOIN branches b ON e.branch_id = b.id
            JOIN companies c ON b.company_id = c.id
            WHERE e.username = :username AND e.password = :password AND e.is_active = TRUE AND b.is_active = TRUE AND c.is_active = TRUE
            '''), {'username': username, 'password': password})
            employee = result.fetchone()
        
        if employee:
            return {
                "id": employee[0], 
                "username": employee[1], 
                "full_name": employee[2], 
                "user_type": "employee", 
                "profile_pic_url": employee[3],
                "role": employee[4],
                "branch_id": employee[5],
                "branch_name": employee[6],
                "company_id": employee[7],
                "company_name": employee[8]
            }
    
    return None

# Login form
def display_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Enhanced Employee Management System</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Login type selection
    login_type = st.selectbox("Login as", ["Admin", "Company", "Employee"])
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        user_type_map = {"Admin": "admin", "Company": "company", "Employee": "employee"}
        user = authenticate(username, password, user_type=user_type_map[login_type])
        
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error(f"Invalid username or password for {login_type} account")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Logout function
def logout():
    st.session_state.pop("user", None)
    st.rerun()

#------------------------- ADMIN DASHBOARD -------------------------#

def admin_dashboard():
    st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Admin profile display
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="profile-container">', unsafe_allow_html=True)
        try:
            st.image(st.session_state.user["profile_pic_url"], width=80, clamp=True, output_format="auto", channels="RGB", use_container_width=False)
        except:
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=80, use_container_width=False)
        
        st.markdown(f'''
        <div>
            <h3>{st.session_state.user["full_name"]}</h3>
            <p>Administrator</p>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Companies", "Messages", "Logout"],
        icons=["house", "building", "envelope", "box-arrow-right"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6", "border-radius": "10px", "margin-bottom": "20px"},
            "icon": {"color": "#1E88E5", "font-size": "16px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "padding": "10px", "border-radius": "5px"},
            "nav-link-selected": {"background-color": "#1E88E5", "color": "white", "font-weight": "600"},
        }
    )
    
    if selected == "Dashboard":
        display_admin_dashboard()
    elif selected == "Companies":
        manage_companies()
    elif selected == "Messages":
        admin_messages()
    elif selected == "Logout":
        logout()

# Admin Dashboard Overview
def display_admin_dashboard():
    st.markdown('<h2 class="sub-header">Overview</h2>', unsafe_allow_html=True)
    
    # Statistics
    with engine.connect() as conn:
        # Total companies
        result = conn.execute(text('SELECT COUNT(*) FROM companies WHERE is_active = TRUE'))
        total_companies = result.fetchone()[0]
        
        # Inactive companies
        result = conn.execute(text('SELECT COUNT(*) FROM companies WHERE is_active = FALSE'))
        inactive_companies = result.fetchone()[0]
        
        # Total branches
        result = conn.execute(text('SELECT COUNT(*) FROM branches WHERE is_active = TRUE'))
        total_branches = result.fetchone()[0]
        
        # Total employees
        result = conn.execute(text('SELECT COUNT(*) FROM employees WHERE is_active = TRUE'))
        total_employees = result.fetchone()[0]
        
        # Recent companies
        result = conn.execute(text('''
        SELECT id, company_name, username, is_active, created_at
        FROM companies
        ORDER BY created_at DESC
        LIMIT 5
        '''))
        recent_companies = result.fetchall()
        
        # Unread messages
        result = conn.execute(text('''
        SELECT COUNT(*) FROM messages 
        WHERE receiver_type = 'admin' AND receiver_id = 0 AND is_read = FALSE
        '''))
        unread_messages = result.fetchone()[0]
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_companies}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Active Companies</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{inactive_companies}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Inactive Companies</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_branches}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Branches</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_employees}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Employees</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Recent Companies</h3>', unsafe_allow_html=True)
        if recent_companies:
            for company in recent_companies:
                status_class = "status-active" if company[3] else "status-inactive"
                status_text = "Active" if company[3] else "Inactive"
                
                st.markdown(f'''
                <div class="company-card">
                    <h4>{company[1]} <span class="status-badge {status_class}">{status_text}</span></h4>
                    <p><strong>Username:</strong> {company[2]}</p>
                    <p><strong>Created:</strong> {company[4].strftime('%d %b, %Y')}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No companies available")
    
    with col2:
        st.markdown('<h3 class="sub-header">Messages</h3>', unsafe_allow_html=True)
        st.markdown(f'''
        <div class="stat-card" style="margin-bottom: 1rem;">
            <div class="stat-value">{unread_messages}</div>
            <div class="stat-label">Unread Messages</div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("View Messages"):
            st.session_state["section"] = "Messages"
            st.rerun()

# Admin Messages
def admin_messages():
    st.markdown('<h2 class="sub-header">Messages</h2>', unsafe_allow_html=True)
    
    # Fetch messages
    with engine.connect() as conn:
        # Fetch companies for filter
        result = conn.execute(text('''
        SELECT id, company_name FROM companies ORDER BY company_name
        '''))
        companies = result.fetchall()
        
        company_options = ["All Companies"] + [f"{c[1]} (ID: {c[0]})" for c in companies]
        selected_company = st.selectbox("Filter by Company", company_options)
        
        # Build query
        query = '''
        SELECT m.id, m.sender_type, m.sender_id, m.receiver_type, m.receiver_id, 
               m.message_text, m.is_read, m.created_at,
               CASE 
                   WHEN m.sender_type = 'admin' THEN 'Administrator'
                   WHEN m.sender_type = 'company' THEN (SELECT company_name FROM companies WHERE id = m.sender_id)
               END as sender_name,
               CASE 
                   WHEN m.receiver_type = 'admin' THEN 'Administrator'
                   WHEN m.receiver_type = 'company' THEN (SELECT company_name FROM companies WHERE id = m.receiver_id)
               END as receiver_name
        FROM messages m
        WHERE (m.sender_type = 'admin' AND m.sender_id = 0) 
           OR (m.receiver_type = 'admin' AND m.receiver_id = 0)
        '''
        
        params = {}
        if selected_company != "All Companies":
            company_id = int(selected_company.split("(ID: ")[1].split(")")[0])
            query += ' AND ((m.sender_type = \'company\' AND m.sender_id = :company_id) OR (m.receiver_type = \'company\' AND m.receiver_id = :company_id))'
            params['company_id'] = company_id
        
        query += ' ORDER BY m.created_at DESC'
        
        result = conn.execute(text(query), params)
        messages = result.fetchall()
    
    # Display message compose form
    if "compose_message" in st.session_state:
        st.subheader("Compose Message")
        
        with st.form("compose_message_form"):
            selected_company = st.selectbox("To Company", [f"{c[1]} (ID: {c[0]})" for c in companies])
            company_id = int(selected_company.split("(ID: ")[1].split(")")[0])
            
            message_text = st.text_area("Message", height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Send Message")
            with col2:
                if st.form_submit_button("Cancel"):
                    del st.session_state["compose_message"]
                    st.rerun()
            
            if submitted:
                if not message_text:
                    st.error("Please enter a message")
                else:
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            INSERT INTO messages (sender_type, sender_id, receiver_type, receiver_id, message_text)
                            VALUES ('admin', 0, 'company', :company_id, :message_text)
                            '''), {
                                'company_id': company_id,
                                'message_text': message_text
                            })
                            conn.commit()
                        
                        st.success("Message sent successfully")
                        del st.session_state["compose_message"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error sending message: {e}")
    else:
        if st.button("Compose New Message"):
            st.session_state["compose_message"] = True
            st.rerun()
    
    # Display messages
    st.subheader("Message History")
    
    if not messages:
        st.info("No messages found")
    else:
        st.write(f"Found {len(messages)} messages")
        
        for msg in messages:
            msg_id = msg[0]
            sender_type = msg[1]
            receiver_type = msg[3]
            message_text = msg[5]
            is_read = msg[6]
            created_at = msg[7]
            sender_name = msg[8]
            receiver_name = msg[9]
            
            is_outgoing = sender_type == 'admin'
            
            with st.container():
                st.markdown(f'''
                <div class="message-item" style="border-left-color: {'#1E88E5' if is_outgoing else '#FF9800'};">
                    <p><strong>{'From: You (Admin)' if is_outgoing else f'From: {sender_name}'}</strong> → 
                    <strong>{'To: You (Admin)' if not is_outgoing else f'To: {receiver_name}'}</strong></p>
                    <p>{message_text}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #777; font-size: 0.8rem;">
                            {created_at.strftime('%d %b, %Y %H:%M')}
                        </span>
                        <span style="font-weight: 600; color: {'#9e9e9e' if is_read else '#4CAF50'};">
                            {'' if is_outgoing else ('Read' if is_read else 'Unread')}
                        </span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Mark as read button
                if not is_outgoing and not is_read:
                    if st.button(f"Mark as Read", key=f"read_{msg_id}"):
                        with engine.connect() as conn:
                            conn.execute(text('UPDATE messages SET is_read = TRUE WHERE id = :id'), {'id': msg_id})
                            conn.commit()
                        st.success("Message marked as read")
                        st.rerun()
    
    # Mark all as read button
    if st.button("Mark All as Read"):
        with engine.connect() as conn:
            conn.execute(text('''
            UPDATE messages 
            SET is_read = TRUE 
            WHERE receiver_type = 'admin' AND receiver_id = 0 AND is_read = FALSE
            '''))
            conn.commit()
        st.success("All messages marked as read")
        st.rerun()

# Manage Companies
def manage_companies():
    st.markdown('<h2 class="sub-header">Manage Companies</h2>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Company List", "Add New Company", "View Branches"])
    
    with tab1:
        # Fetch and display all branches
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, branch_name, is_main_branch, is_active, created_at,
                  (SELECT COUNT(*) FROM employees WHERE branch_id = branches.id) as employee_count
            FROM branches
            WHERE company_id = :company_id
            ORDER BY is_main_branch DESC, branch_name
            '''), {'company_id': company_id})
            branches = result.fetchall()
        
        if not branches:
            st.info("No branches found. Add your first branch using the 'Add New Branch' tab.")
        else:
            # Filter options
            status_filter = st.selectbox("Status Filter", ["All", "Active", "Inactive"], key="branch_status_filter")
            
            filtered_branches = branches
            if status_filter == "Active":
                filtered_branches = [b for b in branches if b[3]]  # is_active is True
            elif status_filter == "Inactive":
                filtered_branches = [b for b in branches if not b[3]]  # is_active is False
            
            st.write(f"Total branches: {len(filtered_branches)}")
            
            for branch in filtered_branches:
                branch_id = branch[0]
                branch_name = branch[1]
                is_main_branch = branch[2]
                is_active = branch[3]
                created_at = branch[4]
                employee_count = branch[5]
                
                with st.expander(f"{branch_name}{' (Main Branch)' if is_main_branch else ''}", expanded=False):
                    status_class = "status-active" if is_active else "status-inactive"
                    status_text = "Active" if is_active else "Inactive"
                    
                    st.markdown(f'''
                    <div>
                        <h3>{branch_name} {" (Main Branch)" if is_main_branch else ""}
                        <span class="status-badge {status_class}">{status_text}</span></h3>
                        <p><strong>Created:</strong> {created_at.strftime('%d %b, %Y')}</p>
                        <p><strong>Employees:</strong> {employee_count}</p>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Action buttons (except for Main Branch which can't be deactivated)
                    if not is_main_branch:
                        col1, col2 = st.columns(2)
                        with col1:
                            if is_active:  # If active
                                if st.button(f"Deactivate", key=f"deactivate_branch_{branch_id}"):
                                    with engine.connect() as conn:
                                        # Deactivate branch
                                        conn.execute(text('UPDATE branches SET is_active = FALSE WHERE id = :id'), {'id': branch_id})
                                        # Employees are automatically inactive because they require active branch
                                        conn.commit()
                                    st.success(f"Deactivated branch: {branch_name} (and all its employees)")
                                    st.rerun()
                            else:  # If inactive
                                if st.button(f"Activate", key=f"activate_branch_{branch_id}"):
                                    with engine.connect() as conn:
                                        # Activate branch
                                        conn.execute(text('UPDATE branches SET is_active = TRUE WHERE id = :id'), {'id': branch_id})
                                        conn.commit()
                                    st.success(f"Activated branch: {branch_name}")
                                    st.rerun()
                    
                    # Display employees of this branch
                    st.markdown("#### Employees in this Branch")
                    
                    with engine.connect() as conn:
                        result = conn.execute(text('''
                        SELECT id, full_name, username, role, is_active
                        FROM employees
                        WHERE branch_id = :branch_id
                        ORDER BY role, full_name
                        '''), {'branch_id': branch_id})
                        branch_employees = result.fetchall()
                    
                    if not branch_employees:
                        st.info("No employees in this branch yet")
                    else:
                        for emp in branch_employees:
                            emp_id = emp[0]
                            emp_name = emp[1]
                            emp_username = emp[2]
                            emp_role = emp[3]
                            emp_is_active = emp[4]
                            
                            role_class = ""
                            if emp_role == "Manager":
                                role_class = "role-manager"
                            elif emp_role == "Asst. Manager":
                                role_class = "role-asst-manager"
                            else:
                                role_class = "role-employee"
                            
                            status_class = "status-active" if emp_is_active else "status-inactive"
                            
                            st.markdown(f'''
                            <div style="padding: 0.5rem; margin-bottom: 0.5rem; border-bottom: 1px solid #eee;">
                                <strong>{emp_name}</strong> 
                                <span class="role-badge {role_class}">{emp_role}</span>
                                <span class="status-badge {status_class}">{"Active" if emp_is_active else "Inactive"}</span>
                                <br/>
                                <small>Username: {emp_username}</small>
                            </div>
                            ''', unsafe_allow_html=True)
    
    with tab2:
        # Form to add new branch
        with st.form("add_branch_form"):
            branch_name = st.text_input("Branch Name", help="Name of the new branch")
            
            submitted = st.form_submit_button("Add Branch")
            if submitted:
                if not branch_name:
                    st.error("Please enter a branch name")
                else:
                    # Check if branch name already exists for this company
                    with engine.connect() as conn:
                        result = conn.execute(text('''
                        SELECT COUNT(*) FROM branches 
                        WHERE company_id = :company_id AND branch_name = :branch_name
                        '''), {'company_id': company_id, 'branch_name': branch_name})
                        count = result.fetchone()[0]
                        
                        if count > 0:
                            st.error(f"Branch '{branch_name}' already exists")
                        else:
                            # Insert new branch
                            try:
                                conn.execute(text('''
                                INSERT INTO branches (company_id, branch_name, is_main_branch, is_active)
                                VALUES (:company_id, :branch_name, FALSE, TRUE)
                                '''), {
                                    'company_id': company_id,
                                    'branch_name': branch_name
                                })
                                conn.commit()
                                st.success(f"Successfully added branch: {branch_name}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding branch: {e}")

# Manage Company Employees
def manage_company_employees():
    st.markdown('<h2 class="sub-header">Manage Employees</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    tab1, tab2, tab3 = st.tabs(["Employee List", "Add New Employee", "Transfer Employee"])
    
    with tab1:
        # Fetch and display all employees
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT e.id, e.full_name, e.username, e.profile_pic_url, e.role, e.is_active, 
                   b.id as branch_id, b.branch_name, b.is_active as branch_is_active
            FROM employees e
            JOIN branches b ON e.branch_id = b.id
            WHERE b.company_id = :company_id
            ORDER BY b.branch_name, e.role, e.full_name
            '''), {'company_id': company_id})
            employees = result.fetchall()
        
        if not employees:
            st.info("No employees found. Add employees using the 'Add New Employee' tab.")
        else:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Branch filter
                with engine.connect() as conn:
                    result = conn.execute(text('''
                    SELECT id, branch_name FROM branches 
                    WHERE company_id = :company_id
                    ORDER BY is_main_branch DESC, branch_name
                    '''), {'company_id': company_id})
                    branches = result.fetchall()
                
                branch_options = ["All Branches"] + [b[1] for b in branches]
                branch_filter = st.selectbox("Branch", branch_options, key="employee_branch_filter")
            
            with col2:
                # Role filter
                role_options = ["All Roles", "Manager", "Asst. Manager", "General Employee"]
                role_filter = st.selectbox("Role", role_options, key="employee_role_filter")
            
            with col3:
                # Status filter
                status_options = ["All", "Active", "Inactive"]
                status_filter = st.selectbox("Status", status_options, key="employee_status_filter")
            
            # Apply filters
            filtered_employees = employees
            if branch_filter != "All Branches":
                filtered_employees = [e for e in filtered_employees if e[7] == branch_filter]
            
            if role_filter != "All Roles":
                filtered_employees = [e for e in filtered_employees if e[4] == role_filter]
            
            if status_filter == "Active":
                filtered_employees = [e for e in filtered_employees if e[5]]  # is_active is True
            elif status_filter == "Inactive":
                filtered_employees = [e for e in filtered_employees if not e[5]]  # is_active is False
            
            st.write(f"Found {len(filtered_employees)} employees")
            
            # Group employees by branch
            employees_by_branch = {}
            for emp in filtered_employees:
                branch_name = emp[7]
                if branch_name not in employees_by_branch:
                    employees_by_branch[branch_name] = []
                employees_by_branch[branch_name].append(emp)
            
            for branch_name, branch_employees in employees_by_branch.items():
                with st.expander(f"{branch_name} ({len(branch_employees)} employees)", expanded=True):
                    for emp in branch_employees:
                        emp_id = emp[0]
                        emp_name = emp[1]
                        emp_username = emp[2]
                        emp_pic_url = emp[3]
                        emp_role = emp[4]
                        is_active = emp[5]
                        branch_is_active = emp[8]
                        
                        with st.container():
                            col1, col2 = st.columns([1, 3])
                            
                            with col1:
                                try:
                                    st.image(emp_pic_url, width=100, use_container_width=False)
                                except:
                                    st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
                            
                            with col2:
                                role_class = ""
                                if emp_role == "Manager":
                                    role_class = "role-manager"
                                elif emp_role == "Asst. Manager":
                                    role_class = "role-asst-manager"
                                else:
                                    role_class = "role-employee"
                                
                                status_class = "status-active" if is_active else "status-inactive"
                                branch_status_msg = "" if branch_is_active else " (Branch Inactive)"
                                
                                st.markdown(f'''
                                <div>
                                    <h4>{emp_name} 
                                    <span class="role-badge {role_class}">{emp_role}</span>
                                    <span class="status-badge {status_class}">{"Active" if is_active else "Inactive"}{branch_status_msg}</span></h4>
                                    <p><strong>Username:</strong> {emp_username}</p>
                                </div>
                                ''', unsafe_allow_html=True)
                                
                                # Action buttons
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    if is_active:  # If active
                                        if st.button(f"Deactivate", key=f"deactivate_emp_{emp_id}"):
                                            with engine.connect() as conn:
                                                conn.execute(text('UPDATE employees SET is_active = FALSE WHERE id = :id'), {'id': emp_id})
                                                conn.commit()
                                            st.success(f"Deactivated employee: {emp_name}")
                                            st.rerun()
                                    else:  # If inactive
                                        if st.button(f"Activate", key=f"activate_emp_{emp_id}"):
                                            with engine.connect() as conn:
                                                conn.execute(text('UPDATE employees SET is_active = TRUE WHERE id = :id'), {'id': emp_id})
                                                conn.commit()
                                            st.success(f"Activated employee: {emp_name}")
                                            st.rerun()
                                
                                with col2:
                                    if st.button(f"Reset Password", key=f"reset_emp_{emp_id}"):
                                        new_password = "employee123"  # Default reset password
                                        with engine.connect() as conn:
                                            conn.execute(text('UPDATE employees SET password = :password WHERE id = :id'), 
                                                        {'id': emp_id, 'password': new_password})
                                            conn.commit()
                                        st.success(f"Password reset to '{new_password}' for {emp_name}")
                                
                                with col3:
                                    # Change role button (open a form)
                                    if st.button(f"Change Role", key=f"role_emp_{emp_id}"):
                                        st.session_state["change_role_employee"] = {
                                            "id": emp_id,
                                            "name": emp_name,
                                            "current_role": emp_role
                                        }
                                        st.rerun()
            
            # Handle role change if employee is selected
            if "change_role_employee" in st.session_state:
                emp_id = st.session_state["change_role_employee"]["id"]
                emp_name = st.session_state["change_role_employee"]["name"]
                current_role = st.session_state["change_role_employee"]["current_role"]
                
                st.markdown(f"### Change Role for {emp_name}")
                st.write(f"Current Role: {current_role}")
                
                with st.form("change_role_form"):
                    new_role = st.selectbox("New Role", ["Manager", "Asst. Manager", "General Employee"], 
                                           index=["Manager", "Asst. Manager", "General Employee"].index(current_role))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("Change Role")
                    with col2:
                        if st.form_submit_button("Cancel"):
                            del st.session_state["change_role_employee"]
                            st.rerun()
                    
                    if submitted:
                        if new_role == current_role:
                            st.info("No change in role")
                        else:
                            try:
                                with engine.connect() as conn:
                                    conn.execute(text('UPDATE employees SET role = :role WHERE id = :id'), 
                                                {'id': emp_id, 'role': new_role})
                                    conn.commit()
                                st.success(f"Role updated from {current_role} to {new_role} for {emp_name}")
                                del st.session_state["change_role_employee"]
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating role: {e}")
    
    with tab2:
        # Form to add new employee
        with st.form("add_employee_form"):
            # Select branch
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT id, branch_name FROM branches 
                WHERE company_id = :company_id AND is_active = TRUE
                    ORDER BY is_main_branch DESC, branch_name
                    '''), {'company_id': company_id})
                    active_branches = result.fetchall()
                
                if not active_branches:
                    st.error("You need to have at least one active branch to assign tasks")
                    submitted = st.form_submit_button("Assign Task", disabled=True)
                else:
                    branch_options = [f"{b[1]} (ID: {b[0]})" for b in active_branches]
                    selected_branch = st.selectbox("Select Branch", branch_options)
                    branch_id = int(selected_branch.split("(ID: ")[1].split(")")[0])
                    assigned_to_id = branch_id
                    assigned_to_type = 'branch'
            else:  # Employee
                # Get active employees
                with engine.connect() as conn:
                    result = conn.execute(text('''
                    SELECT e.id, e.full_name, e.role, b.branch_name
                    FROM employees e
                    JOIN branches b ON e.branch_id = b.id
                    WHERE b.company_id = :company_id AND e.is_active = TRUE AND b.is_active = TRUE
                    ORDER BY e.full_name
                    '''), {'company_id': company_id})
                    active_employees = result.fetchall()
                
                if not active_employees:
                    st.error("You need to have at least one active employee to assign tasks")
                    submitted = st.form_submit_button("Assign Task", disabled=True)
                else:
                    employee_options = [f"{e[1]} - {e[2]} at {e[3]} (ID: {e[0]})" for e in active_employees]
                    selected_employee = st.selectbox("Select Employee", employee_options)
                    employee_id = int(selected_employee.split("(ID: ")[1].split(")")[0])
                    assigned_to_id = employee_id
                    assigned_to_type = 'employee'
            
            # Task details
            task_description = st.text_area("Task Description")
            due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=7))
            
            submitted = st.form_submit_button("Assign Task")
            if submitted:
                if not task_description:
                    st.error("Please enter a task description")
                else:
                    # Insert new task
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            INSERT INTO tasks (assigned_by_type, assigned_by_id, assigned_to_type, assigned_to_id, 
                                              task_description, due_date, is_completed)
                            VALUES ('company', :company_id, :assigned_to_type, :assigned_to_id, 
                                   :task_description, :due_date, FALSE)
                            '''), {
                                'company_id': company_id,
                                'assigned_to_type': assigned_to_type,
                                'assigned_to_id': assigned_to_id,
                                'task_description': task_description,
                                'due_date': due_date
                            })
                            conn.commit()
                        
                        success_message = f"Successfully assigned task to {assignment_type.lower()}"
                        if assignment_type == "Branch":
                            branch_name = selected_branch.split(" (ID:")[0]
                            success_message += f": {branch_name}"
                        else:
                            employee_name = selected_employee.split(" - ")[0]
                            success_message += f": {employee_name}"
                        
                        st.success(success_message)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error assigning task: {e}")

# View Company Reports
def view_company_reports():
    st.markdown('<h2 class="sub-header">View Reports</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Branch filter
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, branch_name FROM branches 
            WHERE company_id = :company_id
            ORDER BY is_main_branch DESC, branch_name
            '''), {'company_id': company_id})
            branches = result.fetchall()
        
        branch_options = ["All Branches"] + [b[1] for b in branches]
        branch_filter = st.selectbox("Branch", branch_options, key="report_branch_filter")
    
    with col2:
        # Employee role filter
        role_options = ["All Roles", "Manager", "Asst. Manager", "General Employee"]
        role_filter = st.selectbox("Employee Role", role_options, key="report_role_filter")
    
    with col3:
        # Date range filter
        today = datetime.date.today()
        date_options = [
            "All Time",
            "Today",
            "This Week",
            "This Month",
            "This Year",
            "Custom Range"
        ]
        date_filter = st.selectbox("Date Range", date_options, key="report_date_filter")
    
    # Custom date range if selected
    if date_filter == "Custom Range":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", today - datetime.timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", today)
    else:
        # Set default dates based on filter
        if date_filter == "Today":
            start_date = today
            end_date = today
        elif date_filter == "This Week":
            start_date = today - datetime.timedelta(days=today.weekday())
            end_date = today
        elif date_filter == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif date_filter == "This Year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        else:  # All Time
            start_date = datetime.date(2000, 1, 1)
            end_date = today
    
    # Build query based on filters
    query = '''
    SELECT dr.id, dr.employee_id, dr.report_date, dr.report_text, dr.created_at,
           e.full_name, e.role, b.id as branch_id, b.branch_name
    FROM daily_reports dr
    JOIN employees e ON dr.employee_id = e.id
    JOIN branches b ON e.branch_id = b.id
    WHERE b.company_id = :company_id
    AND dr.report_date BETWEEN :start_date AND :end_date
    '''
    
    params = {'company_id': company_id, 'start_date': start_date, 'end_date': end_date}
    
    if branch_filter != "All Branches":
        query += ' AND b.branch_name = :branch_name'
        params['branch_name'] = branch_filter
    
    if role_filter != "All Roles":
        query += ' AND e.role = :role'
        params['role'] = role_filter
    
    query += ' ORDER BY dr.report_date DESC, e.full_name'
    
    # Execute query
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        reports = result.fetchall()
    
    # Display reports
    if not reports:
        st.info("No reports found for the selected criteria")
    else:
        st.write(f"Found {len(reports)} reports")
        
        # Group by branch for organization
        reports_by_branch = {}
        for report in reports:
            branch_name = report[8]
            if branch_name not in reports_by_branch:
                reports_by_branch[branch_name] = []
            reports_by_branch[branch_name].append(report)
        
        # Export options for all reports
        if st.button("Export All Reports as PDF"):
            pdf = create_company_report_pdf(reports, start_date, end_date)
            st.download_button(
                label="Download All Reports PDF",
                data=pdf,
                file_name=f"all_reports_{start_date}_to_{end_date}.pdf",
                mime="application/pdf"
            )
        
        # Display reports by branch
        for branch_name, branch_reports in reports_by_branch.items():
            with st.expander(f"Reports from {branch_name} ({len(branch_reports)})", expanded=True):
                # Export options for this branch
                if st.button(f"Export {branch_name} Reports as PDF", key=f"export_{branch_name}"):
                    pdf = create_company_report_pdf(branch_reports, start_date, end_date)
                    st.download_button(
                        label=f"Download {branch_name} PDF",
                        data=pdf,
                        file_name=f"{branch_name}_reports_{start_date}_to_{end_date}.pdf",
                        mime="application/pdf"
                    )
                
                # Group reports by employee
                reports_by_employee = {}
                for report in branch_reports:
                    employee_name = report[5]
                    employee_role = report[6]
                    
                    if employee_name not in reports_by_employee:
                        reports_by_employee[employee_name] = {
                            "role": employee_role,
                            "reports": []
                        }
                    reports_by_employee[employee_name]["reports"].append(report)
                
                # Display reports by employee
                for employee_name, employee_data in reports_by_employee.items():
                    employee_role = employee_data["role"]
                    employee_reports = employee_data["reports"]
                    
                    role_class = ""
                    if employee_role == "Manager":
                        role_class = "role-manager"
                    elif employee_role == "Asst. Manager":
                        role_class = "role-asst-manager"
                    else:
                        role_class = "role-employee"
                    
                    st.markdown(f'''
                    <h4>{employee_name} <span class="role-badge {role_class}">{employee_role}</span></h4>
                    ''', unsafe_allow_html=True)
                    
                    # Export options for this employee
                    if st.button(f"Export {employee_name} Reports as PDF", key=f"export_{branch_name}_{employee_name}"):
                        pdf = create_company_report_pdf(employee_reports, start_date, end_date)
                        st.download_button(
                            label=f"Download {employee_name} PDF",
                            data=pdf,
                            file_name=f"{employee_name}_reports_{start_date}_to_{end_date}.pdf",
                            mime="application/pdf"
                        )
                    
                    # Group by month/year for better organization
                    reports_by_period = {}
                    for report in employee_reports:
                        period = report[2].strftime('%B %Y')
                        if period not in reports_by_period:
                            reports_by_period[period] = []
                        reports_by_period[period].append(report)
                    
                    for period, period_reports in reports_by_period.items():
                        st.markdown(f"##### {period}")
                        for report in period_reports:
                            report_date = report[2]
                            report_text = report[3]
                            
                            st.markdown(f'''
                            <div class="report-item">
                                <span style="color: #777;">{report_date.strftime('%A, %d %b %Y')}</span>
                                <p>{report_text}</p>
                            </div>
                            ''', unsafe_allow_html=True)
                    
                    st.markdown("<hr>", unsafe_allow_html=True)

# Create PDF for company reports
def create_company_report_pdf(reports, start_date, end_date):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )
    elements.append(Paragraph(f"Employee Reports", title_style))
    elements.append(Spacer(1, 12))
    
    # Date range
    date_style = ParagraphStyle(
        'DateRange',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.gray
    )
    elements.append(Paragraph(f"Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}", date_style))
    elements.append(Spacer(1, 20))
    
    # Group reports by branch, then employee
    reports_by_branch = {}
    for report in reports:
        branch_name = report[8]
        employee_name = report[5]
        employee_role = report[6]
        
        if branch_name not in reports_by_branch:
            reports_by_branch[branch_name] = {}
        
        if employee_name not in reports_by_branch[branch_name]:
            reports_by_branch[branch_name][employee_name] = {
                "role": employee_role,
                "reports": []
            }
        
        reports_by_branch[branch_name][employee_name]["reports"].append(report)
    
    # Add each branch's reports
    for branch_name, branch_employees in reports_by_branch.items():
        # Branch header
        branch_style = ParagraphStyle(
            'Branch',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.blue,
            spaceAfter=10
        )
        elements.append(Paragraph(f"Branch: {branch_name}", branch_style))
        
        # Add each employee's reports
        for employee_name, employee_data in branch_employees.items():
            # Employee header
            employee_style = ParagraphStyle(
                'Employee',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.darkgreen,
                spaceAfter=6
            )
            elements.append(Paragraph(f"{employee_name} - {employee_data['role']}", employee_style))
            
            # Group by month
            reports_by_month = {}
            for report in employee_data["reports"]:
                month_year = report[2].strftime('%B %Y')
                if month_year not in reports_by_month:
                    reports_by_month[month_year] = []
                reports_by_month[month_year].append(report)
            
            # Add reports for each month
            for month, month_reports in reports_by_month.items():
                # Month header
                month_style = ParagraphStyle(
                    'Month',
                    parent=styles['Heading4'],
                    fontSize=11,
                    textColor=colors.darkblue,
                    spaceAfter=4
                )
                elements.append(Paragraph(month, month_style))
                
                # Reports for the month
                for report in month_reports:
                    # Date
                    date_style = ParagraphStyle(
                        'Date',
                        parent=styles['Normal'],
                        fontSize=10,
                        textColor=colors.gray
                    )
                    elements.append(Paragraph(report[2].strftime('%A, %d %b %Y'), date_style))
                    
                    # Report text
                    text_style = ParagraphStyle(
                        'ReportText',
                        parent=styles['Normal'],
                        fontSize=10,
                        leftIndent=10,
                        spaceAfter=6
                    )
                    elements.append(Paragraph(report[3], text_style))
                    elements.append(Spacer(1, 6))
            
            elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# Company Messages
def company_messages():
    st.markdown('<h2 class="sub-header">Messages</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Fetch messages
    with engine.connect() as conn:
        query = '''
        SELECT m.id, m.sender_type, m.sender_id, m.receiver_type, m.receiver_id, 
               m.message_text, m.is_read, m.created_at,
               CASE 
                   WHEN m.sender_type = 'admin' THEN 'Administrator'
                   WHEN m.sender_type = 'company' THEN (SELECT company_name FROM companies WHERE id = m.sender_id)
               END as sender_name
        FROM messages m
        WHERE (m.sender_type = 'company' AND m.sender_id = :company_id) 
           OR (m.receiver_type = 'company' AND m.receiver_id = :company_id)
        ORDER BY m.created_at DESC
        '''
        
        result = conn.execute(text(query), {'company_id': company_id})
        messages = result.fetchall()
    
    # Display message compose form
    if st.button("Send Message to Admin"):
        with st.form("send_message_form"):
            message_text = st.text_area("Message", height=150)
            
            submitted = st.form_submit_button("Send Message")
            if submitted:
                if not message_text:
                    st.error("Please enter a message")
                else:
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            INSERT INTO messages (sender_type, sender_id, receiver_type, receiver_id, message_text)
                            VALUES ('company', :company_id, 'admin', 0, :message_text)
                            '''), {
                                'company_id': company_id,
                                'message_text': message_text
                            })
                            conn.commit()
                        
                        st.success("Message sent to Admin")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error sending message: {e}")
    
    # Display messages
    st.subheader("Message History")
    
    if not messages:
        st.info("No messages found")
    else:
        st.write(f"Found {len(messages)} messages")
        
        for msg in messages:
            msg_id = msg[0]
            sender_type = msg[1]
            receiver_type = msg[3]
            message_text = msg[5]
            is_read = msg[6]
            created_at = msg[7]
            sender_name = msg[8]
            
            is_outgoing = sender_type == 'company'
            
            with st.container():
                st.markdown(f'''
                <div class="message-item" style="border-left-color: {'#1E88E5' if is_outgoing else '#FF9800'};">
                    <p><strong>{'From: You' if is_outgoing else f'From: {sender_name}'}</strong> → 
                    <strong>{'To: Administrator' if is_outgoing else 'To: You'}</strong></p>
                    <p>{message_text}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #777; font-size: 0.8rem;">
                            {created_at.strftime('%d %b, %Y %H:%M')}
                        </span>
                        <span style="font-weight: 600; color: {'#9e9e9e' if is_read else '#4CAF50'};">
                            {'' if is_outgoing else ('Read' if is_read else 'Unread')}
                        </span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Mark as read button
                if not is_outgoing and not is_read:
                    if st.button(f"Mark as Read", key=f"read_msg_{msg_id}"):
                        with engine.connect() as conn:
                            conn.execute(text('UPDATE messages SET is_read = TRUE WHERE id = :id'), {'id': msg_id})
                            conn.commit()
                        st.success("Message marked as read")
                        st.rerun()
    
    # Mark all as read button
    if st.button("Mark All as Read"):
        with engine.connect() as conn:
            conn.execute(text('''
            UPDATE messages 
            SET is_read = TRUE 
            WHERE receiver_type = 'company' AND receiver_id = :company_id AND is_read = FALSE
            '''), {'company_id': company_id})
            conn.commit()
        st.success("All messages marked as read")
        st.rerun()

# Edit Company Profile
def edit_company_profile():
    st.markdown('<h2 class="sub-header">Edit Company Profile</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Fetch current company data
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT username, company_name, profile_pic_url
        FROM companies
        WHERE id = :company_id
        '''), {'company_id': company_id})
        company_data = result.fetchone()
    
    if not company_data:
        st.error("Could not retrieve your profile information. Please try again later.")
        return
    
    username, current_company_name, current_pic_url = company_data
    
    # Display current profile picture
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<p>Current Profile Picture:</p>", unsafe_allow_html=True)
        try:
            st.image(current_pic_url, width=150, use_container_width=False)
        except:
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=150, use_container_width=False)
    
    with col2:
        st.markdown(f"<p><strong>Username:</strong> {username}</p>", unsafe_allow_html=True)
        st.info("Username cannot be changed as it is used for login purposes.")
    
    # Form for updating profile
    with st.form("update_company_profile_form"):
        st.subheader("Update Your Information")
        
        # Company name update
        new_company_name = st.text_input("Company Name", value=current_company_name)
        
        # Profile picture URL update
        new_profile_pic_url = st.text_input("Profile Picture URL", value=current_pic_url or "")
        
        # Password update section
        st.subheader("Change Password")
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("Update Profile")
        if submitted:
            updates_made = False
            
            # Check if any changes were made to name or picture URL
            if new_company_name != current_company_name or new_profile_pic_url != current_pic_url:
                with engine.connect() as conn:
                    conn.execute(text('''
                    UPDATE companies
                    SET company_name = :company_name, profile_pic_url = :profile_pic_url
                    WHERE id = :company_id
                    '''), {
                        'company_name': new_company_name,
                        'profile_pic_url': new_profile_pic_url,
                        'company_id': company_id
                    })
                    conn.commit()
                
                # Update session state with new values
                st.session_state.user["full_name"] = new_company_name
                st.session_state.user["profile_pic_url"] = new_profile_pic_url
                
                updates_made = True
                st.success("Profile information updated successfully.")
            
            # Handle password change if attempted
            if current_password or new_password or confirm_password:
                if not current_password:
                    st.error("Please enter your current password to change it.")
                elif not new_password:
                    st.error("Please enter a new password.")
                elif new_password != confirm_password:
                    st.error("New passwords do not match.")
                else:
                    # Verify current password
                    with engine.connect() as conn:
                        result = conn.execute(text('''
                        SELECT COUNT(*)
                        FROM companies
                        WHERE id = :company_id AND password = :current_password
                        '''), {'company_id': company_id, 'current_password': current_password})
                        is_valid = result.fetchone()[0] > 0
                    
                    if not is_valid:
                        st.error("Current password is incorrect.")
                    else:
                        # Update password
                        with engine.connect() as conn:
                            conn.execute(text('''
                            UPDATE companies
                            SET password = :new_password
                            WHERE id = :company_id
                            '''), {'new_password': new_password, 'company_id': company_id})
                            conn.commit()
                        
                        updates_made = True
                        st.success("Password updated successfully.")
            
            if updates_made:
                time.sleep(1)  # Give the user time to read the success message
                st.rerun() TRUE
                ORDER BY is_main_branch DESC, branch_name
                '''), {'company_id': company_id})
                active_branches = result.fetchall()
            
            if not active_branches:
                st.error("You need to have at least one active branch to add employees")
                st.form_submit_button("Add Employee", disabled=True)
            else:
                branch_options = [b[1] for b in active_branches]
                branch_name = st.selectbox("Branch", branch_options)
                branch_id = next(b[0] for b in active_branches if b[1] == branch_name)
                
                # Employee details
                full_name = st.text_input("Full Name")
                username = st.text_input("Username", help="Username for employee login")
                password = st.text_input("Password", type="password", help="Initial password")
                profile_pic_url = st.text_input("Profile Picture URL", help="Link to employee profile picture")
                
                # Role selection
                role = st.selectbox("Role", ["Manager", "Asst. Manager", "General Employee"])
                
                submitted = st.form_submit_button("Add Employee")
                if submitted:
                    if not full_name or not username or not password:
                        st.error("Please fill all required fields")
                    else:
                        # Check if username already exists
                        with engine.connect() as conn:
                            result = conn.execute(text('SELECT COUNT(*) FROM employees WHERE username = :username'), 
                                                {'username': username})
                            count = result.fetchone()[0]
                            
                            if count > 0:
                                st.error(f"Username '{username}' already exists")
                            else:
                                # Check if branch already has a manager if adding a manager
                                if role == "Manager":
                                    result = conn.execute(text('''
                                    SELECT COUNT(*) FROM employees 
                                    WHERE branch_id = :branch_id AND role = 'Manager' AND is_active = TRUE
                                    '''), {'branch_id': branch_id})
                                    manager_count = result.fetchone()[0]
                                    
                                    if manager_count > 0:
                                        st.error(f"Branch already has an active manager. Please deactivate the current manager first or select a different role.")
                                        st.stop()
                                
                                # Insert new employee
                                try:
                                    conn.execute(text('''
                                    INSERT INTO employees (branch_id, username, password, full_name, profile_pic_url, role, is_active)
                                    VALUES (:branch_id, :username, :password, :full_name, :profile_pic_url, :role, TRUE)
                                    '''), {
                                        'branch_id': branch_id,
                                        'username': username,
                                        'password': password,
                                        'full_name': full_name,
                                        'profile_pic_url': profile_pic_url if profile_pic_url else "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y",
                                        'role': role
                                    })
                                    conn.commit()
                                    st.success(f"Successfully added employee: {full_name} as {role} to {branch_name}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error adding employee: {e}")
    
    with tab3:
        # Transfer employee between branches
        st.subheader("Transfer Employee Between Branches")
        
        # Get employees
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT e.id, e.full_name, e.role, b.branch_name
            FROM employees e
            JOIN branches b ON e.branch_id = b.id
            WHERE b.company_id = :company_id AND e.is_active = TRUE AND b.is_active = TRUE
            ORDER BY e.full_name
            '''), {'company_id': company_id})
            active_employees = result.fetchall()
            
            result = conn.execute(text('''
            SELECT id, branch_name FROM branches 
            WHERE company_id = :company_id AND is_active = TRUE
            ORDER BY is_main_branch DESC, branch_name
            '''), {'company_id': company_id})
            active_branches = result.fetchall()
        
        if not active_employees:
            st.info("No active employees to transfer")
        elif not active_branches or len(active_branches) < 2:
            st.info("You need at least two active branches to transfer employees")
        else:
            with st.form("transfer_employee_form"):
                # Select employee to transfer
                employee_options = [f"{e[1]} - {e[2]} at {e[3]} (ID: {e[0]})" for e in active_employees]
                selected_employee = st.selectbox("Select Employee to Transfer", employee_options)
                employee_id = int(selected_employee.split("(ID: ")[1].split(")")[0])
                
                # Get current branch
                current_branch = next(e[3] for e in active_employees if e[0] == employee_id)
                
                # Select destination branch
                branch_options = [b[1] for b in active_branches if b[1] != current_branch]
                destination_branch = st.selectbox("Transfer to Branch", branch_options)
                destination_branch_id = next(b[0] for b in active_branches if b[1] == destination_branch)
                
                # Get employee role
                employee_role = next(e[2] for e in active_employees if e[0] == employee_id)
                
                submitted = st.form_submit_button("Transfer Employee")
                if submitted:
                    # Check if destination branch already has a manager if transferring a manager
                    if employee_role == "Manager":
                        with engine.connect() as conn:
                            result = conn.execute(text('''
                            SELECT COUNT(*) FROM employees 
                            WHERE branch_id = :branch_id AND role = 'Manager' AND is_active = TRUE
                            '''), {'branch_id': destination_branch_id})
                            manager_count = result.fetchone()[0]
                            
                            if manager_count > 0:
                                st.error(f"Destination branch already has an active manager. Please deactivate the current manager first.")
                                st.stop()
                    
                    # Update employee branch
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('UPDATE employees SET branch_id = :branch_id WHERE id = :id'), 
                                        {'id': employee_id, 'branch_id': destination_branch_id})
                            conn.commit()
                        st.success(f"Successfully transferred employee to {destination_branch}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error transferring employee: {e}")

# Manage Company Tasks
def manage_company_tasks():
    st.markdown('<h2 class="sub-header">Manage Tasks</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    tab1, tab2 = st.tabs(["View Tasks", "Assign New Task"])
    
    with tab1:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Assigned to filter
            assigned_to_options = ["All Tasks", "Branch Tasks", "Employee Tasks", "Company Tasks"]
            assigned_to_filter = st.selectbox("Assigned To", assigned_to_options, key="task_assigned_to_filter")
        
        with col2:
            # Status filter
            status_options = ["All Tasks", "Pending", "Completed"]
            status_filter = st.selectbox("Status", status_options, key="task_status_filter")
        
        with col3:
            # Sort by
            sort_options = ["Due Date (Ascending)", "Due Date (Descending)", "Creation Date (Newest)", "Creation Date (Oldest)"]
            sort_by = st.selectbox("Sort By", sort_options, key="task_sort_by")
        
        # Build query based on filters
        query = '''
        SELECT t.id, t.assigned_by_type, t.assigned_by_id, t.assigned_to_type, t.assigned_to_id,
               t.task_description, t.due_date, t.is_completed, t.created_at,
               CASE 
                   WHEN t.assigned_to_type = 'employee' THEN 
                       (SELECT e.full_name FROM employees e WHERE e.id = t.assigned_to_id)
                   WHEN t.assigned_to_type = 'branch' THEN 
                       (SELECT b.branch_name FROM branches b WHERE b.id = t.assigned_to_id)
                   ELSE 'Company'
               END as assigned_to_name,
               CASE 
                   WHEN t.assigned_to_type = 'branch' THEN 
                       (SELECT COUNT(*) FROM employees e WHERE e.branch_id = t.assigned_to_id AND e.is_active = TRUE)
                   ELSE 0
               END as employee_count,
               CASE 
                   WHEN t.assigned_to_type = 'branch' THEN 
                       (SELECT COUNT(*) FROM task_completions tc 
                        JOIN employees e ON tc.employee_id = e.id
                        WHERE tc.task_id = t.id AND e.branch_id = t.assigned_to_id)
                   ELSE 0
               END as completion_count
        FROM tasks t
        WHERE (t.assigned_by_type = 'company' AND t.assigned_by_id = :company_id)
           OR (t.assigned_to_type = 'company' AND t.assigned_to_id = :company_id)
        '''
        
        params = {'company_id': company_id}
        
        # Apply filters
        if assigned_to_filter == "Branch Tasks":
            query += ' AND t.assigned_to_type = \'branch\''
        elif assigned_to_filter == "Employee Tasks":
            query += ' AND t.assigned_to_type = \'employee\''
        elif assigned_to_filter == "Company Tasks":
            query += ' AND t.assigned_to_type = \'company\''
        
        if status_filter == "Pending":
            query += ' AND t.is_completed = FALSE'
        elif status_filter == "Completed":
            query += ' AND t.is_completed = TRUE'
        
        # Apply sorting
        if sort_by == "Due Date (Ascending)":
            query += ' ORDER BY t.due_date ASC NULLS LAST'
        elif sort_by == "Due Date (Descending)":
            query += ' ORDER BY t.due_date DESC NULLS LAST'
        elif sort_by == "Creation Date (Newest)":
            query += ' ORDER BY t.created_at DESC'
        elif sort_by == "Creation Date (Oldest)":
            query += ' ORDER BY t.created_at ASC'
        
        # Execute query
        with engine.connect() as conn:
            result = conn.execute(text(query), params)
            tasks = result.fetchall()
        
        # Display tasks
        if not tasks:
            st.info("No tasks found for the selected criteria")
        else:
            st.write(f"Found {len(tasks)} tasks")
            
            for task in tasks:
                task_id = task[0]
                assigned_to_type = task[3]
                assigned_to_id = task[4]
                task_description = task[5]
                due_date = task[6].strftime('%d %b, %Y') if task[6] else "No due date"
                is_completed = task[7]
                created_at = task[8]
                assigned_to_name = task[9]
                
                # For branch tasks, check completion status
                employee_count = task[10] if assigned_to_type == 'branch' else 0
                completion_count = task[11] if assigned_to_type == 'branch' else 0
                
                # Status style
                status_class = "completed" if is_completed else ""
                
                with st.container():
                    st.markdown(f'''
                    <div class="task-item {status_class}">
                        <div style="display: flex; justify-content: space-between;">
                            <h4>Task for: {assigned_to_name}</h4>
                            <span style="font-weight: 600; color: {'#9e9e9e' if is_completed else '#4CAF50'};">
                                {"Completed" if is_completed else "Pending"}
                            </span>
                        </div>
                        <p><strong>Due:</strong> {due_date}</p>
                        <p>{task_description}</p>
                        {f"<p><strong>Completion:</strong> {completion_count}/{employee_count} employees completed</p>" if assigned_to_type == 'branch' else ""}
                        <div style="font-size: 0.8rem; color: #777; text-align: right;">
                            Created: {created_at.strftime('%d %b, %Y')}
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if not is_completed:
                            if st.button(f"Mark as Completed", key=f"complete_task_{task_id}"):
                                with engine.connect() as conn:
                                    conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task_id})
                                    conn.commit()
                                st.success("Task marked as completed")
                                st.rerun()
                    
                    with col2:
                        if st.button(f"Delete Task", key=f"delete_task_{task_id}"):
                            with engine.connect() as conn:
                                # Delete task completions first
                                conn.execute(text('DELETE FROM task_completions WHERE task_id = :id'), {'id': task_id})
                                # Then delete the task
                                conn.execute(text('DELETE FROM tasks WHERE id = :id'), {'id': task_id})
                                conn.commit()
                            st.success("Task deleted")
                            st.rerun()
    
    with tab2:
        # Form to assign new task
        with st.form("assign_task_form"):
            # Select assignment type
            assignment_type = st.selectbox("Assign Task To", ["Branch", "Employee"])
            
            # Based on assignment type, show different selection options
            if assignment_type == "Branch":
                # Get active branches
                with engine.connect() as conn:
                    result = conn.execute(text('''
                    SELECT id, branch_name FROM branches 
                    WHERE company_id = :company_id AND is_active =
        # Fetch and display all companies
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, company_name, username, profile_pic_url, is_active, created_at 
            FROM companies
            ORDER BY company_name
            '''))
            companies = result.fetchall()
        
        if not companies:
            st.info("No companies found. Add companies using the 'Add New Company' tab.")
        else:
            # Filter options
            status_filter = st.selectbox("Status Filter", ["All", "Active", "Inactive"], key="company_status_filter")
            
            filtered_companies = companies
            if status_filter == "Active":
                filtered_companies = [c for c in companies if c[4]]  # is_active is True
            elif status_filter == "Inactive":
                filtered_companies = [c for c in companies if not c[4]]  # is_active is False
            
            st.write(f"Total companies: {len(filtered_companies)}")
            
            for company in filtered_companies:
                company_id = company[0]
                company_name = company[1]
                username = company[2]
                profile_pic_url = company[3]
                is_active = company[4]
                created_at = company[5]
                
                with st.expander(f"{company_name} ({username})", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        try:
                            st.image(profile_pic_url, width=100, use_container_width=False)
                        except:
                            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
                    
                    with col2:
                        status_class = "status-active" if is_active else "status-inactive"
                        status_text = "Active" if is_active else "Inactive"
                        
                        st.markdown(f'''
                        <h4>{company_name} <span class="status-badge {status_class}">{status_text}</span></h4>
                        <p><strong>Username:</strong> {username}</p>
                        <p><strong>Created:</strong> {created_at.strftime('%d %b, %Y')}</p>
                        ''', unsafe_allow_html=True)
                        
                        # Fetch branches for this company
                        with engine.connect() as conn:
                            result = conn.execute(text('''
                            SELECT COUNT(*) FROM branches WHERE company_id = :company_id
                            '''), {'company_id': company_id})
                            branches_count = result.fetchone()[0]
                            
                            result = conn.execute(text('''
                            SELECT COUNT(*) FROM employees 
                            WHERE branch_id IN (SELECT id FROM branches WHERE company_id = :company_id)
                            '''), {'company_id': company_id})
                            employees_count = result.fetchone()[0]
                        
                        st.write(f"**Branches:** {branches_count}")
                        st.write(f"**Employees:** {employees_count}")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if is_active:  # If active
                                if st.button(f"Deactivate", key=f"deactivate_company_{company_id}"):
                                    with engine.connect() as conn:
                                        # Deactivate company
                                        conn.execute(text('UPDATE companies SET is_active = FALSE WHERE id = :id'), {'id': company_id})
                                        # Deactivate all branches of this company
                                        conn.execute(text('UPDATE branches SET is_active = FALSE WHERE company_id = :company_id'), 
                                                    {'company_id': company_id})
                                        # Employees are automatically inactive because they require active branch and company
                                        conn.commit()
                                    st.success(f"Deactivated company: {company_name} (and all its branches)")
                                    st.rerun()
                            else:  # If inactive
                                if st.button(f"Activate", key=f"activate_company_{company_id}"):
                                    with engine.connect() as conn:
                                        # Activate company
                                        conn.execute(text('UPDATE companies SET is_active = TRUE WHERE id = :id'), {'id': company_id})
                                        # Activate all branches that were active before company deactivation
                                        conn.execute(text('UPDATE branches SET is_active = TRUE WHERE company_id = :company_id'), 
                                                    {'company_id': company_id})
                                        conn.commit()
                                    st.success(f"Activated company: {company_name} (and all its branches)")
                                    st.rerun()
                        
                        with col2:
                            if st.button(f"Reset Password", key=f"reset_company_{company_id}"):
                                new_password = "company123"  # Default reset password
                                with engine.connect() as conn:
                                    conn.execute(text('UPDATE companies SET password = :password WHERE id = :id'), 
                                                {'id': company_id, 'password': new_password})
                                    conn.commit()
                                st.success(f"Password reset to '{new_password}' for {company_name}")
                        
                        with col3:
                            if st.button(f"Send Message", key=f"message_company_{company_id}"):
                                st.session_state["message_to_company"] = {
                                    "id": company_id,
                                    "name": company_name
                                }
                                st.rerun()
    
    with tab2:
        # Check if we're in message mode
        if "message_to_company" in st.session_state:
            company_id = st.session_state["message_to_company"]["id"]
            company_name = st.session_state["message_to_company"]["name"]
            
            st.subheader(f"Send Message to {company_name}")
            
            with st.form("send_message_form"):
                message_text = st.text_area("Message", height=150)
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("Send Message")
                with col2:
                    if st.form_submit_button("Cancel"):
                        del st.session_state["message_to_company"]
                        st.rerun()
                
                if submitted:
                    if not message_text:
                        st.error("Please enter a message")
                    else:
                        try:
                            with engine.connect() as conn:
                                conn.execute(text('''
                                INSERT INTO messages (sender_type, sender_id, receiver_type, receiver_id, message_text)
                                VALUES ('admin', 0, 'company', :company_id, :message_text)
                                '''), {
                                    'company_id': company_id,
                                    'message_text': message_text
                                })
                                conn.commit()
                            
                            st.success(f"Message sent to {company_name}")
                            del st.session_state["message_to_company"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error sending message: {e}")
        else:
        # Form to add new company
        with st.form("add_company_form"):
            company_name = st.text_input("Company Name", help="Name of the company")
            username = st.text_input("Username", help="Username for company login")
            password = st.text_input("Password", type="password", help="Initial password")
            profile_pic_url = st.text_input("Profile Picture URL", help="Link to company profile picture")
            
            submitted = st.form_submit_button("Add Company")
            if submitted:
                if not company_name or not username or not password:
                    st.error("Please fill all required fields")
                else:
                    # Check if username already exists
                    with engine.connect() as conn:
                        result = conn.execute(text('SELECT COUNT(*) FROM companies WHERE username = :username'), 
                                             {'username': username})
                        count = result.fetchone()[0]
                        
                        if count > 0:
                            st.error(f"Username '{username}' already exists")
                        else:
                            # Insert new company and create main branch
                            try:
                                # Insert company
                                conn.execute(text('''
                                INSERT INTO companies (company_name, username, password, profile_pic_url, is_active)
                                VALUES (:company_name, :username, :password, :profile_pic_url, TRUE)
                                RETURNING id
                                '''), {
                                    'company_name': company_name,
                                    'username': username,
                                    'password': password,
                                    'profile_pic_url': profile_pic_url if profile_pic_url else "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
                                })
                                result = conn.fetchone()
                                company_id = result[0]
                                
                                # Create main branch for this company
                                conn.execute(text('''
                                INSERT INTO branches (company_id, branch_name, is_main_branch, is_active)
                                VALUES (:company_id, 'Main Branch', TRUE, TRUE)
                                '''), {
                                    'company_id': company_id
                                })
                                
                                conn.commit()
                                st.success(f"Successfully added company: {company_name} with Main Branch")
                            except Exception as e:
                                st.error(f"Error adding company: {e}")
