import streamlit as st
from config.settings import setup_page_config
from database.connection import init_connection, init_db
from pages.login.login_page import display_login
from pages.admin.dashboard import admin_dashboard
from pages.company.dashboard import company_dashboard
from pages.employee.dashboard import employee_dashboard

def main():
    """Main application entry point"""
    # Set up page configuration
    setup_page_config()
    
    # Initialize database connection
    engine = init_connection()
    
    if engine:
        # Initialize database tables if they don't exist
        init_db(engine)
# Add to your init_db() function in app.py
def init_db():
    with engine.connect() as conn:
        # Existing tables...
        
        # Add employee roles table and role_id column to employees
        conn.execute(text('''
        -- Employee Roles table
        CREATE TABLE IF NOT EXISTS employee_roles (
            id SERIAL PRIMARY KEY,
            company_id INTEGER REFERENCES companies(id),
            role_name VARCHAR(50) NOT NULL,
            role_level INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_id, role_name)
        );
        
        -- Add role_id to employees table
        ALTER TABLE employees ADD COLUMN IF NOT EXISTS role_id INTEGER REFERENCES employee_roles(id);
        
        -- Insert default roles for each company
        INSERT INTO employee_roles (role_name, role_level, company_id)
        SELECT 'Manager', 1, id FROM companies
        WHERE NOT EXISTS (
            SELECT 1 FROM employee_roles WHERE role_name = 'Manager' AND company_id = companies.id
        );
        
        INSERT INTO employee_roles (role_name, role_level, company_id)
        SELECT 'Asst. Manager', 2, id FROM companies
        WHERE NOT EXISTS (
            SELECT 1 FROM employee_roles WHERE role_name = 'Asst. Manager' AND company_id = companies.id
        );
        
        INSERT INTO employee_roles (role_name, role_level, company_id)
        SELECT 'General Employee', 3, id FROM companies
        WHERE NOT EXISTS (
            SELECT 1 FROM employee_roles WHERE role_name = 'General Employee' AND company_id = companies.id
        );
        '''))
        conn.commit()
        
        # Set default role for existing employees
        conn.execute(text('''
        -- Set existing employees to General Employee role by default
        UPDATE employees e
        SET role_id = r.id
        FROM employee_roles r
        JOIN branches b ON r.company_id = b.company_id
        WHERE e.branch_id = b.id AND r.role_name = 'General Employee' AND e.role_id IS NULL;
        '''))
        conn.commit()
        
        # Check if user is logged in
        if "user" not in st.session_state:
            display_login(engine)
        else:
            # Show appropriate dashboard based on user type
            user_type = st.session_state.user.get("user_type", "")
            
            if user_type == "admin":
                admin_dashboard(engine)
            elif user_type == "company":
                company_dashboard(engine)
            elif user_type == "employee":
                employee_dashboard(engine)
            else:
                st.error("Invalid user type. Please log out and try again.")
                if st.button("Logout"):
                    st.session_state.pop("user", None)
                    st.rerun()
    else:
        st.error("Failed to connect to the database. Please check your database configuration.")

if __name__ == "__main__":
    main()
