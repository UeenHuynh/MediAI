"""
Authentication Page
Login and registration for MediAI platform
"""

import streamlit as st
from utils.audit_logger import AuditEventType
import hashlib


def hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def show_auth_page():
    """Show authentication page (adapted from UI.md AuthPage)"""

    st.markdown('<div class="main-header">🏥 MediAI Login</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="card">
            <h2 style="color: #667eea; text-align: center;">Sign In to MediAI</h2>
            <p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">
                ICU Risk Prediction Platform
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Tab selection
        auth_tab = st.radio(
            "Authentication Method",
            ["🔐 Login", "✍️ Register"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if auth_tab == "🔐 Login":
            show_login_form()
        else:
            show_register_form()

        st.markdown("---")

        # Demo credentials
        st.info("""
        **📝 Demo Credentials:**
        - Username: `demo`
        - Password: `demo123`

        **Note:** This is a demonstration platform. Use demo credentials or create a new account.
        """)

        # Compliance notice
        st.markdown("""
        <div class="alert-success">
            <strong>🔒 Secure Login:</strong> All authentication is encrypted and logged for security auditing.
        </div>
        """, unsafe_allow_html=True)


def show_login_form():
    """Show login form"""

    st.markdown("### 🔐 Login to Your Account")

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        remember_me = st.checkbox("Remember me for 30 days")

        submit = st.form_submit_button("Sign In", use_container_width=True)

        if submit:
            # Validate credentials (demo implementation)
            if validate_login(username, password):
                st.session_state.authenticated = True
                st.session_state.user_id = username

                # Log successful login
                audit = st.session_state.audit_logger
                audit.log_login(
                    user_id=username,
                    ip_address='127.0.0.1',  # TODO: Get real IP
                    success=True
                )

                st.success(f"✅ Welcome back, {username}!")
                st.rerun()
            else:
                # Log failed login
                audit = st.session_state.audit_logger
                audit.log_login(
                    user_id=username or 'unknown',
                    ip_address='127.0.0.1',
                    success=False
                )

                st.error("❌ Invalid username or password")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <p style="text-align: center; color: #6b7280;">
        <a href="#" style="color: #667eea;">Forgot your password?</a>
    </p>
    """, unsafe_allow_html=True)


def show_register_form():
    """Show registration form"""

    st.markdown("### ✍️ Create New Account")

    with st.form("register_form"):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name", placeholder="John")
            username = st.text_input("Username", placeholder="johndoe")
            password = st.text_input("Password", type="password", placeholder="Enter password")

        with col2:
            last_name = st.text_input("Last Name", placeholder="Doe")
            email = st.text_input("Email", placeholder="john.doe@hospital.com")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

        role = st.selectbox("Role", ["Clinician", "Nurse", "Researcher", "Administrator"])

        st.markdown("---")

        terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        hipaa = st.checkbox("I acknowledge HIPAA compliance requirements")

        submit = st.form_submit_button(
            "Create Account",
            use_container_width=True,
            disabled=not (terms and hipaa)
        )

        if submit:
            # Validate inputs
            errors = []

            if not all([first_name, last_name, username, email, password]):
                errors.append("All fields are required")

            if password != confirm_password:
                errors.append("Passwords do not match")

            if len(password) < 8:
                errors.append("Password must be at least 8 characters")

            if '@' not in email:
                errors.append("Invalid email address")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Register user (demo implementation)
                if register_user(username, email, password, first_name, last_name, role):
                    st.success(f"✅ Account created successfully! Welcome, {first_name}!")
                    st.info("Please log in with your new credentials.")
                else:
                    st.error("❌ Username or email already exists")


def validate_login(username: str, password: str) -> bool:
    """
    Validate user credentials

    Demo implementation - accepts:
    - demo / demo123
    - Any username with password matching the username

    Production: Check against database with hashed passwords
    """
    if not username or not password:
        return False

    # Demo credentials
    if username == "demo" and password == "demo123":
        return True

    # Allow any username with matching password (demo only)
    if username == password:
        return True

    return False


def register_user(username: str, email: str, password: str, first_name: str, last_name: str, role: str) -> bool:
    """
    Register new user

    Demo implementation - always succeeds

    Production:
    - Hash password with bcrypt
    - Store in database
    - Send verification email
    - Log registration event
    """

    # Log registration event
    audit = st.session_state.audit_logger
    audit.log_event(
        event_type=AuditEventType.LOGIN,  # Use custom event in production
        user_id=username,
        ip_address='127.0.0.1',
        success=True,
        details={
            'action': 'user_registration',
            'email': email,
            'role': role,
            'name': f"{first_name} {last_name}"
        }
    )

    return True
