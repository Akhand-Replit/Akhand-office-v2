import streamlit as st
from config.settings import setup_page_config
from database.connection import init_connection, init_db
from pages.login.login_page import display_login
from pages.admin.dashboard import admin_dashboard
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
        
        # Check if user is logged in
        if "user" not in st.session_state:
            display_login(engine)
        else:
            # Show appropriate dashboard based on user type
            if st.session_state.user.get("is_admin", False):
                admin_dashboard(engine)
            else:
                employee_dashboard(engine)
    else:
        st.error("Failed to connect to the database. Please check your database configuration.")

if __name__ == "__main__":
    main()
