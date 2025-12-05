"""
MediAI Streamlit Application
ICU Risk Prediction Platform with HIPAA/GDPR Compliance

Using st.navigation() API for clean multi-page navigation
"""

import os
from pathlib import Path

# Load environment variables from root .env file
from dotenv import load_dotenv

# Load .env from project root (parent of apps/)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import streamlit as st

# Import page modules
from pages import (
    auth,
    dashboard,
    legal,
    model_performance,
    predict_mortality,
    predict_sepsis,
    settings,
)

# Try to import RAG chatbot, fallback to basic chatbot
try:
    from pages import chatbot_rag as chatbot
except ImportError:
    from pages import chatbot
from utils.audit_logger import AuditEventType, AuditLogger

# Import compliance utilities
from utils.encryption import DataEncryption

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "session_id" not in st.session_state:
    import uuid

    st.session_state.session_id = str(uuid.uuid4())
if "compliance_accepted" not in st.session_state:
    st.session_state.compliance_accepted = False
if "audit_logger" not in st.session_state:
    st.session_state.audit_logger = AuditLogger()
if "encryptor" not in st.session_state:
    st.session_state.encryptor = DataEncryption()

# Page configuration
st.set_page_config(
    page_title="MediAI - ICU Risk Prediction Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/mediai/support",
        "Report a bug": "https://github.com/mediai/issues",
        "About": """
        # MediAI v1.0.0

        ICU Risk Prediction Platform

        **Features:**
        - Sepsis Early Warning (6-hour prediction)
        - Mortality Risk Assessment
        - HIPAA/GDPR Compliant
        - AI-powered predictions with explainability

        **Compliance:**
        - ✅ Data Encryption (AES-256)
        - ✅ Audit Logging
        - ✅ HIPAA Safeguards
        - ✅ GDPR Data Rights
        """,
    },
)

# Custom CSS - Full styling from original design
st.markdown(
    """
    <style>
    /* Global Styles */
    .main {
        background: #764ba2;
        background-attachment: fixed;
    }

    /* Card Styles */
    .card {
        background-color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    /* Header Styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        text-align: center;
        padding: 2rem 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .page-header {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 1rem;
    }

    /* Risk Level Colors */
    .risk-low {
        color: #10b981;
        font-weight: bold;
    }
    .risk-medium {
        color: #f59e0b;
        font-weight: bold;
    }
    .risk-high {
        color: #ef4444;
        font-weight: bold;
    }
    .risk-critical {
        color: #dc2626;
        font-weight: bold;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.875rem;
        opacity: 0.9;
    }

    /* Button Styles */
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

    /* Sidebar dark theme */
    section[data-testid="stSidebar"] {
        background-color: #1f2937;
    }

    section[data-testid="stSidebar"] > div:first-child {
        background-color: #1f2937;
    }

    /* Sidebar text colors */
    section[data-testid="stSidebar"] .element-container {
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] h3 {
        color: #f9fafb;
    }

    /* Compliance Badge */
    .compliance-badge {
        display: inline-block;
        background-color: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }

    /* Alert Styles */
    .alert-success {
        background-color: #d1fae5;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .alert-warning {
        background-color: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    .alert-danger {
        background-color: #fee2e2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }

    /* Patient Table */
    .patient-row-critical {
        background-color: #fee2e2 !important;
    }

    .patient-row-high {
        background-color: #fed7aa !important;
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
""",
    unsafe_allow_html=True,
)


def show_compliance_modal():
    """Show HIPAA/GDPR compliance notice"""
    st.markdown(
        '<div style="font-size: 2.5rem; font-weight: bold; color: white; text-align: center; padding: 2rem 0; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);">🏥 MediAI - ICU Risk Prediction Platform</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="card">
        <h2 style="color: #667eea; text-align: center;">Healthcare Data Compliance Notice</h2>
        <p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">
            Please review and accept our data protection policies before proceeding
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🇺🇸 HIPAA Compliance")
        st.markdown("**Health Insurance Portability and Accountability Act**")
        st.markdown("")
        st.markdown("**We protect your health information through:**")
        st.markdown(
            """
        - ✓ AES-256 Encryption for all PHI
        - ✓ Comprehensive Audit Logging
        - ✓ Role-Based Access Controls
        - ✓ Secure Data Transmission (TLS)
        - ✓ 7-Year Retention Policy
        """
        )

    with col2:
        st.markdown("### 🇪🇺 GDPR Compliance")
        st.markdown("**General Data Protection Regulation**")
        st.markdown("")
        st.markdown("**We process your data with:**")
        st.markdown(
            """
        - ✓ Explicit Consent
        - ✓ Data Minimization
        - ✓ Purpose Limitation
        - ✓ Pseudonymization
        - ✓ Security by Design
        """
        )

    st.markdown("---")

    # Important Note
    st.warning(
        """
    ⚠️ **Important Note**

    This is a **demonstration platform** for educational and research purposes only.
    This system is **NOT approved for clinical use** and should not be used to make
    medical decisions. All predictions must be reviewed by qualified healthcare professionals.
    """
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        hipaa_consent = st.checkbox(
            "✅ I have read and accept the HIPAA Privacy Policy", key="hipaa_consent"
        )

        gdpr_consent = st.checkbox(
            "✅ I have read and accept the GDPR Data Protection Policy",
            key="gdpr_consent",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "Continue to Application",
            use_container_width=True,
            disabled=not (hipaa_consent and gdpr_consent),
        ):
            st.session_state.compliance_accepted = True

            # Log consent
            audit = st.session_state.audit_logger
            audit.log_consent(
                user_id=st.session_state.get("user_id", "anonymous"),
                patient_id=None,
                consent_given=True,
                ip_address="127.0.0.1",
            )

            st.rerun()

        if not (hipaa_consent and gdpr_consent):
            st.info("📋 Please accept both policies to continue")


def main():
    """Main application with st.navigation() API"""

    # Check compliance acceptance
    if not st.session_state.compliance_accepted:
        show_compliance_modal()
        return

    # Check authentication
    if not st.session_state.authenticated:
        auth.show_auth_page()
        return

    # Sidebar with user info, navigation, and compliance status
    with st.sidebar:
        # Logo
        st.image(
            "https://via.placeholder.com/300x100/667eea/FFFFFF?text=MediAI",
            use_container_width=True,
        )

        # User info
        st.markdown("### 👤 User")
        st.write(f"**{st.session_state.user_id}**")

        st.markdown("---")

    # Define pages with st.Page
    pages = [
        st.Page(
            dashboard.show_dashboard, title="Dashboard", icon="🏠", url_path="dashboard"
        ),
        st.Page(
            predict_sepsis.show_sepsis_prediction,
            title="Sepsis Prediction",
            icon="🔬",
            url_path="sepsis",
        ),
        st.Page(
            predict_mortality.show_mortality_prediction,
            title="Mortality Prediction",
            icon="💔",
            url_path="mortality",
        ),
        st.Page(
            model_performance.show_model_performance,
            title="Model Performance",
            icon="📊",
            url_path="performance",
        ),
        st.Page(
            chatbot.show_chatbot, title="AI Assistant", icon="🤖", url_path="chatbot"
        ),
        st.Page(
            settings.show_settings, title="Settings", icon="⚙️", url_path="settings"
        ),
        st.Page(legal.show_legal, title="Legal", icon="📄", url_path="legal"),
    ]

    # Create navigation
    page = st.navigation(pages)

    # Render selected page
    page.run()

    # Sidebar compliance and stats AFTER navigation
    with st.sidebar:
        st.markdown("---")

        # Compliance status
        st.markdown("### 🛡️ Compliance")
        st.success("✅ HIPAA")
        st.success("✅ GDPR")
        st.info("🔒 Encrypted")

        st.markdown("---")

        # Quick stats
        st.markdown("### 📈 System")
        st.metric("API", "Online", "✅")
        st.metric("Patients", "1,247")
        st.metric("High Risk", "87", "-5")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            # Log logout
            audit = st.session_state.audit_logger
            audit.log_event(
                event_type=AuditEventType.LOGOUT,
                user_id=st.session_state.user_id,
                ip_address="127.0.0.1",
                success=True,
            )

            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.rerun()

    # Footer
    st.markdown("---")

    # Footer with clickable compliance links
    st.markdown(
        """
    <div class="footer">
        <p>
            🏥 MediAI v1.0.0 |
            <a href="https://www.hhs.gov/hipaa/index.html" target="_blank" style="color: #10b981; text-decoration: none;">HIPAA</a> &
            <a href="https://gdpr.eu/" target="_blank" style="color: #10b981; text-decoration: none;">GDPR</a> Compliant |
            © 2025
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Legal document links (temporarily hidden)
    # st.markdown("""
    # <div style="text-align: center; margin-top: 1rem; font-size: 0.85rem;">
    #     <a href="/legal" style="color: #9ca3af; text-decoration: none; margin: 0 1rem;">📋 Terms & Conditions</a> |
    #     <a href="/legal" style="color: #9ca3af; text-decoration: none; margin: 0 1rem;">🔒 Privacy Policy</a>
    # </div>
    # """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
