import streamlit as st
from sqlalchemy import text
from database.models import EmployeeModel, BranchModel

def manage_employees(engine):
    """Manage employees - listing, adding, deactivating.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h2 class="sub-header">Manage Employees</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    tab1, tab2 = st.tabs(["Employee List", "Add New Employee"])
    
    with tab1:
        display_employee_list(engine, company_id)
    
    with tab2:
        add_new_employee(engine, company_id)

def display_employee_list(engine, company_id):
    """Display the list of employees for this company's branches.
    
    Args:
        engine: SQLAlchemy database engine
        company_id: ID of the current company
    """
    # Get all employees for this company's branches
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT e.id, e.username, e.full_name, e.profile_pic_url, e.is_active, 
               b.branch_name, b.id as branch_id
        FROM employees e
        JOIN branches b ON e.branch_id = b.id
        WHERE b.company_id = :company_id
        ORDER BY b.branch_name, e.full_name
        '''), {'company_id': company_id})
        employees = result.fetchall()
    
    if not employees:
        st.info("No employees found. Add employees using the 'Add New Employee' tab.")
    else:
        st.write(f"Total employees: {len(employees)}")
        
        # Group employees by branch
        employees_by_branch = {}
        for employee in employees:
            branch_name = employee[5]
            if branch_name not in employees_by_branch:
                employees_by_branch[branch_name] = []
            employees_by_branch[branch_name].append(employee)
        
        # Display employees by branch
        for branch_name, branch_employees in employees_by_branch.items():
            st.markdown(f'<h3 class="sub-header">{branch_name}</h3>', unsafe_allow_html=True)
            
            for employee in branch_employees:
                employee_id = employee[0]
                username = employee[1]
                full_name = employee[2]
                profile_pic_url = employee[3]
                is_active = employee[4]
                
                with st.expander(f"{full_name} ({username})", expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        try:
                            st.image(profile_pic_url, width=100, use_container_width=False)
                        except:
                            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", width=100)
                    
                    with col2:
                        st.write(f"**Username:** {username}")
                        st.write(f"**Full Name:** {full_name}")
                        st.write(f"**Branch:** {branch_name}")
                        st.write(f"**Status:** {'Active' if is_active else 'Inactive'}")
                        
                        # Action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if is_active:  # If active
                                if st.button(f"Deactivate", key=f"deactivate_emp_{employee_id}"):
                                    with engine.connect() as conn:
                                        EmployeeModel.update_employee_status(conn, employee_id, False)
                                    st.success(f"Deactivated employee: {full_name}")
                                    st.rerun()
                            else:  # If inactive
                                if st.button(f"Activate", key=f"activate_emp_{employee_id}"):
                                    with engine.connect() as conn:
                                        EmployeeModel.update_employee_status(conn, employee_id, True)
                                    st.success(f"Activated employee: {full_name}")
                                    st.rerun()
                        
                        with col2:
                            if st.button(f"Reset Password", key=f"reset_emp_{employee_id}"):
                                new_password = "employee123"  # Default reset password
                                with engine.connect() as conn:
                                    EmployeeModel.reset_password(conn, employee_id, new_password)
                                st.success(f"Password reset to '{new_password}' for {full_name}")

def add_new_employee(engine, company_id):
    """Form to add a new employee.
    
    Args:
        engine: SQLAlchemy database engine
        company_id: ID of the current company
    """
    # Get active branches for this company
    with engine.connect() as conn:
        branches = BranchModel.get_active_branches(conn, company_id)
    
    if not branches:
        st.warning("No active branches found. Please add and activate branches first.")
        return
    
    # Create branch selection dictionary
    branch_options = {branch[1]: branch[0] for branch in branches}
    
    with st.form("add_employee_form"):
        st.subheader("Employee Details")
        
        selected_branch = st.selectbox("Select Branch", list(branch_options.keys()))
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
                        # Get branch ID from selection
                        branch_id = branch_options[selected_branch]
                        
                        # Insert new employee
                        try:
                            with engine.connect() as conn:
                                EmployeeModel.add_employee(
                                    conn, 
                                    branch_id, 
                                    username, 
                                    password, 
                                    full_name, 
                                    profile_pic_url
                                )
                            st.success(f"Successfully added employee: {full_name}")
                        except Exception as e:
                            st.error(f"Error adding employee: {e}")
