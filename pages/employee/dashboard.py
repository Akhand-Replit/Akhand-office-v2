import streamlit as st
import datetime
from sqlalchemy import text
from pages.common.components import (
    display_profile_header, employee_navigation, 
    display_stats_card, display_report_item, 
    display_task_item
)
from pages.employee.reports import submit_report, view_my_reports
from pages.employee.tasks import view_my_tasks
from pages.employee.profile import edit_my_profile
from utils.auth import logout

def employee_dashboard(engine):
    """Display the employee dashboard.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h1 class="main-header">Employee Dashboard</h1>', unsafe_allow_html=True)
    
    # Display employee profile
    display_profile_header(st.session_state.user)
    
    # Navigation
    selected = employee_navigation()
    
    # Clear any previous content to avoid overlap between sections
    if "current_section" in st.session_state and st.session_state.current_section != selected:
        # If switching sections, clear the previous section
        st.session_state.current_section = selected
    else:
        # First time setting the section
        st.session_state.current_section = selected
    
    # Display the selected section
    if selected == "Dashboard":
        display_employee_dashboard_overview(engine)
    elif selected == "Submit Report":
        submit_report(engine)
    elif selected == "My Reports":
        view_my_reports(engine)
    elif selected == "My Tasks":
        view_my_tasks(engine)
    elif selected == "My Profile":
        edit_my_profile(engine)
    elif selected == "Logout":
        logout()

def display_employee_dashboard_overview(engine):
    """Display the employee dashboard overview with statistics and recent activities.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h2 class="sub-header">My Overview</h2>', unsafe_allow_html=True)
    
    employee_id = st.session_state.user["id"]
    
    # Statistics
    with engine.connect() as conn:
        # Total reports
        result = conn.execute(text('SELECT COUNT(*) FROM daily_reports WHERE employee_id = :employee_id'), 
                             {'employee_id': employee_id})
        total_reports = result.fetchone()[0]
        
        # Reports this month
        today = datetime.date.today()
        first_day_of_month = today.replace(day=1)
        result = conn.execute(text('''
        SELECT COUNT(*) FROM daily_reports 
        WHERE employee_id = :employee_id AND report_date >= :first_day
        '''), {'employee_id': employee_id, 'first_day': first_day_of_month})
        reports_this_month = result.fetchone()[0]
        
        # Total tasks
        result = conn.execute(text('SELECT COUNT(*) FROM tasks WHERE employee_id = :employee_id'), 
                             {'employee_id': employee_id})
        total_tasks = result.fetchone()[0]
        
        # Pending tasks
        result = conn.execute(text('''
        SELECT COUNT(*) FROM tasks 
        WHERE employee_id = :employee_id AND is_completed = FALSE
        '''), {'employee_id': employee_id})
        pending_tasks = result.fetchone()[0]
        
        # Recent reports
        result = conn.execute(text('''
        SELECT report_date, report_text FROM daily_reports 
        WHERE employee_id = :employee_id 
        ORDER BY report_date DESC LIMIT 3
        '''), {'employee_id': employee_id})
        recent_reports = result.fetchall()
        
        # Pending tasks details
        result = conn.execute(text('''
        SELECT id, task_description, due_date FROM tasks 
        WHERE employee_id = :employee_id AND is_completed = FALSE 
        ORDER BY due_date ASC NULLS LAST LIMIT 5
        '''), {'employee_id': employee_id})
        pending_task_details = result.fetchall()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_stats_card(total_reports, "Total Reports")
    
    with col2:
        display_stats_card(reports_this_month, "Reports This Month")
    
    with col3:
        display_stats_card(total_tasks, "Total Tasks")
    
    with col4:
        display_stats_card(pending_tasks, "Pending Tasks")
    
    # Recent activity and pending tasks
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">My Recent Reports</h3>', unsafe_allow_html=True)
        if recent_reports:
            for report in recent_reports:
                display_report_item(report[0].strftime('%d %b, %Y'), report[1])
        else:
            st.info("No reports submitted yet")
        
        if st.button("Submit New Report", key="quick_submit"):
            st.session_state["selected_tab"] = "Submit Report"
            st.rerun()
    
    with col2:
        st.markdown('<h3 class="sub-header">My Pending Tasks</h3>', unsafe_allow_html=True)
        if pending_task_details:
            for task in pending_task_details:
                due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                display_task_item(task[1], due_date)
                
                if st.button(f"Mark as Completed", key=f"quick_complete_employee_{task[0]}_{task[2].strftime('%Y%m%d') if task[2] else 'nodate'}"):
                    with engine.connect() as conn:
                        conn.execute(text('UPDATE tasks SET is_completed = TRUE WHERE id = :id'), {'id': task[0]})
                        conn.commit()
                    st.success("Task marked as completed")
                    st.rerun()
        else:
            st.info("No pending tasks")
