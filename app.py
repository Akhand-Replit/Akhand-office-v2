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
    page_title="Company & Employee Management System",
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
        background-image: url("https://i.ibb.co/s9b3rSvg/3a02fb88ce57.png");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
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
    
    .company-item {
        background-color: #f7f0ff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #673AB7;
    }
    
    .message-item {
        background-color: #fff6e6;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #FF9800;
    }
    
    .branch-item {
        background-color: #e6f9ff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #00BCD4;
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
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def init_connection():
    try:
        return create_engine(st.secrets["postgres"]["url"])
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

# Initialize DB tables if they don't exist
def init_db():
    with engine.connect() as conn:
        try:
            # Execute schema creation statements one by one with error handling
            try:
                # Create companies table
                conn.execute(text('''
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    company_name VARCHAR(100) NOT NULL,
                    profile_pic_url TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''))
                conn.commit()
            except Exception as e:
                st.error(f"Error creating companies table: {str(e)}")
            
            try:
                # Create branches table with parent_branch_id for hierarchy
                conn.execute(text('''
                CREATE TABLE IF NOT EXISTS branches (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id),
                    branch_name VARCHAR(100) NOT NULL,
                    branch_type VARCHAR(50) DEFAULT 'Branch',
                    parent_branch_id INTEGER REFERENCES branches(id) NULL,
                    location VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_main BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''))
                conn.commit()
            except Exception as e:
                st.error(f"Error creating branches table: {str(e)}")
            
            try:
                # Create company_messages table
                conn.execute(text('''
                CREATE TABLE IF NOT EXISTS company_messages (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER REFERENCES companies(id),
                    message_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT FALSE
                )
                '''))
                conn.commit()
            except Exception as e:
                st.error(f"Error creating company_messages table: {str(e)}")
            
            try:
                # Create employees table with branch_id and role
                conn.execute(text('''
                CREATE TABLE IF NOT EXISTS employees (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    profile_pic_url TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    branch_id INTEGER REFERENCES branches(id),
                    role VARCHAR(50) DEFAULT 'General Employee',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''))
                conn.commit()
            except Exception as e:
                st.error(f"Error creating employees table: {str(e)}")
            
            try:
                # Create daily_reports table
                conn.execute(text('''
                CREATE TABLE IF NOT EXISTS daily_reports (
                    id SERIAL PRIMARY KEY,
                    employee_id INTEGER REFERENCES employees(id),
                    report_date DATE NOT NULL,
                    report_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''))
                conn.commit()
            except Exception as e:
                st.error(f"Error creating daily_reports table: {str(e)}")
            
            try:
                # Create tasks table with branch assignment
                conn.execute(text('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    branch_id INTEGER REFERENCES branches(id) NULL,
                    employee_id INTEGER REFERENCES employees(id) NULL,
                    task_description TEXT NOT NULL,
                    due_date DATE,
                    is_completed BOOLEAN DEFAULT FALSE,
                    completed_by_id INTEGER REFERENCES employees(id) NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''))
                conn.commit()
            except Exception as e:
                st.error(f"Error creating tasks table: {str(e)}")
                
            try:
                # Create task_assignments table for tracking individual employee task completion
                conn.execute(text('''
                CREATE TABLE IF NOT EXISTS task_assignments (
                    id SERIAL PRIMARY KEY,
                    task_id INTEGER REFERENCES tasks(id),
                    employee_id INTEGER REFERENCES employees(id),
                    is_completed BOOLEAN DEFAULT FALSE,
                    completed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                '''))
                conn.commit()
            except Exception as e:
                st.error(f"Error creating task_assignments table: {str(e)}")
                
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")

# Authentication function
def authenticate(username, password):
    # Check if admin credentials are properly set in Streamlit secrets
    if "admin_username" not in st.secrets or "admin_password" not in st.secrets:
        st.warning("Admin credentials are not properly configured in Streamlit secrets. Please set admin_username and admin_password in .streamlit/secrets.toml")
        return None
    
    # Check if credentials match admin in Streamlit secrets
    admin_username = st.secrets["admin_username"]
    admin_password = st.secrets["admin_password"]
    
    if username == admin_username and password == admin_password:
        return {
            "id": 0,  # Special ID for admin
            "username": username, 
            "full_name": "Administrator", 
            "is_admin": True, 
            "profile_pic_url": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        }
    
    # Check if company credentials match
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
            "is_admin": False, 
            "is_company": True,
            "profile_pic_url": company[3] or "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        }
    
    # Check if employee credentials match
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT e.id, e.username, e.full_name, e.profile_pic_url, e.branch_id, b.company_id
        FROM employees e
        JOIN branches b ON e.branch_id = b.id
        WHERE e.username = :username AND e.password = :password AND e.is_active = TRUE
        '''), {'username': username, 'password': password})
        employee = result.fetchone()
    
    if employee:
        return {
            "id": employee[0], 
            "username": employee[1], 
            "full_name": employee[2], 
            "is_admin": False,
            "is_company": False,
            "branch_id": employee[4],
            "company_id": employee[5],
            "profile_pic_url": employee[3] or "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        }
    
    return None

# Login form
def display_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">Company & Employee Management System</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        user = authenticate(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Logout function
def logout():
    st.session_state.pop("user", None)
    st.rerun()

# Admin Dashboard
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
        options=["Dashboard", "Companies", "Reports", "Messages", "Logout"],
        icons=["house", "building", "clipboard-data", "envelope", "box-arrow-right"],
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
    elif selected == "Reports":
        view_all_reports()
    elif selected == "Messages":
        manage_messages()
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
        
        # Total branches
        result = conn.execute(text('SELECT COUNT(*) FROM branches WHERE is_active = TRUE'))
        total_branches = result.fetchone()[0]
        
        # Total employees
        result = conn.execute(text('SELECT COUNT(*) FROM employees WHERE is_active = TRUE'))
        total_employees = result.fetchone()[0]
        
        # Total reports
        result = conn.execute(text('SELECT COUNT(*) FROM daily_reports'))
        total_reports = result.fetchone()[0]
        
        # Recent companies
        result = conn.execute(text('''
        SELECT company_name, username, created_at, is_active 
        FROM companies 
        ORDER BY created_at DESC 
        LIMIT 5
        '''))
        recent_companies = result.fetchall()
        
        # Recent branches
        result = conn.execute(text('''
        SELECT b.branch_name, c.company_name, b.created_at, b.is_active 
        FROM branches b
        JOIN companies c ON b.company_id = c.id
        ORDER BY b.created_at DESC 
        LIMIT 5
        '''))
        recent_branches = result.fetchall()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_companies}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Active Companies</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_branches}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Active Branches</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_employees}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Active Employees</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_reports}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Reports</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Recent Companies</h3>', unsafe_allow_html=True)
        if recent_companies:
            for company in recent_companies:
                status = "Active" if company[3] else "Inactive"
                status_color = "#4CAF50" if company[3] else "#F44336"
                
                st.markdown(f'''
                <div class="company-item">
                    <strong>{company[0]}</strong>
                    <p>Username: {company[1]}</p>
                    <p>Created: {company[2].strftime('%d %b, %Y')}</p>
                    <p>Status: <span style="color: {status_color};">{status}</span></p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No companies available")
    
    with col2:
        st.markdown('<h3 class="sub-header">Recent Branches</h3>', unsafe_allow_html=True)
        if recent_branches:
            for branch in recent_branches:
                status = "Active" if branch[3] else "Inactive"
                status_color = "#4CAF50" if branch[3] else "#F44336"
                
                st.markdown(f'''
                <div class="branch-item">
                    <strong>{branch[0]}</strong>
                    <p>Company: {branch[1]}</p>
                    <p>Created: {branch[2].strftime('%d %b, %Y')}</p>
                    <p>Status: <span style="color: {status_color};">{status}</span></p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No branches available")

# Manage Companies
def manage_companies():
    st.markdown('<h2 class="sub-header">Manage Companies</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Company List", "Add New Company"])
    
    with tab1:
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
            st.write(f"Total companies: {len(companies)}")
            
            for company in companies:
                company_id = company[0]
                company_name = company[1]
                username = company[2]
                profile_pic = company[3] or "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
                is_active = company[4]
                created_at = company[5].strftime('%d %b, %Y')
                
                with st.expander(f"{company_name} ({username})", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        try:
                            st.image(profile_pic, width=100, use_container_width=False)
                        except:
                            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
                    
                    with col2:
                        st.write(f"**Company Name:** {company_name}")
                        st.write(f"**Username:** {username}")
                        st.write(f"**Created:** {created_at}")
                        st.write(f"**Status:** {'Active' if is_active else 'Inactive'}")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if is_active:  # If active
                                if st.button(f"Deactivate", key=f"deactivate_company_{company_id}"):
                                    with engine.connect() as conn:
                                        # Deactivate company
                                        conn.execute(text('UPDATE companies SET is_active = FALSE WHERE id = :id'), {'id': company_id})
                                        
                                        # Cascade deactivation to branches
                                        conn.execute(text('UPDATE branches SET is_active = FALSE WHERE company_id = :company_id'), 
                                                  {'company_id': company_id})
                                        
                                        # Cascade deactivation to employees
                                        conn.execute(text('''
                                        UPDATE employees SET is_active = FALSE 
                                        WHERE branch_id IN (SELECT id FROM branches WHERE company_id = :company_id)
                                        '''), {'company_id': company_id})
                                        
                                        conn.commit()
                                    st.success(f"Deactivated company: {company_name} (including all branches and employees)")
                                    st.rerun()
                            else:  # If inactive
                                if st.button(f"Activate", key=f"activate_company_{company_id}"):
                                    with engine.connect() as conn:
                                        # Activate company
                                        conn.execute(text('UPDATE companies SET is_active = TRUE WHERE id = :id'), {'id': company_id})
                                        
                                        # Cascade activation to branches
                                        conn.execute(text('UPDATE branches SET is_active = TRUE WHERE company_id = :company_id'), 
                                                  {'company_id': company_id})
                                        
                                        # Cascade activation to employees
                                        conn.execute(text('''
                                        UPDATE employees SET is_active = TRUE 
                                        WHERE branch_id IN (SELECT id FROM branches WHERE company_id = :company_id)
                                        '''), {'company_id': company_id})
                                        
                                        conn.commit()
                                    st.success(f"Activated company: {company_name} (including all branches and employees)")
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
                                st.session_state.selected_company_for_message = {
                                    'id': company_id,
                                    'name': company_name
                                }
                                st.rerun()
                    
                    # Display branches for this company
                    st.markdown('<h4>Company Branches</h4>', unsafe_allow_html=True)
                    
                    with engine.connect() as conn:
                        result = conn.execute(text('''
                        SELECT id, branch_name, location, is_active, created_at
                        FROM branches
                        WHERE company_id = :company_id
                        ORDER BY branch_name
                        '''), {'company_id': company_id})
                        branches = result.fetchall()
                    
                    if not branches:
                        st.info(f"No branches found for {company_name}")
                    else:
                        branches_df = pd.DataFrame(
                            [(b[1], b[2] or "N/A", "Active" if b[3] else "Inactive", b[4].strftime('%d %b, %Y')) 
                             for b in branches],
                            columns=["Branch Name", "Location", "Status", "Created"]
                        )
                        st.dataframe(branches_df, use_container_width=True)
    
    with tab2:
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
                            # Insert new company
                            try:
                                conn.execute(text('''
                                INSERT INTO companies (company_name, username, password, profile_pic_url, is_active)
                                VALUES (:company_name, :username, :password, :profile_pic_url, TRUE)
                                '''), {
                                    'company_name': company_name,
                                    'username': username,
                                    'password': password,
                                    'profile_pic_url': profile_pic_url
                                })
                                conn.commit()
                                st.success(f"Successfully added company: {company_name}")
                            except Exception as e:
                                st.error(f"Error adding company: {e}")

    # Message form if a company is selected
    if hasattr(st.session_state, 'selected_company_for_message'):
        company_id = st.session_state.selected_company_for_message['id']
        company_name = st.session_state.selected_company_for_message['name']
        
        st.markdown(f'<h3 class="sub-header">Send Message to {company_name}</h3>', unsafe_allow_html=True)
        
        with st.form("send_company_message_form"):
            message_text = st.text_area("Message", height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                sent = st.form_submit_button("Send Message")
            
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if sent:
                if not message_text:
                    st.error("Please enter a message")
                else:
                    with engine.connect() as conn:
                        conn.execute(text('''
                        INSERT INTO company_messages (company_id, message_text)
                        VALUES (:company_id, :message_text)
                        '''), {
                            'company_id': company_id,
                            'message_text': message_text
                        })
                        conn.commit()
                    
                    st.success(f"Message sent to {company_name}")
                    del st.session_state.selected_company_for_message
                    st.rerun()
            
            if cancel:
                del st.session_state.selected_company_for_message
                st.rerun()

# View All Reports function for Admin
def view_all_reports():
    st.markdown('<h2 class="sub-header">All Reports</h2>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Company filter
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, company_name FROM companies 
            WHERE is_active = TRUE
            ORDER BY company_name
            '''))
            companies = result.fetchall()
        
        company_options = ["All Companies"] + [comp[1] for comp in companies]
        company_filter = st.selectbox("Select Company", company_options, key="reports_company_filter")
        
        # If company selected, get branches
        if company_filter != "All Companies":
            selected_company_id = next(comp[0] for comp in companies if comp[1] == company_filter)
            
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT id, branch_name FROM branches 
                WHERE company_id = :company_id AND is_active = TRUE
                ORDER BY branch_name
                '''), {'company_id': selected_company_id})
                branches = result.fetchall()
            
            branch_options = ["All Branches"] + [branch[1] for branch in branches]
            branch_filter = st.selectbox("Select Branch", branch_options, key="reports_branch_filter")
        else:
            branch_filter = "All Branches"
    
    with col2:
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
        date_filter = st.selectbox("Date Range", date_options, key="reports_date_filter")
    
    with col3:
        # Custom date range if selected
        if date_filter == "Custom Range":
            start_date = st.date_input("Start Date", today - datetime.timedelta(days=30))
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
    SELECT e.full_name as employee_name, dr.report_date, dr.report_text, dr.id, 
           b.branch_name, c.company_name
    FROM daily_reports dr
    JOIN employees e ON dr.employee_id = e.id
    JOIN branches b ON e.branch_id = b.id
    JOIN companies c ON b.company_id = c.id
    WHERE dr.report_date BETWEEN :start_date AND :end_date
    '''
    
    params = {'start_date': start_date, 'end_date': end_date}
    
    if company_filter != "All Companies":
        query += ' AND c.company_name = :company_name'
        params['company_name'] = company_filter
        
        if branch_filter != "All Branches":
            query += ' AND b.branch_name = :branch_name'
            params['branch_name'] = branch_filter
    
    query += ' ORDER BY dr.report_date DESC, c.company_name, b.branch_name, e.full_name'
    
    # Execute query
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        reports = result.fetchall()
    
    # Display reports
    if not reports:
        st.info("No reports found for the selected criteria")
    else:
        st.write(f"Found {len(reports)} reports")
        
        # Group by company and branch for better organization
        reports_by_company = {}
        for report in reports:
            company_name = report[5]
            if company_name not in reports_by_company:
                reports_by_company[company_name] = {}
            
            branch_name = report[4]
            if branch_name not in reports_by_company[company_name]:
                reports_by_company[company_name][branch_name] = []
            
            reports_by_company[company_name][branch_name].append(report)
        
        # Display reports grouped by company and branch
        for company_name, branches in reports_by_company.items():
            with st.expander(f"Reports from {company_name}", expanded=True):
                for branch_name, branch_reports in branches.items():
                    st.markdown(f"#### Branch: {branch_name}")
                    
                    # Group by employee
                    reports_by_employee = {}
                    for report in branch_reports:
                        employee_name = report[0]
                        if employee_name not in reports_by_employee:
                            reports_by_employee[employee_name] = []
                        reports_by_employee[employee_name].append(report)
                    
                    # Display employee reports
                    for employee_name, emp_reports in reports_by_employee.items():
                        with st.expander(f"Reports by {employee_name} ({len(emp_reports)})", expanded=False):
                            # Group by month/year for better organization
                            reports_by_period = {}
                            for report in emp_reports:
                                period = report[1].strftime('%B %Y')
                                if period not in reports_by_period:
                                    reports_by_period[period] = []
                                reports_by_period[period].append(report)
                            
                            for period, period_reports in reports_by_period.items():
                                st.markdown(f"##### {period}")
                                for report in period_reports:
                                    st.markdown(f'''
                                    <div class="report-item">
                                        <span style="color: #777;">{report[1].strftime('%A, %d %b %Y')}</span>
                                        <p>{report[2]}</p>
                                    </div>
                                    ''', unsafe_allow_html=True)

# Manage Messages for Admin
def manage_messages():
    st.markdown('<h2 class="sub-header">Company Messages</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Send New Message", "Message History"])
    
    with tab1:
        # First check if any active companies exist
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, company_name FROM companies 
            WHERE is_active = TRUE
            ORDER BY company_name
            '''))
            companies = result.fetchall()
        
        if not companies:
            st.info("No active companies available to message")
        else:
            # Form to send a message to a company
            with st.form("send_message_form"):
                company_id = st.selectbox("Select Company", 
                                   options=[c[0] for c in companies],
                                   format_func=lambda x: next(c[1] for c in companies if c[0] == x))
                
                message_text = st.text_area("Message", height=150)
                
                submitted = st.form_submit_button("Send Message")
                if submitted:
                    if not message_text:
                        st.error("Please enter a message")
                    else:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            INSERT INTO company_messages (company_id, message_text)
                            VALUES (:company_id, :message_text)
                            '''), {
                                'company_id': company_id,
                                'message_text': message_text
                            })
                            conn.commit()
                        
                        company_name = next(c[1] for c in companies if c[0] == company_id)
                        st.success(f"Message sent to {company_name}")
    
    with tab2:
        # Display message history
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT cm.id, c.company_name, cm.message_text, cm.created_at, cm.is_read
            FROM company_messages cm
            JOIN companies c ON cm.company_id = c.id
            ORDER BY cm.created_at DESC
            '''))
            messages = result.fetchall()
        
        if not messages:
            st.info("No message history found")
        else:
            st.write(f"Total messages: {len(messages)}")
            
            # Group messages by company
            messages_by_company = {}
            for msg in messages:
                company_name = msg[1]
                if company_name not in messages_by_company:
                    messages_by_company[company_name] = []
                messages_by_company[company_name].append(msg)
            
            # Display messages by company
            for company_name, company_messages in messages_by_company.items():
                with st.expander(f"Messages to {company_name} ({len(company_messages)})", expanded=False):
                    for msg in company_messages:
                        read_status = "Read" if msg[4] else "Unread"
                        status_color = "#9e9e9e" if msg[4] else "#1E88E5"
                        
                        st.markdown(f'''
                        <div class="message-item">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #777;">{msg[3].strftime('%d %b %Y, %H:%M')}</span>
                                <span style="color: {status_color}; font-weight: 600;">{read_status}</span>
                            </div>
                            <p style="margin-top: 0.5rem;">{msg[2]}</p>
                        </div>
                        ''', unsafe_allow_html=True)

# Company Dashboard
def company_dashboard():
    st.markdown('<h1 class="main-header">Company Dashboard</h1>', unsafe_allow_html=True)
    
    # Company profile display
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
            <p>Company Management</p>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Branches", "Employees", "Tasks", "Reports", "Messages", "Profile", "Logout"],
        icons=["house", "building", "people", "list-task", "clipboard-data", "envelope", "person-circle", "box-arrow-right"],
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
        display_company_dashboard()
    elif selected == "Branches":
        manage_branches()
    elif selected == "Employees":
        manage_company_employees()
    elif selected == "Tasks":
        manage_company_tasks()
    elif selected == "Reports":
        view_company_reports()
    elif selected == "Messages":
        view_company_messages()
    elif selected == "Profile":
        edit_company_profile()
    elif selected == "Logout":
        logout()

# Company Dashboard Overview
def display_company_dashboard():
    st.markdown('<h2 class="sub-header">Company Overview</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Check if tables exist before querying
    with engine.connect() as conn:
        try:
            # Check if branches table exists
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'branches')"))
            branches_exists = result.fetchone()[0]
            
            # Check if employees table exists
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employees')"))
            employees_exists = result.fetchone()[0]
            
            # Check if daily_reports table exists
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'daily_reports')"))
            reports_exists = result.fetchone()[0]
            
            # Check if company_messages table exists
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'company_messages')"))
            messages_exists = result.fetchone()[0]
            
            # Check if tasks table exists
            result = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tasks')"))
            tasks_exists = result.fetchone()[0]
            
            # Statistics
            # Total branches
            if branches_exists:
                result = conn.execute(text('''
                SELECT 
                    (SELECT COUNT(*) FROM branches WHERE company_id = :company_id AND is_active = TRUE AND branch_type = 'Branch') as branch_count,
                    (SELECT COUNT(*) FROM branches WHERE company_id = :company_id AND is_active = TRUE AND branch_type = 'Sub-Branch') as sub_branch_count,
                    (SELECT COUNT(*) FROM branches WHERE company_id = :company_id AND is_active = TRUE) as total_branch_count
                '''), {'company_id': company_id})
                branch_counts = result.fetchone()
                branch_count = branch_counts[0]
                sub_branch_count = branch_counts[1]
                total_branches = branch_counts[2]
            else:
                branch_count = 0
                sub_branch_count = 0
                total_branches = 0
            
            # Total employees by role
            if branches_exists and employees_exists:
                result = conn.execute(text('''
                SELECT role, COUNT(*) 
                FROM employees e
                JOIN branches b ON e.branch_id = b.id
                WHERE b.company_id = :company_id AND e.is_active = TRUE
                GROUP BY role
                '''), {'company_id': company_id})
                role_counts = {}
                for row in result.fetchall():
                    role_counts[row[0]] = row[1]
                
                manager_count = role_counts.get('Manager', 0)
                asst_manager_count = role_counts.get('Asst. Manager', 0)
                employee_count = role_counts.get('General Employee', 0)
                total_employees = manager_count + asst_manager_count + employee_count
            else:
                manager_count = 0
                asst_manager_count = 0
                employee_count = 0
                total_employees = 0
            
            # Total reports
            if branches_exists and employees_exists and reports_exists:
                result = conn.execute(text('''
                SELECT COUNT(*) FROM daily_reports dr
                JOIN employees e ON dr.employee_id = e.id
                JOIN branches b ON e.branch_id = b.id
                WHERE b.company_id = :company_id
                '''), {'company_id': company_id})
                total_reports = result.fetchone()[0]
                
                # Reports in last 30 days
                today = datetime.date.today()
                month_ago = today - datetime.timedelta(days=30)
                result = conn.execute(text('''
                SELECT COUNT(*) FROM daily_reports dr
                JOIN employees e ON dr.employee_id = e.id
                JOIN branches b ON e.branch_id = b.id
                WHERE b.company_id = :company_id AND dr.report_date >= :month_ago
                '''), {'company_id': company_id, 'month_ago': month_ago})
                recent_reports = result.fetchone()[0]
            else:
                total_reports = 0
                recent_reports = 0
            
            # Task statistics
            if tasks_exists:
                result = conn.execute(text('''
                SELECT 
                    (SELECT COUNT(*) FROM tasks t 
                     JOIN branches b ON t.branch_id = b.id 
                     WHERE b.company_id = :company_id AND t.employee_id IS NULL) as branch_tasks,
                    (SELECT COUNT(*) FROM tasks t 
                     JOIN employees e ON t.employee_id = e.id
                     JOIN branches b ON e.branch_id = b.id
                     WHERE b.company_id = :company_id) as individual_tasks,
                    (SELECT COUNT(*) FROM tasks t 
                     LEFT JOIN branches b ON t.branch_id = b.id 
                     LEFT JOIN employees e ON t.employee_id = e.id
                     LEFT JOIN branches b2 ON e.branch_id = b2.id
                     WHERE (b.company_id = :company_id OR b2.company_id = :company_id) AND t.is_completed = TRUE) as completed_tasks,
                    (SELECT COUNT(*) FROM tasks t 
                     LEFT JOIN branches b ON t.branch_id = b.id 
                     LEFT JOIN employees e ON t.employee_id = e.id
                     LEFT JOIN branches b2 ON e.branch_id = b2.id
                     WHERE (b.company_id = :company_id OR b2.company_id = :company_id)) as total_tasks
                '''), {'company_id': company_id})
                task_counts = result.fetchone()
                branch_tasks = task_counts[0]
                individual_tasks = task_counts[1]
                completed_tasks = task_counts[2]
                total_tasks = task_counts[3]
                completion_rate = 0 if total_tasks == 0 else round((completed_tasks / total_tasks) * 100)
            else:
                branch_tasks = 0
                individual_tasks = 0
                completed_tasks = 0
                total_tasks = 0
                completion_rate = 0
            
            # Unread messages
            if messages_exists:
                result = conn.execute(text('''
                SELECT COUNT(*) FROM company_messages
                WHERE company_id = :company_id AND is_read = FALSE
                '''), {'company_id': company_id})
                unread_messages = result.fetchone()[0]
            else:
                unread_messages = 0
            
            # Recent branches
            if branches_exists:
                result = conn.execute(text('''
                SELECT branch_name, branch_type, location, created_at, is_active
                FROM branches
                WHERE company_id = :company_id
                ORDER BY created_at DESC
                LIMIT 5
                '''), {'company_id': company_id})
                recent_branches = result.fetchall()
            else:
                recent_branches = []
            
            # Recent employees
            if branches_exists and employees_exists:
                result = conn.execute(text('''
                SELECT e.full_name, e.role, b.branch_name, e.created_at, e.is_active
                FROM employees e
                JOIN branches b ON e.branch_id = b.id
                WHERE b.company_id = :company_id
                ORDER BY e.created_at DESC
                LIMIT 5
                '''), {'company_id': company_id})
                recent_employees = result.fetchall()
            else:
                recent_employees = []
                
            # Recent tasks with completion status
            if tasks_exists:
                result = conn.execute(text('''
                SELECT t.task_description, t.due_date, t.is_completed, 
                       CASE WHEN t.employee_id IS NULL THEN b.branch_name ELSE e.full_name END as assigned_to,
                       CASE WHEN t.employee_id IS NULL THEN 'Branch' ELSE 'Individual' END as assignment_type,
                       t.created_at
                FROM tasks t
                LEFT JOIN branches b ON t.branch_id = b.id
                LEFT JOIN employees e ON t.employee_id = e.id
                LEFT JOIN branches b2 ON e.branch_id = b2.id
                WHERE (b.company_id = :company_id OR b2.company_id = :company_id)
                ORDER BY t.created_at DESC
                LIMIT 5
                '''), {'company_id': company_id})
                recent_tasks = result.fetchall()
            else:
                recent_tasks = []
                
        except Exception as e:
            st.error(f"Error retrieving dashboard data: {str(e)}")
            branch_count = 0
            sub_branch_count = 0
            total_branches = 0
            manager_count = 0
            asst_manager_count = 0
            employee_count = 0
            total_employees = 0
            total_reports = 0
            recent_reports = 0
            branch_tasks = 0
            individual_tasks = 0
            completed_tasks = 0
            total_tasks = 0
            completion_rate = 0
            unread_messages = 0
            recent_branches = []
            recent_employees = []
            recent_tasks = []
    
    # Display statistics in an organized dashboard
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Branch statistics
    st.markdown('<h3>Branch Statistics</h3>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{branch_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Branches</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{sub_branch_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Sub-Branches</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_branches}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Branches</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Employee statistics
    st.markdown('<h3>Employee Statistics</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{manager_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Managers</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{asst_manager_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Asst. Managers</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{employee_count}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">General Employees</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_employees}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Employees</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Task and report statistics
    st.markdown('<h3>Activity Statistics</h3>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_tasks}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Tasks</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{completion_rate}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Task Completion Rate</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_reports}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Reports</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{unread_messages}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Unread Messages</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display task analytics
    if total_tasks > 0:
        st.markdown('<h3 class="sub-header">Task Analytics</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            # Task distribution chart
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h4>Task Distribution</h4>', unsafe_allow_html=True)
            
            # Data for pie chart
            labels = ['Branch Tasks', 'Individual Tasks']
            values = [branch_tasks, individual_tasks]
            
            # Plot using Plotly
            fig = px.pie(
                names=labels, 
                values=values,
                color_discrete_sequence=['#1E88E5', '#4CAF50']
            )
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Task completion status
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h4>Task Completion Status</h4>', unsafe_allow_html=True)
            
            # Data for pie chart
            labels = ['Completed', 'Pending']
            values = [completed_tasks, total_tasks - completed_tasks]
            
            # Plot using Plotly
            fig = px.pie(
                names=labels, 
                values=values,
                color_discrete_sequence=['#4CAF50', '#FFC107']
            )
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Recent Tasks</h3>', unsafe_allow_html=True)
        if recent_tasks:
            for task in recent_tasks:
                task_description = task[0]
                due_date = task[1].strftime('%d %b, %Y') if task[1] else "No due date"
                is_completed = task[2]
                assigned_to = task[3]
                assignment_type = task[4]
                created_at = task[5].strftime('%d %b, %Y')
                
                status_class = "completed" if is_completed else ""
                
                st.markdown(f'''
                <div class="task-item {status_class}">
                    <strong>{assignment_type} Task for {assigned_to}</strong> - Due: {due_date}
                    <p>{task_description[:100]}{'...' if len(task_description) > 100 else ''}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #777; font-size: 0.8rem;">Created: {created_at}</span>
                        <span style="font-weight: 600; color: {'#9e9e9e' if is_completed else '#4CAF50'};">
                            {"Completed" if is_completed else "Pending"}
                        </span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No tasks available")
    
    with col2:
        st.markdown('<h3 class="sub-header">Recent Employees</h3>', unsafe_allow_html=True)
        if recent_employees:
            for employee in recent_employees:
                full_name = employee[0]
                role = employee[1]
                branch_name = employee[2]
                created_at = employee[3].strftime('%d %b, %Y')
                is_active = employee[4]
                
                status = "Active" if is_active else "Inactive"
                status_color = "#4CAF50" if is_active else "#F44336"
                
                st.markdown(f'''
                <div class="task-item">
                    <strong>{full_name}</strong> - {role}
                    <p>Branch: {branch_name}</p>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #777; font-size: 0.8rem;">Joined: {created_at}</span>
                        <span style="font-weight: 600; color: {status_color};">
                            {status}
                        </span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No employees available")
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_branches}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Active Branches</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_employees}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Active Employees</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{total_reports}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Reports</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-value">{unread_messages}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Unread Messages</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent branches and employees
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Recent Branches</h3>', unsafe_allow_html=True)
        if recent_branches:
            for branch in recent_branches:
                status = "Active" if branch[3] else "Inactive"
                status_color = "#4CAF50" if branch[3] else "#F44336"
                
                st.markdown(f'''
                <div class="branch-item">
                    <strong>{branch[0]}</strong>
                    <p>Location: {branch[1] or 'N/A'}</p>
                    <p>Created: {branch[2].strftime('%d %b, %Y')}</p>
                    <p>Status: <span style="color: {status_color};">{status}</span></p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No branches available. Create branches to manage your company structure.")
    
    with col2:
        st.markdown('<h3 class="sub-header">Recent Employees</h3>', unsafe_allow_html=True)
        if recent_employees:
            for employee in recent_employees:
                status = "Active" if employee[3] else "Inactive"
                status_color = "#4CAF50" if employee[3] else "#F44336"
                
                st.markdown(f'''
                <div class="task-item">
                    <strong>{employee[0]}</strong>
                    <p>Branch: {employee[1]}</p>
                    <p>Joined: {employee[2].strftime('%d %b, %Y')}</p>
                    <p>Status: <span style="color: {status_color};">{status}</span></p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No employees available. Add employees to your branches.")

# Manage Branches for Companies
def manage_branches():
    st.markdown('<h2 class="sub-header">Manage Branches</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Check if main branch exists, create if it doesn't
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT COUNT(*) FROM branches 
        WHERE company_id = :company_id AND is_main = TRUE
        '''), {'company_id': company_id})
        main_branch_exists = result.fetchone()[0] > 0
        
        if not main_branch_exists:
            try:
                # Create main branch for this company
                conn.execute(text('''
                INSERT INTO branches (company_id, branch_name, branch_type, is_main, is_active)
                VALUES (:company_id, 'Main Branch', 'Main', TRUE, TRUE)
                '''), {'company_id': company_id})
                conn.commit()
                st.success("Main Branch has been created automatically")
            except Exception as e:
                st.error(f"Error creating main branch: {str(e)}")
    
    tab1, tab2, tab3 = st.tabs(["Branch List", "Add New Branch", "Add Sub-Branch"])
    
    with tab1:
        # Fetch and display all branches
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT b.id, b.branch_name, b.branch_type, p.branch_name as parent_branch, 
                   b.location, b.created_at, b.is_active, b.is_main
            FROM branches b
            LEFT JOIN branches p ON b.parent_branch_id = p.id
            WHERE b.company_id = :company_id
            ORDER BY b.is_main DESC, b.branch_name
            '''), {'company_id': company_id})
            branches = result.fetchall()
        
        if not branches:
            st.info("No branches found. Add branches using the 'Add New Branch' tab.")
        else:
            st.write(f"Total branches: {len(branches)}")
            
            # Create a separate list for main branches and sub-branches
            main_branches = []
            regular_branches = []
            sub_branches = []
            
            for branch in branches:
                if branch[7]:  # is_main
                    main_branches.append(branch)
                elif branch[2] == "Sub-Branch":
                    sub_branches.append(branch)
                else:
                    regular_branches.append(branch)
            
            # Display main branch first
            if main_branches:
                st.markdown("### Main Branch")
                for branch in main_branches:
                    display_branch(branch, company_id)
            
            # Display regular branches
            if regular_branches:
                st.markdown("### Branches")
                for branch in regular_branches:
                    display_branch(branch, company_id)
            
            # Display sub-branches
            if sub_branches:
                st.markdown("### Sub-Branches")
                for branch in sub_branches:
                    display_branch(branch, company_id)
    
    with tab2:
        # Form to add new branch
        with st.form("add_branch_form"):
            st.subheader("Add New Branch")
            branch_name = st.text_input("Branch Name", help="Name of the branch")
            location = st.text_input("Location", help="Branch location (city, address, etc.)")
            
            submitted = st.form_submit_button("Add Branch")
            if submitted:
                if not branch_name:
                    st.error("Please enter a branch name")
                else:
                    # Insert new branch
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            INSERT INTO branches (company_id, branch_name, branch_type, location, is_active)
                            VALUES (:company_id, :branch_name, 'Branch', :location, TRUE)
                            '''), {
                                'company_id': company_id,
                                'branch_name': branch_name,
                                'location': location
                            })
                            conn.commit()
                        st.success(f"Successfully added branch: {branch_name}")
                    except Exception as e:
                        st.error(f"Error adding branch: {e}")
    
    with tab3:
        # Form to add new sub-branch connected to a parent branch
        with st.form("add_sub_branch_form"):
            st.subheader("Add New Sub-Branch")
            
            # Get parent branches for selection
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT id, branch_name FROM branches 
                WHERE company_id = :company_id AND is_active = TRUE
                ORDER BY branch_name
                '''), {'company_id': company_id})
                parent_branches = result.fetchall()
            
            if not parent_branches:
                st.error("You need to create at least one main branch or branch first")
                st.stop()
            
            parent_branch_id = st.selectbox("Parent Branch", 
                                    options=[b[0] for b in parent_branches],
                                    format_func=lambda x: next(b[1] for b in parent_branches if b[0] == x))
            
            sub_branch_name = st.text_input("Sub-Branch Name", help="Name of the sub-branch")
            location = st.text_input("Location", help="Sub-branch location (city, address, etc.)")
            
            submitted = st.form_submit_button("Add Sub-Branch")
            if submitted:
                if not sub_branch_name:
                    st.error("Please enter a sub-branch name")
                else:
                    # Insert new sub-branch
                    try:
                        with engine.connect() as conn:
                            conn.execute(text('''
                            INSERT INTO branches (company_id, branch_name, branch_type, parent_branch_id, location, is_active)
                            VALUES (:company_id, :branch_name, 'Sub-Branch', :parent_branch_id, :location, TRUE)
                            '''), {
                                'company_id': company_id,
                                'branch_name': sub_branch_name,
                                'parent_branch_id': parent_branch_id,
                                'location': location
                            })
                            conn.commit()
                        st.success(f"Successfully added sub-branch: {sub_branch_name}")
                    except Exception as e:
                        st.error(f"Error adding sub-branch: {e}")
    
    # Edit branch form if selected
    if hasattr(st.session_state, 'edit_branch'):
        st.markdown('<h3 class="sub-header">Edit Branch</h3>', unsafe_allow_html=True)
        
        with st.form("edit_branch_form"):
            branch_name = st.text_input("Branch Name", value=st.session_state.edit_branch['name'])
            location = st.text_input("Location", value=st.session_state.edit_branch['location'])
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Update Branch")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submitted:
                if not branch_name:
                    st.error("Please enter a branch name")
                else:
                    with engine.connect() as conn:
                        conn.execute(text('''
                        UPDATE branches 
                        SET branch_name = :branch_name, location = :location
                        WHERE id = :id
                        '''), {
                            'branch_name': branch_name,
                            'location': location,
                            'id': st.session_state.edit_branch['id']
                        })
                        conn.commit()
                    st.success(f"Branch updated successfully")
                    del st.session_state.edit_branch
                    st.rerun()
            
            if cancel:
                del st.session_state.edit_branch
                st.rerun()

# Helper function to display a branch with its details and actions
def display_branch(branch, company_id):
    branch_id = branch[0]
    branch_name = branch[1]
    branch_type = branch[2]
    parent_branch = branch[3] or "None"
    location = branch[4] or "Not specified"
    created_at = branch[5].strftime('%d %b, %Y')
    is_active = branch[6]
    is_main = branch[7]
    
    with st.expander(f"{branch_name} ({branch_type})", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Branch Name:** {branch_name}")
            st.write(f"**Branch Type:** {branch_type}")
            if branch_type == "Sub-Branch":
                st.write(f"**Parent Branch:** {parent_branch}")
            st.write(f"**Location:** {location}")
        
        with col2:
            st.write(f"**Created:** {created_at}")
            st.write(f"**Status:** {'Active' if is_active else 'Inactive'}")
            
            # Display employee count
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT COUNT(*) FROM employees
                WHERE branch_id = :branch_id
                '''), {'branch_id': branch_id})
                employee_count = result.fetchone()[0]
            
            st.write(f"**Employees:** {employee_count}")
        
        # Display employees in this branch
        st.markdown("#### Branch Employees")
        
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, full_name, username, role, is_active
            FROM employees
            WHERE branch_id = :branch_id
            ORDER BY role, full_name
            '''), {'branch_id': branch_id})
            employees = result.fetchall()
        
        if not employees:
            st.info(f"No employees assigned to {branch_name}")
        else:
            employees_df = pd.DataFrame(
                [(e[1], e[2], e[3], "Active" if e[4] else "Inactive") for e in employees],
                columns=["Name", "Username", "Role", "Status"]
            )
            st.dataframe(employees_df, use_container_width=True)
        
        # Action buttons
        if not is_main:  # Don't allow deactivation of main branch
            col1, col2 = st.columns(2)
            with col1:
                if is_active:  # If active
                    if st.button(f"Deactivate Branch", key=f"deactivate_branch_{branch_id}"):
                        with engine.connect() as conn:
                            # Deactivate branch
                            conn.execute(text('UPDATE branches SET is_active = FALSE WHERE id = :id'), {'id': branch_id})
                            
                            # Cascade deactivation to sub-branches
                            conn.execute(text('''
                            UPDATE branches SET is_active = FALSE 
                            WHERE parent_branch_id = :branch_id AND company_id = :company_id
                            '''), {'branch_id': branch_id, 'company_id': company_id})
                            
                            # Cascade deactivation to employees
                            conn.execute(text('UPDATE employees SET is_active = FALSE WHERE branch_id = :branch_id'), 
                                      {'branch_id': branch_id})
                            
                            # Also deactivate employees in sub-branches
                            sub_branch_ids = conn.execute(text('''
                            SELECT id FROM branches WHERE parent_branch_id = :branch_id
                            '''), {'branch_id': branch_id}).fetchall()
                            
                            for sub_id in sub_branch_ids:
                                conn.execute(text('UPDATE employees SET is_active = FALSE WHERE branch_id = :branch_id'), 
                                          {'branch_id': sub_id[0]})
                            
                            conn.commit()
                        st.success(f"Deactivated branch: {branch_name} (including all sub-branches and employees)")
                        st.rerun()
                else:  # If inactive
                    if st.button(f"Activate Branch", key=f"activate_branch_{branch_id}"):
                        with engine.connect() as conn:
                            # Activate branch
                            conn.execute(text('UPDATE branches SET is_active = TRUE WHERE id = :id'), {'id': branch_id})
                            
                            # Cascade activation to sub-branches
                            conn.execute(text('''
                            UPDATE branches SET is_active = TRUE 
                            WHERE parent_branch_id = :branch_id AND company_id = :company_id
                            '''), {'branch_id': branch_id, 'company_id': company_id})
                            
                            # Cascade activation to employees
                            conn.execute(text('UPDATE employees SET is_active = TRUE WHERE branch_id = :branch_id'), 
                                      {'branch_id': branch_id})
                            
                            # Also activate employees in sub-branches
                            sub_branch_ids = conn.execute(text('''
                            SELECT id FROM branches WHERE parent_branch_id = :branch_id
                            '''), {'branch_id': branch_id}).fetchall()
                            
                            for sub_id in sub_branch_ids:
                                conn.execute(text('UPDATE employees SET is_active = TRUE WHERE branch_id = :branch_id'), 
                                          {'branch_id': sub_id[0]})
                            
                            conn.commit()
                        st.success(f"Activated branch: {branch_name} (including all sub-branches and employees)")
                        st.rerun()
            
            with col2:
                if st.button(f"Edit Branch", key=f"edit_branch_{branch_id}"):
                    st.session_state.edit_branch = {
                        'id': branch_id,
                        'name': branch_name,
                        'location': location if location != "Not specified" else ""
                    }
                    st.rerun()

# Manage Employees for Companies
def manage_company_employees():
    st.markdown('<h2 class="sub-header">Manage Employees</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    tab1, tab2, tab3 = st.tabs(["Employee List", "Add New Employee", "Update Employee Role"])
    
    with tab1:
        # Fetch and display all employees
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT e.id, e.username, e.full_name, e.profile_pic_url, e.is_active, 
                   b.branch_name, e.created_at, e.role, b.id as branch_id
            FROM employees e
            JOIN branches b ON e.branch_id = b.id
            WHERE b.company_id = :company_id
            ORDER BY e.role, e.full_name
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
                    ORDER BY branch_name
                    '''), {'company_id': company_id})
                    branches = result.fetchall()
                
                branch_options = ["All Branches"] + [branch[1] for branch in branches]
                branch_filter = st.selectbox("Filter by Branch", branch_options, key="employee_branch_filter")
            
            with col2:
                # Role filter
                role_options = ["All Roles", "Manager", "Asst. Manager", "General Employee"]
                role_filter = st.selectbox("Filter by Role", role_options, key="employee_role_filter")
            
            with col3:
                # Status filter
                status_options = ["All Employees", "Active", "Inactive"]
                status_filter = st.selectbox("Filter by Status", status_options, key="employee_status_filter")
            
            # Apply filters
            filtered_employees = employees
            if branch_filter != "All Branches":
                filtered_employees = [e for e in filtered_employees if e[5] == branch_filter]
            
            if role_filter != "All Roles":
                filtered_employees = [e for e in filtered_employees if e[7] == role_filter]
            
            if status_filter == "Active":
                filtered_employees = [e for e in filtered_employees if e[4]]
            elif status_filter == "Inactive":
                filtered_employees = [e for e in filtered_employees if not e[4]]
            
            st.write(f"Showing {len(filtered_employees)} of {len(employees)} employees")
            
            for employee in filtered_employees:
                employee_id = employee[0]
                username = employee[1]
                full_name = employee[2]
                profile_pic = employee[3] or "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
                is_active = employee[4]
                branch_name = employee[5]
                created_at = employee[6].strftime('%d %b, %Y')
                role = employee[7]
                branch_id = employee[8]
                
                with st.expander(f"{full_name} ({role})", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        try:
                            st.image(profile_pic, width=100, use_container_width=False)
                        except:
                            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
                    
                    with col2:
                        st.write(f"**Full Name:** {full_name}")
                        st.write(f"**Username:** {username}")
                        st.write(f"**Role:** {role}")
                        st.write(f"**Branch:** {branch_name}")
                        st.write(f"**Joined:** {created_at}")
                        st.write(f"**Status:** {'Active' if is_active else 'Inactive'}")
                        
                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if is_active:  # If active
                                if st.button(f"Deactivate", key=f"deactivate_employee_{employee_id}"):
                                    with engine.connect() as conn:
                                        conn.execute(text('UPDATE employees SET is_active = FALSE WHERE id = :id'), {'id': employee_id})
                                        conn.commit()
                                    st.success(f"Deactivated employee: {full_name}")
                                    st.rerun()
                            else:  # If inactive
                                if st.button(f"Activate", key=f"activate_employee_{employee_id}"):
                                    with engine.connect() as conn:
                                        conn.execute(text('UPDATE employees SET is_active = TRUE WHERE id = :id'), {'id': employee_id})
                                        conn.commit()
                                    st.success(f"Activated employee: {full_name}")
                                    st.rerun()
                        
                        with col2:
                            if st.button(f"Reset Password", key=f"reset_employee_{employee_id}"):
                                new_password = "password123"  # Default reset password
                                with engine.connect() as conn:
                                    conn.execute(text('UPDATE employees SET password = :password WHERE id = :id'), 
                                              {'id': employee_id, 'password': new_password})
                                    conn.commit()
                                st.success(f"Password reset to '{new_password}' for {full_name}")
                        
                        with col3:
                            if st.button(f"Transfer Employee", key=f"transfer_{employee_id}"):
                                st.session_state.transfer_employee = {
                                    'id': employee_id,
                                    'name': full_name,
                                    'current_branch_id': branch_id,
                                    'current_branch_name': branch_name
                                }
                                st.rerun()
    
    with tab2:
        # Form to add new employee
        with st.form("add_employee_form"):
            # Select branch
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT id, branch_name FROM branches 
                WHERE company_id = :company_id AND is_active = TRUE
                ORDER BY branch_name
                '''), {'company_id': company_id})
                branches = result.fetchall()
            
            if not branches:
                st.error("You need to create at least one active branch before adding employees")
                st.stop()
            
            branch_id = st.selectbox("Branch", 
                               options=[b[0] for b in branches],
                               format_func=lambda x: next(b[1] for b in branches if b[0] == x))
            
            # Role selection
            role = st.selectbox("Role", ["Manager", "Asst. Manager", "General Employee"])
            
            username = st.text_input("Username", help="Username for employee login")
            password = st.text_input("Password", type="password", help="Initial password")
            full_name = st.text_input("Full Name")
            profile_pic_url = st.text_input("Profile Picture URL", help="Link to employee profile picture")
            
            submitted = st.form_submit_button("Add Employee")
            if submitted:
                if not username or not password or not full_name:
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
                            # Insert new employee
                            try:
                                conn.execute(text('''
                                INSERT INTO employees (username, password, full_name, profile_pic_url, is_active, branch_id, role)
                                VALUES (:username, :password, :full_name, :profile_pic_url, TRUE, :branch_id, :role)
                                '''), {
                                    'username': username,
                                    'password': password,
                                    'full_name': full_name,
                                    'profile_pic_url': profile_pic_url,
                                    'branch_id': branch_id,
                                    'role': role
                                })
                                conn.commit()
                                st.success(f"Successfully added employee: {full_name}")
                            except Exception as e:
                                st.error(f"Error adding employee: {e}")
    
    with tab3:
        # Update employee role
        with st.form("update_role_form"):
            # Select employee
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT e.id, e.full_name, e.role, b.branch_name
                FROM employees e
                JOIN branches b ON e.branch_id = b.id
                WHERE b.company_id = :company_id AND e.is_active = TRUE
                ORDER BY e.full_name
                '''), {'company_id': company_id})
                role_employees = result.fetchall()
            
            if not role_employees:
                st.error("No active employees found")
                st.stop()
            
            employee_id = st.selectbox("Select Employee", 
                                 options=[e[0] for e in role_employees],
                                 format_func=lambda x: f"{next(e[1] for e in role_employees if e[0] == x)} - {next(e[3] for e in role_employees if e[0] == x)} ({next(e[2] for e in role_employees if e[0] == x)})")
            
            # Get current role
            current_role = next(e[2] for e in role_employees if e[0] == employee_id)
            st.write(f"Current Role: **{current_role}**")
            
            # New role
            new_role = st.selectbox("New Role", ["Manager", "Asst. Manager", "General Employee"])
            
            submitted = st.form_submit_button("Update Role")
            if submitted:
                if new_role == current_role:
                    st.info("No change in role")
                else:
                    with engine.connect() as conn:
                        conn.execute(text('UPDATE employees SET role = :role WHERE id = :id'), 
                                  {'id': employee_id, 'role': new_role})
                        conn.commit()
                    
                    employee_name = next(e[1] for e in role_employees if e[0] == employee_id)
                    st.success(f"Updated role for {employee_name} from {current_role} to {new_role}")
    
    # Transfer employee form if selected
    if hasattr(st.session_state, 'transfer_employee'):
        st.markdown(f'<h3 class="sub-header">Transfer {st.session_state.transfer_employee["name"]}</h3>', unsafe_allow_html=True)
        
        with st.form("transfer_employee_form"):
            st.write(f"Current Branch: **{st.session_state.transfer_employee['current_branch_name']}**")
            
            # Get branches for transfer
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT id, branch_name FROM branches 
                WHERE company_id = :company_id AND is_active = TRUE 
                AND id != :current_branch_id
                ORDER BY branch_name
                '''), {
                    'company_id': company_id,
                    'current_branch_id': st.session_state.transfer_employee['current_branch_id']
                })
                available_branches = result.fetchall()
            
            if not available_branches:
                st.error("No other active branches available for transfer")
                st.stop()
            
            new_branch_id = st.selectbox("Transfer to Branch", 
                                   options=[b[0] for b in available_branches],
                                   format_func=lambda x: next(b[1] for b in available_branches if b[0] == x))
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Transfer Employee")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submitted:
                with engine.connect() as conn:
                    conn.execute(text('UPDATE employees SET branch_id = :branch_id WHERE id = :id'), 
                              {'id': st.session_state.transfer_employee['id'], 'branch_id': new_branch_id})
                    conn.commit()
                
                new_branch_name = next(b[1] for b in available_branches if b[0] == new_branch_id)
                st.success(f"Transferred {st.session_state.transfer_employee['name']} from {st.session_state.transfer_employee['current_branch_name']} to {new_branch_name}")
                del st.session_state.transfer_employee
                st.rerun()
            
            if cancel:
                del st.session_state.transfer_employee
                st.rerun()

# View Company Reports
def view_company_reports():
    st.markdown('<h2 class="sub-header">Employee Reports</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Branch filter
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, branch_name FROM branches 
            WHERE company_id = :company_id
            ORDER BY branch_name
            '''), {'company_id': company_id})
            branches = result.fetchall()
        
        branch_options = ["All Branches"] + [branch[1] for branch in branches]
        branch_filter = st.selectbox("Select Branch", branch_options, key="company_reports_branch_filter")
        
        # If branch selected, get employees
        if branch_filter != "All Branches":
            selected_branch_id = next(b[0] for b in branches if b[1] == branch_filter)
            
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT id, full_name FROM employees 
                WHERE branch_id = :branch_id AND is_active = TRUE
                ORDER BY full_name
                '''), {'branch_id': selected_branch_id})
                employees = result.fetchall()
            
            employee_options = ["All Employees"] + [emp[1] for emp in employees]
            employee_filter = st.selectbox("Select Employee", employee_options, key="company_reports_employee_filter")
        else:
            employee_filter = "All Employees"
    
    with col2:
        # Role filter
        role_options = ["All Roles", "Manager", "Asst. Manager", "General Employee"]
        role_filter = st.selectbox("Select Role", role_options, key="company_reports_role_filter")
    
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
        date_filter = st.selectbox("Date Range", date_options, key="company_reports_date_filter")
        
        # Custom date range if selected
        if date_filter == "Custom Range":
            start_date = st.date_input("Start Date", today - datetime.timedelta(days=30))
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
    SELECT e.full_name, dr.report_date, dr.report_text, dr.id, e.id as employee_id, b.branch_name, e.role
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
        
        if employee_filter != "All Employees":
            query += ' AND e.full_name = :employee_name'
            params['employee_name'] = employee_filter
    
    if role_filter != "All Roles":
        query += ' AND e.role = :role'
        params['role'] = role_filter
    
    query += ' ORDER BY dr.report_date DESC, b.branch_name, e.role, e.full_name'
    
    # Execute query
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        reports = result.fetchall()
    
    # Display reports
    if not reports:
        st.info("No reports found for the selected criteria")
    else:
        st.write(f"Found {len(reports)} reports")
        
        # Add export button
        if len(reports) > 0:
            pdf = create_company_report_pdf(reports, start_date, end_date, branch_filter, role_filter)
            
            st.download_button(
                label="Export as PDF",
                data=pdf,
                file_name=f"employee_reports_{start_date}_to_{end_date}.pdf",
                mime="application/pdf"
            )
        
        # Group by branch for better organization
        reports_by_branch = {}
        for report in reports:
            branch_name = report[5]
            if branch_name not in reports_by_branch:
                reports_by_branch[branch_name] = {}
            
            role = report[6]
            if role not in reports_by_branch[branch_name]:
                reports_by_branch[branch_name][role] = {}
            
            employee_name = report[0]
            if employee_name not in reports_by_branch[branch_name][role]:
                reports_by_branch[branch_name][role][employee_name] = []
            
            reports_by_branch[branch_name][role][employee_name].append(report)
        
        # Display branches
        for branch_name, roles in reports_by_branch.items():
            with st.expander(f"Branch: {branch_name}", expanded=True):
                # Display roles
                for role, employees in roles.items():
                    st.markdown(f"### {role}s")
                    
                    # Display employees
                    for employee_name, emp_reports in employees.items():
                        with st.expander(f"Reports by {employee_name} ({len(emp_reports)})", expanded=False):
                            # Group by month/year for better organization
                            reports_by_period = {}
                            for report in emp_reports:
                                period = report[1].strftime('%B %Y')
                                if period not in reports_by_period:
                                    reports_by_period[period] = []
                                reports_by_period[period].append(report)
                            
                            for period, period_reports in reports_by_period.items():
                                st.markdown(f"##### {period}")
                                for report in period_reports:
                                    st.markdown(f'''
                                    <div class="report-item">
                                        <span style="color: #777;">{report[1].strftime('%A, %d %b %Y')}</span>
                                        <p>{report[2]}</p>
                                    </div>
                                    ''', unsafe_allow_html=True)

# Create PDF for company reports with filters
def create_company_report_pdf(reports, start_date, end_date, branch_filter, role_filter):
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
    
    # Create title based on filters
    title = "Employee Reports"
    if branch_filter != "All Branches":
        title += f" - {branch_filter}"
    if role_filter != "All Roles":
        title += f" - {role_filter}s"
    
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Date range
    date_style = ParagraphStyle(
        'DateRange',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.gray
    )
    
    date_range = f"Period: {start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
    elements.append(Paragraph(date_range, date_style))
    elements.append(Spacer(1, 20))
    
    # Group reports by branch, role, and employee
    reports_by_branch = {}
    for report in reports:
        employee_name = report[0]
        report_date = report[1]
        report_text = report[2]
        branch_name = report[5]
        role = report[6]
        
        if branch_name not in reports_by_branch:
            reports_by_branch[branch_name] = {}
        
        if role not in reports_by_branch[branch_name]:
            reports_by_branch[branch_name][role] = {}
        
        if employee_name not in reports_by_branch[branch_name][role]:
            reports_by_branch[branch_name][role][employee_name] = []
        
        reports_by_branch[branch_name][role][employee_name].append((report_date, report_text))
    
    # Add each branch's reports
    for branch_name, roles in reports_by_branch.items():
        # Branch header
        branch_style = ParagraphStyle(
            'Branch',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        )
        elements.append(Paragraph(f"Branch: {branch_name}", branch_style))
        
        # Add each role's reports
        for role, employees in roles.items():
            # Role header
            role_style = ParagraphStyle(
                'Role',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=8
            )
            elements.append(Paragraph(f"{role}s", role_style))
            
            # Add each employee's reports
            for employee_name, emp_reports in employees.items():
                # Employee header
                employee_style = ParagraphStyle(
                    'Employee',
                    parent=styles['Heading4'],
                    fontSize=11,
                    spaceAfter=6
                )
                elements.append(Paragraph(employee_name, employee_style))
                
                # Sort reports by date
                emp_reports.sort(key=lambda x: x[0], reverse=True)
                
                # Group by month for better organization
                reports_by_month = {}
                for report_date, report_text in emp_reports:
                    month_year = report_date.strftime('%B %Y')
                    if month_year not in reports_by_month:
                        reports_by_month[month_year] = []
                    reports_by_month[month_year].append((report_date, report_text))
                
                # Add each month's reports
                for month, month_reports in reports_by_month.items():
                    # Month header
                    month_style = ParagraphStyle(
                        'Month',
                        parent=styles['Normal'],
                        fontSize=10,
                        textColor=colors.blue,
                        spaceBefore=8,
                        spaceAfter=4
                    )
                    elements.append(Paragraph(month, month_style))
                    
                    # Reports for the month
                    for report_date, report_text in month_reports:
                        # Date
                        date_style = ParagraphStyle(
                            'Date',
                            parent=styles['Normal'],
                            fontSize=9,
                            textColor=colors.gray
                        )
                        elements.append(Paragraph(report_date.strftime('%A, %d %b %Y'), date_style))
                        
                        # Report text
                        text_style = ParagraphStyle(
                            'ReportText',
                            parent=styles['Normal'],
                            fontSize=9,
                            leftIndent=20,
                            spaceBefore=2,
                            spaceAfter=10
                        )
                        elements.append(Paragraph(report_text, text_style))
                
                elements.append(Spacer(1, 10))
            
            elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("", styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# View Company Messages
def view_company_messages():
    st.markdown('<h2 class="sub-header">Messages from Admin</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Fetch all messages
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT id, message_text, created_at, is_read
        FROM company_messages
        WHERE company_id = :company_id
        ORDER BY created_at DESC
        '''), {'company_id': company_id})
        messages = result.fetchall()
    
    if not messages:
        st.info("No messages received yet")
    else:
        # Mark unread messages as read when viewed
        unread_message_ids = [msg[0] for msg in messages if not msg[3]]
        if unread_message_ids:
            with engine.connect() as conn:
                for msg_id in unread_message_ids:
                    conn.execute(text('UPDATE company_messages SET is_read = TRUE WHERE id = :id'), {'id': msg_id})
                conn.commit()
        
        st.write(f"Total messages: {len(messages)}")
        
        for msg in messages:
            msg_id = msg[0]
            msg_text = msg[1]
            created_at = msg[2].strftime('%d %b %Y, %H:%M')
            was_unread = not msg[3]
            
            # Add a "new" badge for messages that were unread
            badge_html = '<span style="background-color: #1E88E5; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.7rem; margin-left: 10px;">New</span>' if was_unread else ''
            
            st.markdown(f'''
            <div class="message-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #777;">{created_at}</span>
                    {badge_html}
                </div>
                <p style="margin-top: 0.5rem;">{msg_text}</p>
            </div>
            ''', unsafe_allow_html=True)

# Edit Company Profile
def edit_company_profile():
    st.markdown('<h2 class="sub-header">Company Profile</h2>', unsafe_allow_html=True)
    
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
            st.image(current_pic_url or "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=150, use_container_width=False)
        except:
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=150, use_container_width=False)
    
    with col2:
        st.markdown(f"<p><strong>Username:</strong> {username}</p>", unsafe_allow_html=True)
        st.info("Username cannot be changed as it is used for login purposes.")
    
    # Form for updating profile
    with st.form("update_company_profile_form"):
        st.subheader("Update Company Information")
        
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
            if new_company_name != current_company_name or new_profile_pic_url != (current_pic_url or ""):
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
                st.success("Company information updated successfully.")
            
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
                st.rerun()

# View Detailed Task Tracking
def view_task_tracking():
    st.markdown('<h2 class="sub-header">Task Tracking Dashboard</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Branch filter
        with engine.connect() as conn:
            result = conn.execute(text('''
            SELECT id, branch_name FROM branches 
            WHERE company_id = :company_id AND is_active = TRUE
            ORDER BY branch_name
            '''), {'company_id': company_id})
            branches = result.fetchall()
        
        branch_options = ["All Branches"] + [branch[1] for branch in branches]
        branch_filter = st.selectbox("Filter by Branch", branch_options, key="track_branch_filter")
    
    with col2:
        # Status filter
        status_options = ["All Tasks", "Pending", "Completed"]
        status_filter = st.selectbox("Filter by Status", status_options, key="track_status_filter")
    
    # Query for branch tasks with employee completion status
    query = '''
    SELECT 
        t.id, t.task_description, t.due_date, t.is_completed, 
        b.branch_name, t.created_at, t.branch_id,
        (SELECT COUNT(*) FROM task_assignments ta WHERE ta.task_id = t.id) as total_assignments,
        (SELECT COUNT(*) FROM task_assignments ta WHERE ta.task_id = t.id AND ta.is_completed = TRUE) as completed_assignments
    FROM tasks t
    JOIN branches b ON t.branch_id = b.id
    WHERE b.company_id = :company_id AND t.employee_id IS NULL
    '''
    
    params = {'company_id': company_id}
    
    if branch_filter != "All Branches":
        query += ' AND b.branch_name = :branch_name'
        params['branch_name'] = branch_filter
    
    if status_filter == "Pending":
        query += ' AND t.is_completed = FALSE'
    elif status_filter == "Completed":
        query += ' AND t.is_completed = TRUE'
    
    query += ' ORDER BY t.due_date ASC NULLS LAST, t.created_at DESC'
    
    # Execute query
    with engine.connect() as conn:
        result = conn.execute(text(query), params)
        branch_tasks = result.fetchall()
    
    # Display branch tasks with detailed employee completion tracking
    if branch_tasks:
        st.markdown("### Branch Task Progress")
        
        # Group tasks by branch
        tasks_by_branch = {}
        for task in branch_tasks:
            branch_name = task[4]
            if branch_name not in tasks_by_branch:
                tasks_by_branch[branch_name] = []
            tasks_by_branch[branch_name].append(task)
        
        # Display tasks by branch
        for branch_name, branch_task_list in tasks_by_branch.items():
            with st.expander(f"Tasks for {branch_name} ({len(branch_task_list)})", expanded=True):
                for task in branch_task_list:
                    task_id = task[0]
                    task_description = task[1]
                    due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                    is_completed = task[3]
                    created_at = task[5].strftime('%d %b, %Y')
                    branch_id = task[6]
                    total_assignments = task[7]
                    completed_assignments = task[8]
                    
                    # Calculate completion percentage
                    completion_percentage = 0 if total_assignments == 0 else int((completed_assignments / total_assignments) * 100)
                    
                    # Display progress bar color based on completion
                    if completion_percentage == 100:
                        progress_color = "bg-success"
                    elif completion_percentage >= 75:
                        progress_color = "bg-info"
                    elif completion_percentage >= 50:
                        progress_color = "bg-warning"
                    else:
                        progress_color = "bg-danger"
                    
                    # Create progress bar HTML
                    progress_bar = f'''
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar {progress_color}" role="progressbar" 
                             style="width: {completion_percentage}%;" 
                             aria-valuenow="{completion_percentage}" aria-valuemin="0" aria-valuemax="100">
                            {completion_percentage}%
                        </div>
                    </div>
                    '''
                    
                    # Display the task with status-based styling
                    status_class = "completed" if is_completed else ""
                    status_tag = f'<span class="badge bg-success">Completed</span>' if is_completed else f'<span class="badge bg-warning">In Progress</span>'
                    
                    st.markdown(f'''
                    <div class="task-item {status_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <strong>Due: {due_date}</strong>
                            {status_tag}
                        </div>
                        <p>{task_description}</p>
                        <p><strong>Progress:</strong> {completed_assignments} of {total_assignments} employees completed</p>
                        {progress_bar}
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                            <span style="color: #777; font-size: 0.8rem;">Created: {created_at}</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Show employee completion details
                    with st.expander("View Employee Completion Details"):
                        # Get employee completion details
                        with engine.connect() as conn:
                            result = conn.execute(text('''
                            SELECT e.full_name, e.role, ta.is_completed, 
                                   ta.completed_at
                            FROM task_assignments ta
                            JOIN employees e ON ta.employee_id = e.id
                            WHERE ta.task_id = :task_id
                            ORDER BY e.role, e.full_name
                            '''), {'task_id': task_id})
                            employee_completion = result.fetchall()
                        
                        if employee_completion:
                            # Create a dataframe for display
                            completion_data = []
                            for emp in employee_completion:
                                completion_data.append({
                                    'Employee': emp[0],
                                    'Role': emp[1],
                                    'Status': 'Completed' if emp[2] else 'Pending',
                                    'Completed On': emp[3].strftime('%d %b, %Y %H:%M') if emp[3] else 'N/A'
                                })
                            
                            completion_df = pd.DataFrame(completion_data)
                            st.dataframe(completion_df, use_container_width=True)
                        else:
                            st.info("No employee assignment details found")
                    
                    # Action buttons for task management
                    if not is_completed:
                        if st.button(f"Mark as Completed (Override)", key=f"track_complete_{task_id}"):
                            with engine.connect() as conn:
                                conn.execute(text('''
                                UPDATE tasks 
                                SET is_completed = TRUE, completed_by_id = :company_id 
                                WHERE id = :id
                                '''), {'id': task_id, 'company_id': company_id})
                                
                                conn.execute(text('''
                                UPDATE task_assignments 
                                SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP 
                                WHERE task_id = :task_id AND is_completed = FALSE
                                '''), {'task_id': task_id})
                                
                                conn.commit()
                            st.success("Task marked as completed for all employees")
                            st.rerun()
    else:
        st.info("No branch tasks found for the selected criteria")
    
    # Add to Company Dashboard
    st.markdown('''
    <script>
    // Add custom CSS for badges and progress bars
    const style = document.createElement('style');
    style.textContent = `
        .badge {
            display: inline-block;
            padding: 0.25em 0.4em;
            font-size: 75%;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.25rem;
            color: white;
        }
        .bg-success {
            background-color: #28a745!important;
        }
        .bg-warning {
            background-color: #ffc107!important;
            color: black;
        }
        .bg-info {
            background-color: #17a2b8!important;
        }
        .bg-danger {
            background-color: #dc3545!important;
        }
        .progress {
            display: flex;
            height: 1rem;
            overflow: hidden;
            font-size: .75rem;
            background-color: #e9ecef;
            border-radius: 0.25rem;
            margin: 10px 0;
        }
        .progress-bar {
            display: flex;
            flex-direction: column;
            justify-content: center;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            transition: width .6s ease;
        }
    `;
    document.head.appendChild(style);
    </script>
    ''', unsafe_allow_html=True)# Manage Tasks for Companies
def manage_company_tasks():
    st.markdown('<h2 class="sub-header">Manage Tasks</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    tab1, tab2 = st.tabs(["View Tasks", "Assign New Task"])
    
    with tab1:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Branch filter
            with engine.connect() as conn:
                result = conn.execute(text('''
                SELECT id, branch_name FROM branches 
                WHERE company_id = :company_id
                ORDER BY branch_name
                '''), {'company_id': company_id})
                branches = result.fetchall()
            
            branch_options = ["All Branches"] + [branch[1] for branch in branches]
            branch_filter = st.selectbox("Select Branch", branch_options, key="task_branch_filter")
            
            # If branch selected, get employees
            if branch_filter != "All Branches":
                selected_branch_id = next(branch[0] for branch in branches if branch[1] == branch_filter)
                
                with engine.connect() as conn:
                    result = conn.execute(text('''
                    SELECT id, full_name FROM employees 
                    WHERE branch_id = :branch_id AND is_active = TRUE
                    ORDER BY full_name
                    '''), {'branch_id': selected_branch_id})
                    employees = result.fetchall()
                
                employee_options = ["All Employees"] + [emp[1] for emp in employees]
                employee_filter = st.selectbox("Select Employee", employee_options, key="task_employee_filter")
            else:
                employee_filter = "All Employees"
        
        with col2:
            # Assignment type filter
            assignment_options = ["All Tasks", "Branch Tasks", "Individual Tasks"]
            assignment_filter = st.selectbox("Assignment Type", assignment_options, key="task_assignment_filter")
        
        with col3:
            # Status filter
            status_options = ["All Tasks", "Pending", "Completed"]
            status_filter = st.selectbox("Task Status", status_options, key="admin_task_status_filter")
        
        # Build query based on filters
        if branch_filter == "All Branches" and assignment_filter != "Individual Tasks":
            # Query for all branches including branch assignments
            query = '''
            SELECT t.id, t.task_description, t.due_date, t.is_completed, t.created_at, 
                   b.branch_name, e.full_name as employee_name, t.branch_id, t.employee_id, 
                   c.full_name as completed_by
            FROM tasks t
            LEFT JOIN branches b ON t.branch_id = b.id
            LEFT JOIN employees e ON t.employee_id = e.id
            LEFT JOIN employees c ON t.completed_by_id = c.id
            WHERE b.company_id = :company_id
            '''
            params = {'company_id': company_id}
        elif branch_filter != "All Branches" and assignment_filter != "Individual Tasks":
            # Query for specific branch including branch assignments
            query = '''
            SELECT t.id, t.task_description, t.due_date, t.is_completed, t.created_at, 
                   b.branch_name, e.full_name as employee_name, t.branch_id, t.employee_id,
                   c.full_name as completed_by
            FROM tasks t
            LEFT JOIN branches b ON t.branch_id = b.id
            LEFT JOIN employees e ON t.employee_id = e.id
            LEFT JOIN employees c ON t.completed_by_id = c.id
            WHERE b.branch_name = :branch_name AND b.company_id = :company_id
            '''
            params = {'branch_name': branch_filter, 'company_id': company_id}
        elif assignment_filter == "Branch Tasks":
            # Only branch tasks
            query = '''
            SELECT t.id, t.task_description, t.due_date, t.is_completed, t.created_at, 
                   b.branch_name, NULL as employee_name, t.branch_id, t.employee_id,
                   c.full_name as completed_by
            FROM tasks t
            JOIN branches b ON t.branch_id = b.id
            LEFT JOIN employees c ON t.completed_by_id = c.id
            WHERE b.company_id = :company_id AND t.employee_id IS NULL
            '''
            params = {'company_id': company_id}
            
            if branch_filter != "All Branches":
                query += ' AND b.branch_name = :branch_name'
                params['branch_name'] = branch_filter
        else:
            # Individual employee tasks
            query = '''
            SELECT t.id, t.task_description, t.due_date, t.is_completed, t.created_at, 
                   b.branch_name, e.full_name as employee_name, t.branch_id, t.employee_id,
                   c.full_name as completed_by
            FROM tasks t
            JOIN employees e ON t.employee_id = e.id
            JOIN branches b ON e.branch_id = b.id
            LEFT JOIN employees c ON t.completed_by_id = c.id
            WHERE b.company_id = :company_id
            '''
            params = {'company_id': company_id}
            
            if branch_filter != "All Branches":
                query += ' AND b.branch_name = :branch_name'
                params['branch_name'] = branch_filter
                
                if employee_filter != "All Employees":
                    query += ' AND e.full_name = :employee_name'
                    params['employee_name'] = employee_filter
        
        # Add status filter
        if status_filter == "Pending":
            query += ' AND t.is_completed = FALSE'
        elif status_filter == "Completed":
            query += ' AND t.is_completed = TRUE'
        
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
            
            # Group tasks by branch
            tasks_by_branch = {}
            for task in tasks:
                branch_name = task[5] if task[5] else "Unassigned"
                
                if branch_name not in tasks_by_branch:
                    tasks_by_branch[branch_name] = []
                
                tasks_by_branch[branch_name].append(task)
            
            # Display tasks by branch
            for branch_name, branch_tasks in tasks_by_branch.items():
                with st.expander(f"Tasks for {branch_name} ({len(branch_tasks)})", expanded=True):
                    for task in branch_tasks:
                        task_id = task[0]
                        task_description = task[1]
                        due_date = task[2].strftime('%d %b, %Y') if task[2] else "No due date"
                        is_completed = task[3]
                        created_at = task[4].strftime('%d %b, %Y')
                        employee_name = task[6] if task[6] else "Entire Branch"
                        branch_id = task[7]
                        employee_id = task[8]
                        completed_by = task[9] if task[9] else ""
                        
                        # Display task type and assignee
                        task_type = "Branch Task" if employee_name == "Entire Branch" else "Individual Task"
                        assignee = branch_name if employee_name == "Entire Branch" else employee_name
                        
                        # Display the task with status-based styling
                        status_class = "completed" if is_completed else ""
                        completion_info = f"<br><span style='color: #777;'>Completed by: {completed_by}</span>" if is_completed and completed_by else ""
                        
                        st.markdown(f'''
                        <div class="task-item {status_class}">
                            <strong>{task_type} for {assignee}</strong> - Due: {due_date}
                            <p>{task_description}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #777; font-size: 0.8rem;">Created: {created_at}</span>
                                <span style="font-weight: 600; color: {'#9e9e9e' if is_completed else '#4CAF50'};">
                                    {"Completed" if is_completed else "Pending"}
                                </span>
                            </div>
                            {completion_info}
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        # Action buttons
                        if not is_completed:
                            # For branch tasks, check completion status of all employees
                            if employee_name == "Entire Branch":
                                with engine.connect() as conn:
                                    result = conn.execute(text('''
                                    SELECT COUNT(*) FROM task_assignments
                                    WHERE task_id = :task_id AND is_completed = FALSE
                                    '''), {'task_id': task_id})
                                    incomplete_count = result.fetchone()[0]
                                
                                if incomplete_count > 0:
                                    st.info(f"{incomplete_count} employees still need to complete this task")
                                
                                # Show completion button for manager override
                                if st.button(f"Mark as Completed (Override)", key=f"complete_override_{task_id}"):
                                    with engine.connect() as conn:
                                        # Get manager ID (using company user as override)
                                        conn.execute(text('''
                                        UPDATE tasks 
                                        SET is_completed = TRUE, completed_by_id = :company_id 
                                        WHERE id = :id
                                        '''), {'id': task_id, 'company_id': company_id})
                                        
                                        # Mark all assignments as completed
                                        conn.execute(text('''
                                        UPDATE task_assignments 
                                        SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP 
                                        WHERE task_id = :task_id
                                        '''), {'task_id': task_id})
                                        
                                        conn.commit()
                                    st.success("Task marked as completed (managerial override)")
                                    st.rerun()
                            else:
                                # Individual task
                                if st.button(f"Mark as Completed", key=f"complete_task_{task_id}"):
                                    with engine.connect() as conn:
                                        conn.execute(text('''
                                        UPDATE tasks 
                                        SET is_completed = TRUE, completed_by_id = :company_id 
                                        WHERE id = :id
                                        '''), {'id': task_id, 'company_id': company_id})
                                        conn.commit()
                                    st.success("Task marked as completed")
                                    st.rerun()
                        else:
                            # Reopen completed task
                            if st.button(f"Reopen Task", key=f"reopen_{task_id}"):
                                with engine.connect() as conn:
                                    conn.execute(text('''
                                    UPDATE tasks 
                                    SET is_completed = FALSE, completed_by_id = NULL 
                                    WHERE id = :id
                                    '''), {'id': task_id})
                                    
                                    # If it's a branch task, also reopen the assignments
                                    if employee_name == "Entire Branch":
                                        conn.execute(text('''
                                        UPDATE task_assignments 
                                        SET is_completed = FALSE, completed_at = NULL
                                        WHERE task_id = :task_id
                                        '''), {'task_id': task_id})
                                    
                                    conn.commit()
                                st.success("Task reopened")
                                st.rerun()
                        
                        if st.button(f"Delete Task", key=f"delete_{task_id}"):
                            with engine.connect() as conn:
                                # Delete task assignments first
                                conn.execute(text('DELETE FROM task_assignments WHERE task_id = :id'), {'id': task_id})
                                # Then delete the task
                                conn.execute(text('DELETE FROM tasks WHERE id = :id'), {'id': task_id})
                                conn.commit()
                            st.success("Task deleted")
                            st.rerun()
    
    with tab2:
        # Form to assign new task
        with st.form("assign_task_form"):
            # Task assignment type
            assignment_type = st.radio("Assign Task To:", ["Branch", "Individual Employee"])
            
            if assignment_type == "Branch":
                # Branch selection for branch tasks
                with engine.connect() as conn:
                    result = conn.execute(text('''
                    SELECT id, branch_name FROM branches 
                    WHERE company_id = :company_id AND is_active = TRUE
                    ORDER BY branch_name
                    '''), {'company_id': company_id})
                    branches = result.fetchall()
                
                if not branches:
                    st.error("No active branches available")
                    st.stop()
                
                branch_id = st.selectbox("Assign to Branch", 
                                options=[b[0] for b in branches],
                                format_func=lambda x: next(b[1] for b in branches if b[0] == x))
                
                employee_id = None
            else:
                # Branch selection first to filter employees
                with engine.connect() as conn:
                    result = conn.execute(text('''
                    SELECT id, branch_name FROM branches 
                    WHERE company_id = :company_id AND is_active = TRUE
                    ORDER BY branch_name
                    '''), {'company_id': company_id})
                    branches = result.fetchall()
                
                if not branches:
                    st.error("No active branches available")
                    st.stop()
                
                branch_id_for_emp = st.selectbox("Employee's Branch", 
                                       options=[b[0] for b in branches],
                                       format_func=lambda x: next(b[1] for b in branches if b[0] == x))
                
                # Then employee selection
                with engine.connect() as conn:
                    result = conn.execute(text('''
                    SELECT id, full_name, role FROM employees 
                    WHERE branch_id = :branch_id AND is_active = TRUE
                    ORDER BY role, full_name
                    '''), {'branch_id': branch_id_for_emp})
                    employees = result.fetchall()
                
                if not employees:
                    st.error(f"No active employees in the selected branch")
                    st.stop()
                
                employee_id = st.selectbox("Assign to Employee", 
                                    options=[e[0] for e in employees],
                                    format_func=lambda x: f"{next(e[1] for e in employees if e[0] == x)} ({next(e[2] for e in employees if e[0] == x)})")
                
                branch_id = None
            
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
                            # Begin transaction
                            if assignment_type == "Branch":
                                # Create branch task
                                result = conn.execute(text('''
                                INSERT INTO tasks (branch_id, task_description, due_date, is_completed)
                                VALUES (:branch_id, :task_description, :due_date, FALSE)
                                RETURNING id
                                '''), {
                                    'branch_id': branch_id,
                                    'task_description': task_description,
                                    'due_date': due_date
                                })
                                task_id = result.fetchone()[0]
                                
                                # Create task assignments for all active employees in the branch
                                employee_ids = conn.execute(text('''
                                SELECT id FROM employees
                                WHERE branch_id = :branch_id AND is_active = TRUE
                                '''), {'branch_id': branch_id}).fetchall()
                                
                                for emp_id in employee_ids:
                                    conn.execute(text('''
                                    INSERT INTO task_assignments (task_id, employee_id, is_completed)
                                    VALUES (:task_id, :employee_id, FALSE)
                                    '''), {'task_id': task_id, 'employee_id': emp_id[0]})
                                
                                branch_name = next(b[1] for b in branches if b[0] == branch_id)
                                success_message = f"Task assigned to {branch_name} branch ({len(employee_ids)} employees)"
                            else:
                                # Create individual task
                                conn.execute(text('''
                                INSERT INTO tasks (employee_id, task_description, due_date, is_completed)
                                VALUES (:employee_id, :task_description, :due_date, FALSE)
                                '''), {
                                    'employee_id': employee_id,
                                    'task_description': task_description,
                                    'due_date': due_date
                                })
                                
                                employee_name = next(e[1] for e in employees if e[0] == employee_id)
                                success_message = f"Task assigned to {employee_name}"
                            
                            conn.commit()
                        st.success(success_message)
                    except Exception as e:
                        st.error(f"Error assigning task: {e}")

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
            if st.session_state.user.get("is_admin", False):
                admin_dashboard()
            elif st.session_state.user.get("is_company", False):
                company_dashboard()
            else:
                employee_dashboard()  # The original employee dashboard
    else:
        st.error("Failed to connect to the database. Please check your database configuration.")

if __name__ == "__main__":
    main()
