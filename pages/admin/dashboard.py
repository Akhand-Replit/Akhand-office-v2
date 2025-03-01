import streamlit as st
from sqlalchemy import text
from pages.common.components import (
    display_profile_header, admin_navigation, 
    display_stats_card, display_report_item, 
    display_task_item
)
from pages.admin.employees import manage_employees
from pages.admin.reports import view_all_reports
from pages.admin.tasks import manage_tasks
from utils.auth import logout
from utils.helpers import calculate_completion_rate

def admin_dashboard(engine):
    """Display the admin dashboard.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)
    
    # Display admin profile
    display_profile_header(st.session_state.user)
    
    # Navigation
    selected = admin_navigation()
    
    if selected == "Dashboard":
        display_admin_dashboard_overview(engine)
    elif selected == "Employees":
        manage_employees(engine)
    elif selected == "Reports":
        view_all_reports(engine)
    elif selected == "Tasks":
        manage_tasks(engine)
    elif selected == "Logout":
        logout()

def display_admin_dashboard_overview(engine):
    """Display the admin dashboard overview with statistics and recent activities.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h2 class="sub-header">Overview</h2>', unsafe_allow_html=True)
    
    # Statistics
    with engine.connect() as conn:
        # Total employees
        result = conn.execute(text('SELECT COUNT(*) FROM employees WHERE is_active = TRUE AND id != 1'))
        total_employees = result.fetchone()[0]
        
        # Total reports
        result = conn.execute(text('SELECT COUNT(*) FROM daily_reports'))
        total_reports = result.fetchone()[0]
        
        # Total tasks
        result = conn.execute(text('SELECT COUNT(*) FROM tasks'))
        total_tasks = result.fetchone()[0]
        
        # Completed tasks
        result = conn.execute(text('SELECT COUNT(*) FROM tasks WHERE is_completed = TRUE'))
        completed_tasks = result.fetchone()[0]
        
        # Recent reports
        result = conn.execute(text('''
        SELECT e.full_name, dr.report_date, dr.report_text 
        FROM daily_reports dr 
        JOIN employees e ON dr.employee_id = e.id 
        ORDER BY dr.created_at DESC 
        LIMIT 5
        '''))
        recent_reports = result.fetchall()
        
        # Pending tasks
        result = conn.execute(text('''
        SELECT e.full_name, t.task_description, t.due_date 
        FROM tasks t 
        JOIN employees e ON t.employee_id = e.id 
        WHERE t.is_completed = FALSE
        ORDER BY t.due_date ASC 
        LIMIT 5
        '''))
        pending_tasks = result.fetchall()
    
    # Display statistics in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        display_stats_card(total_employees, "Active Employees")
    
    with col2:
        display_stats_card(total_reports, "Total Reports")
    
    with col3:
        display_stats_card(total_tasks, "Total Tasks")
    
    with col4:
        completion_rate = calculate_completion_rate(total_tasks, completed_tasks)
        display_stats_card(f"{completion_rate}%", "Task Completion Rate")
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Recent Reports</h3>', unsafe_allow_html=True)
        if recent_reports:
            for report in recent_reports:
                display_report_item(
                    report[1].strftime('%d %b, %Y'),
                    report[2],
                    author=report[0]
                )
        else:
            st.info("No reports available")
    
    with col2:
        st.markdown('<h3 class="sub-header">Pending Tasks</h3>', unsafe_allow_html=True)
        if pending_tasks:
            for task in pending_tasks:
                due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                display_task_item(
                    task[1],
                    due_date,
                    is_completed=False,
                    author=task[0]
                )
        else:
            st.info("No pending tasks")
