import streamlit as st
from sqlalchemy import create_engine, text

@st.cache_resource
def init_connection():
    """Initialize database connection with caching.
    
    Returns:
        SQLAlchemy engine or None if connection fails
    """
    try:
        return create_engine(st.secrets["postgres"]["url"])
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def init_db(engine):
    """Initialize database tables if they don't exist.
    
    Args:
        engine: SQLAlchemy database engine
    """
    with engine.connect() as conn:
        conn.execute(text('''
        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(100) NOT NULL,
            profile_pic_url TEXT,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        CREATE TABLE IF NOT EXISTS daily_reports (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER REFERENCES employees(id),
            report_date DATE NOT NULL,
            report_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            employee_id INTEGER REFERENCES employees(id),
            task_description TEXT NOT NULL,
            due_date DATE,
            is_completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''))
        conn.commit()
