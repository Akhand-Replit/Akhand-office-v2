import streamlit as st

def display_profile_header(user):
    """Display user profile header with image and name.
    
    Args:
        user: User dict with profile information
    """
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown('<div class="profile-container">', unsafe_allow_html=True)
        try:
            st.image(user["profile_pic_url"], width=80, clamp=True, output_format="auto", 
                    channels="RGB", use_container_width=False)
        except:
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y", 
                    width=80, use_container_width=False)
        
        user_type = "Administrator" if user.get("is_admin", False) else "Employee"
        st.markdown(f'''
        
