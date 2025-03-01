import streamlit as st
from sqlalchemy import text
from database.models import BranchModel

def manage_branches(engine):
    """Manage branches - listing and adding.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h2 class="sub-header">Manage Branches</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    tab1, tab2 = st.tabs(["Branch List", "Add New Branch"])
    
    with tab1:
        display_branch_list(engine, company_id)
    
    with tab2:
        add_new_branch(engine, company_id)

def display_branch_list(engine, company_id):
    """Display the list of branches for this company.
    
    Args:
        engine: SQLAlchemy database engine
        company_id: ID of the current company
    """
    # Fetch and display branches
    with engine.connect() as conn:
        branches = BranchModel.get_company_branches(conn, company_id)
    
    if not branches:
        st.info("No branches found. Add branches using the 'Add New Branch' tab.")
    else:
        st.write(f"Total branches: {len(branches)}")
        
        for branch in branches:
            branch_id = branch[0]
            branch_name = branch[1]
            location = branch[2] or "No location specified"
            branch_head = branch[3] or "No head assigned"
            is_active = branch[4]
            
            with st.expander(f"{branch_name}", expanded=False):
                st.write(f"**Location:** {location}")
                st.write(f"**Branch Head:** {branch_head}")
                st.write(f"**Status:** {'Active' if is_active else 'Inactive'}")
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"Edit Branch", key=f"edit_branch_{branch_id}"):
                        st.session_state.edit_branch = {
                            'id': branch_id,
                            'name': branch_name,
                            'location': location if location != "No location specified" else "",
                            'head': branch_head if branch_head != "No head assigned" else ""
                        }
                        st.rerun()
                
                with col2:
                    if is_active:
                        if st.button(f"Deactivate", key=f"deactivate_branch_{branch_id}"):
                            update_branch_status(engine, branch_id, False)
                            st.success(f"Deactivated branch: {branch_name}")
                            st.rerun()
                    else:
                        if st.button(f"Activate", key=f"activate_branch_{branch_id}"):
                            update_branch_status(engine, branch_id, True)
                            st.success(f"Activated branch: {branch_name}")
                            st.rerun()
    
    # Edit branch form if branch is selected for editing
    if hasattr(st.session_state, 'edit_branch'):
        edit_branch(engine)

def edit_branch(engine):
    """Edit a branch.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h3 class="sub-header">Edit Branch</h3>', unsafe_allow_html=True)
    
    with st.form("edit_branch_form"):
        branch_name = st.text_input("Branch Name", value=st.session_state.edit_branch['name'])
        location = st.text_input("Location", value=st.session_state.edit_branch['location'])
        branch_head = st.text_input("Branch Head", value=st.session_state.edit_branch['head'])
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Update Branch")
        with col2:
            canceled = st.form_submit_button("Cancel")
        
        if submitted:
            if not branch_name:
                st.error("Branch name is required")
            else:
                # Update branch details
                try:
                    update_branch(engine, st.session_state.edit_branch['id'], branch_name, location, branch_head)
                    st.success(f"Branch updated successfully: {branch_name}")
                    del st.session_state.edit_branch
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating branch: {e}")
        
        if canceled:
            del st.session_state.edit_branch
            st.rerun()

def add_new_branch(engine, company_id):
    """Form to add a new branch.
    
    Args:
        engine: SQLAlchemy database engine
        company_id: ID of the current company
    """
    with st.form("add_branch_form"):
        branch_name = st.text_input("Branch Name", help="Name of the branch")
        location = st.text_input("Location", help="Physical location of the branch")
        branch_head = st.text_input("Branch Head", help="Name of the person heading the branch")
        
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
                    st.error(f"Branch with name '{branch_name}' already exists for your company")
                else:
                    # Insert new branch
                    try:
                        add_branch(engine, company_id, branch_name, location, branch_head)
                        st.success(f"Successfully added branch: {branch_name}")
                    except Exception as e:
                        st.error(f"Error adding branch: {e}")

def add_branch(engine, company_id, branch_name, location, branch_head):
    """Add a new branch to the database.
    
    Args:
        engine: SQLAlchemy database engine
        company_id: ID of the company
        branch_name: Name of the branch
        location: Location of the branch
        branch_head: Head of the branch
    """
    with engine.connect() as conn:
        conn.execute(text('''
        INSERT INTO branches (company_id, branch_name, location, branch_head, is_active)
        VALUES (:company_id, :branch_name, :location, :branch_head, TRUE)
        '''), {
            'company_id': company_id,
            'branch_name': branch_name,
            'location': location,
            'branch_head': branch_head
        })
        conn.commit()

def update_branch(engine, branch_id, branch_name, location, branch_head):
    """Update branch details.
    
    Args:
        engine: SQLAlchemy database engine
        branch_id: ID of the branch
        branch_name: New name of the branch
        location: New location of the branch
        branch_head: New head of the branch
    """
    with engine.connect() as conn:
        conn.execute(text('''
        UPDATE branches 
        SET branch_name = :branch_name, location = :location, branch_head = :branch_head
        WHERE id = :branch_id
        '''), {
            'branch_id': branch_id,
            'branch_name': branch_name,
            'location': location,
            'branch_head': branch_head
        })
        conn.commit()

def update_branch_status(engine, branch_id, is_active):
    """Update branch active status and update related employees status too.
    
    Args:
        engine: SQLAlchemy database engine
        branch_id: ID of the branch
        is_active: New active status
    """
    with engine.connect() as conn:
        # Update branch status
        conn.execute(text('''
        UPDATE branches 
        SET is_active = :is_active
        WHERE id = :branch_id
        '''), {'branch_id': branch_id, 'is_active': is_active})
        
        # Update employees in this branch
        conn.execute(text('''
        UPDATE employees 
        SET is_active = :is_active
        WHERE branch_id = :branch_id
        '''), {'branch_id': branch_id, 'is_active': is_active})
        
        conn.commit()
