import streamlit as st
from sqlalchemy import text

def authenticate(engine, username, password):
    """Authenticate a user based on username and password.
    
    Args:
        engine: SQLAlchemy database engine
        username: User's username
        password: User's password
        
    Returns:
        dict: User information if authentication succeeds, None otherwise
    """
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
    
    # If not admin, check employee credentials in database
    with engine.connect() as conn:
        result = conn.execute(text('''
        SELECT id, username, full_name, profile_pic_url
        FROM employees
        WHERE username = :username AND password = :password AND is_active = TRUE
        '''), {'username': username, 'password': password})
        user = result.fetchone()
    
    if user:
        return {"id": user[0], "username": user[1], "full_name": user[2], "is_admin": False, "profile_pic_url": user[3]}
    return None

def logout():
    """Log out the current user by clearing session state."""
    st.session_state.pop("user", None)
    st.rerun()
