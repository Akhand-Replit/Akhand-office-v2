import streamlit as st
from sqlalchemy import text
from pages.common.components import display_profile_header, display_stats_card
from pages.company.branches import manage_branches
from pages.company.employees import manage_employees
from pages.company.messages import view_messages
from pages.company.profile import edit_profile
from utils.auth import logout

def company_dashboard(engine):
    """Display the company dashboard.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h1 class="main-header">Company Dashboard</h1>', unsafe_allow_html=True)
    
    # Display company profile
    display_profile_header(st.session_state.user)
    
    # Navigation
    selected = company_navigation()
    
    if selected == "Dashboard":
        display_company_dashboard_overview(engine)
    elif selected == "Branches":
        manage_branches(engine)
    elif selected == "Employees":
        manage_employees(engine)
    elif selected == "Messages":
        view_messages(engine)
    elif selected == "Profile":
        edit_profile(engine)
    elif selected == "Logout":
        logout()

def company_navigation():
    """Create and return the company navigation menu.
    
    Returns:
        str: Selected menu option
    """
    return st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Branches", "Employees", "Messages", "Profile", "Logout"],
        index=0
    )

def display_company_dashboard_overview(engine):
    """Display the company dashboard overview with statistics and summaries.
    
    Args:
        engine: SQLAlchemy database engine
    """
    st.markdown('<h2 class="sub-header">Company Overview</h2>', unsafe_allow_html=True)
    
    company_id = st.session_state.user["id"]
    
    # Statistics
    with engine.connect() as conn:
        # Total branches
        result = conn.execute(text('''
        SELECT COUNT(*) FROM branches 
        WHERE company_id = :company_id AND is_active = TRUE
        '''), {'company_id': company_id})
        total_branches = result.fetchone()[0]
        
        # Total employees
        result = conn.execute(text('''
        SELECT COUNT(*) FROM employees e
        JOIN branches b ON e.branch_id = b.id
        WHERE b.company_id = :company_id AND e.is_active = TRUE
        '''), {'company_id': company_id})
        total_employees = result.fetchone()[0]
        
        # Unread messages
        result = conn.execute(text('''
        SELECT COUNT(*) FROM messages 
        WHERE receiver_type = 'company' AND receiver_id = :company_id AND is_read = FALSE
        '''), {'company_id': company_id})
        unread_messages = result.fetchone()[0]
        
        # Recent branches
        result = conn.execute(text('''
        SELECT branch_name, location, created_at 
        FROM branches 
        WHERE company_id = :company_id
        ORDER BY created_at DESC 
        LIMIT 5
        '''), {'company_id': company_id})
        recent_branches = result.fetchall()
        
        # Recent messages
        result = conn.execute(text('''
        SELECT message_text, created_at, sender_type
        FROM messages 
        WHERE (receiver_type = 'company' AND receiver_id = :company_id)
           OR (sender_type = 'company' AND sender_id = :company_id)
        ORDER BY created_at DESC 
        LIMIT 5
        '''), {'company_id': company_id})
        recent_messages = result.fetchall()
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        display_stats_card(total_branches, "Active Branches")
    
    with col2:
        display_stats_card(total_employees, "Active Employees")
    
    with col3:
        display_stats_card(unread_messages, "Unread Messages")
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="sub-header">Recent Branches</h3>', unsafe_allow_html=True)
        if recent_branches:
            for branch in recent_branches:
                branch_name = branch[0]
                location = branch[1] or "No location specified"
                created_at = branch[2].strftime('%d %b, %Y') if branch[2] else "Unknown"
                
                st.markdown(f'''
                <div class="card">
                    <strong>{branch_name}</strong>
                    <p>{location}</p>
                    <p style="color: #777; font-size: 0.8rem;">Added on {created_at}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No branches added yet")
        
        if st.button("Add New Branch", key="quick_add_branch"):
            st.session_state.selected_tab = "Branches"
            st.rerun()
    
    with col2:
        st.markdown('<h3 class="sub-header">Recent Messages</h3>', unsafe_allow_html=True)
        if recent_messages:
            for message in recent_messages:
                message_text = message[0]
                created_at = message[1].strftime('%d %b, %Y %H:%M') if message[1] else "Unknown"
                sender_type = message[2]
                is_from_admin = sender_type == 'admin'
                
                # Style differently based on sender
                card_style = "report-item" if is_from_admin else "task-item"
                sender_name = "Admin" if is_from_admin else "You"
                
                st.markdown(f'''
                <div class="{card_style}">
                    <span style="font-weight: 600;">{sender_name}</span> - <span style="color: #777;">{created_at}</span>
                    <p>{message_text[:100]}{'...' if len(message_text) > 100 else ''}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No messages available")
        
        if st.button("View Messages", key="quick_view_messages"):
            st.session_state.selected_tab = "Messages"
            st.rerun()
