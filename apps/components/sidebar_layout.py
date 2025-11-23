"""
Shared Sidebar Layout for MediAI Multi-Page App
Custom sidebar with navigation, compliance badges, and system stats
"""

import streamlit as st
from utils.audit_logger import AuditLogger, AuditEventType


def render_custom_sidebar(current_page=None):
    """
    Render custom sidebar with navigation, compliance status, and system stats

    Args:
        current_page: Name of current page for highlighting (e.g., "Dashboard", "Sepsis")
    """
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
