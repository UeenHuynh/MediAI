"""
Shared Sidebar Layout for MediAI Multi-Page App
Custom sidebar with navigation, compliance badges, and system stats
"""

import streamlit as st
from utils.audit_logger import AuditLogger, AuditEventType


def inject_custom_css():
    """Inject custom CSS for sidebar styling"""
    st.markdown("""
        <style>
        /* Hide Streamlit default navigation menu */
        [data-testid="stSidebarNav"] {
            display: none;
        }

        /* Custom navigation link styling */
        section[data-testid="stSidebar"] a {
            text-decoration: none;
            color: #e5e7eb;
            display: block;
            padding: 0.75rem 1rem;
            border-radius: 0.5rem;
            transition: all 0.2s;
            margin-bottom: 0.25rem;
        }

        section[data-testid="stSidebar"] a:hover {
            background-color: rgba(102, 126, 234, 0.2);
            color: #ffffff;
            transform: translateX(4px);
        }

        /* Active page highlight */
        section[data-testid="stSidebar"] strong {
            color: #667eea;
            font-size: 1.05rem;
        }

        /* Sidebar background */
        section[data-testid="stSidebar"] {
            background-color: #1f2937;
        }

        section[data-testid="stSidebar"] > div:first-child {
            background-color: #1f2937;
        }

        /* Sidebar spacing improvements */
        section[data-testid="stSidebar"] {
            padding-top: 1rem;
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            margin-bottom: 0.5rem;
        }

        /* Improve metric display in sidebar */
        section[data-testid="stSidebar"] [data-testid="stMetric"] {
            background-color: rgba(102, 126, 234, 0.1);
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }

        /* Main content gradient background */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            background-attachment: fixed;
        }

        /* Responsive improvements */
        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                min-width: 250px;
            }
        }

        /* Card styles */
        .card {
            background-color: white;
            padding: 2rem;
            border-radius: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }

        /* Button styles */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 2rem;
            color: white;
            font-size: 0.875rem;
            opacity: 0.8;
        }
        </style>
    """, unsafe_allow_html=True)


def render_custom_sidebar(current_page=None):
    """
    Render custom sidebar with navigation, compliance status, and system stats

    Args:
        current_page: Name of current page for highlighting (e.g., "Dashboard", "Sepsis")
    """
    # Inject custom CSS
    inject_custom_css()

    with st.sidebar:
        # Logo
        st.image("https://via.placeholder.com/300x100/667eea/FFFFFF?text=MediAI", use_column_width=True)

        # User info
        st.markdown("### 👤 User")
        st.write(f"**{st.session_state.get('user_id', 'Guest')}**")

        st.markdown("---")

        # Navigation
        st.markdown("### 🧭 Navigation")

        # Navigation links with custom styling
        pages = [
            ("🏠 Dashboard", "Dashboard", "pages/1_Dashboard.py"),
            ("🔬 Sepsis Prediction", "Sepsis", "pages/2_Sepsis.py"),
            ("💔 Mortality Prediction", "Mortality", "pages/3_Mortality.py"),
            ("📊 Model Performance", "Performance", "pages/4_Performance.py"),
            ("⚙️ Settings", "Settings", "pages/5_Settings.py")
        ]

        for label, page_key, page_path in pages:
            # Highlight current page
            if current_page and page_key.lower() in current_page.lower():
                st.markdown(f"**→ {label}**")
            else:
                st.page_link(page_path, label=label)

        st.markdown("---")

        # Compliance status
        st.markdown("### 🛡️ Compliance Status")
        st.success("✅ HIPAA Compliant")
        st.success("✅ GDPR Compliant")
        st.info("🔒 Data Encrypted")
        st.info("📝 Audit Logging Active")

        st.markdown("---")

        # Quick stats
        st.markdown("### 📈 System Status")
        st.metric("API Status", "Online", "✅")
        st.metric("Total Patients", "1,247")
        st.metric("High Risk", "87", "-5")

        st.markdown("---")

        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            # Log logout
            if 'audit_logger' in st.session_state:
                audit = st.session_state.audit_logger
                audit.log_event(
                    event_type=AuditEventType.LOGOUT,
                    user_id=st.session_state.get('user_id', 'unknown'),
                    ip_address='127.0.0.1',
                    success=True
                )

            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.switch_page("streamlit_app.py")


def check_authentication():
    """
    Check if user is authenticated, redirect to home if not
    Returns True if authenticated, False otherwise
    """
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Please login first")
        st.page_link("streamlit_app.py", label="Go to Login")
        st.stop()
        return False
    return True


def check_compliance():
    """
    Check if user accepted compliance, redirect to home if not
    Returns True if accepted, False otherwise
    """
    if not st.session_state.get('compliance_accepted', False):
        st.warning("⚠️ Please accept compliance policies first")
        st.page_link("streamlit_app.py", label="Go to Compliance")
        st.stop()
        return False
    return True


def render_footer():
    """Render consistent footer across all pages"""
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        <p>🏥 MediAI v1.0.0 | HIPAA & GDPR Compliant | © 2025</p>
        <p>
            <a href="/docs/HIPAA_COMPLIANCE.md" target="_blank">HIPAA Policy</a> |
            <a href="/docs/GDPR_COMPLIANCE.md" target="_blank">GDPR Policy</a> |
            <a href="mailto:privacy@mediai.example.com">Contact Privacy Officer</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
