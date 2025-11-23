"""
Authentication page - User login and authentication.
"""
import streamlit as st

st.title("🔐 Authentication")
st.markdown("Login to access the MediAI Healthcare ML Platform")

st.markdown("---")

# Login form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 🏥 MediAI Login")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        col_a, col_b = st.columns(2)
        with col_a:
            remember_me = st.checkbox("Remember me")

        submit_button = st.form_submit_button("Login", use_container_width=True)

        if submit_button:
            if username and password:
                # TODO: Implement actual authentication
                # For now, accept any non-empty credentials
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.success(f"✅ Welcome, {username}!")
                st.info("Redirecting to dashboard...")
                st.rerun()
            else:
                st.error("⚠️ Please enter both username and password")

    st.markdown("---")

    # Additional options
    col_forgot, col_signup = st.columns(2)
    with col_forgot:
        if st.button("Forgot Password?", use_container_width=True):
            st.info("Password reset functionality coming soon...")

    with col_signup:
        if st.button("Sign Up", use_container_width=True):
            st.info("User registration coming soon...")

# Information section
st.markdown("---")
st.markdown("### ℹ️ About MediAI")

st.markdown("""
**MediAI Healthcare ML Platform** provides:
- 🔬 **Sepsis Risk Prediction** - Early warning system for sepsis onset
- 💔 **Mortality Risk Prediction** - Hospital mortality assessment
- 📊 **Model Performance Monitoring** - Real-time analytics
- ⚙️ **Configurable Settings** - Customizable thresholds

For demo purposes, you can login with any username and password.
""")

# System status footer
st.markdown("---")
st.markdown("**System Status:** 🟢 Online | **Version:** 1.0.0")
