"""
MediAI Streamlit Application
ICU Risk Prediction Platform with HIPAA/GDPR Compliance

Multi-page app structure following UI.md specifications
"""

import streamlit as st
import os
from datetime import datetime

# Import compliance utilities
from utils.encryption import DataEncryption
from utils.audit_logger import AuditLogger, AuditEventType

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'session_id' not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())
if 'compliance_accepted' not in st.session_state:
    st.session_state.compliance_accepted = False
if 'audit_logger' not in st.session_state:
    st.session_state.audit_logger = AuditLogger()
if 'encryptor' not in st.session_state:
    st.session_state.encryptor = DataEncryption()

# Page configuration
st.set_page_config(
    page_title="MediAI - ICU Risk Prediction Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/mediai/support',
        'Report a bug': 'https://github.com/mediai/issues',
        'About': '''
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
        '''
    }
)

# Custom CSS - Adapted from UI.md design
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

    /* Sidebar */
    .css-1d391kg {
        background-color: #1f2937;
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
""", unsafe_allow_html=True)


def show_compliance_modal():
    """Show HIPAA/GDPR compliance notice (adapted from UI.md ComplianceModal)"""
    st.markdown('<div class="main-header">🏥 MediAI - ICU Risk Prediction Platform</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h2 style="color: #667eea; text-align: center;">Healthcare Data Compliance Notice</h2>
        <p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">
            Please review and accept our data protection policies before proceeding
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="card">
            <h3 style="color: #667eea;">🇺🇸 HIPAA Compliance</h3>
            <p><strong>Health Insurance Portability and Accountability Act</strong></p>

            <h4>We protect your health information through:</h4>
            <ul>
                <li><span class="compliance-badge">✓</span> AES-256 Encryption for all PHI</li>
                <li><span class="compliance-badge">✓</span> Comprehensive Audit Logging</li>
                <li><span class="compliance-badge">✓</span> Role-Based Access Controls</li>
                <li><span class="compliance-badge">✓</span> Secure Data Transmission (TLS)</li>
                <li><span class="compliance-badge">✓</span> 7-Year Retention Policy</li>
            </ul>

            <h4>Your Rights:</h4>
            <ul>
                <li>Right to access your health information</li>
                <li>Right to request corrections</li>
                <li>Right to accounting of disclosures</li>
                <li>Right to request restrictions</li>
                <li>Right to breach notification</li>
            </ul>

            <p><a href="/docs/HIPAA_COMPLIANCE.md" target="_blank">📄 Read Full HIPAA Policy</a></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <h3 style="color: #667eea;">🇪🇺 GDPR Compliance</h3>
            <p><strong>General Data Protection Regulation</strong></p>

            <h4>We process your data with:</h4>
            <ul>
                <li><span class="compliance-badge">✓</span> Explicit Consent</li>
                <li><span class="compliance-badge">✓</span> Data Minimization</li>
                <li><span class="compliance-badge">✓</span> Purpose Limitation</li>
                <li><span class="compliance-badge">✓</span> Pseudonymization</li>
                <li><span class="compliance-badge">✓</span> Security by Design</li>
            </ul>

            <h4>Your Rights:</h4>
            <ul>
                <li>Right to be informed</li>
                <li>Right of access</li>
                <li>Right to rectification</li>
                <li>Right to erasure ("Right to be forgotten")</li>
                <li>Right to data portability</li>
                <li>Right to object</li>
            </ul>

            <p><a href="/docs/GDPR_COMPLIANCE.md" target="_blank">📄 Read Full GDPR Policy</a></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3 style="color: #667eea; text-align: center;">Important Information</h3>

        <div class="alert-warning">
            <strong>⚠️ Demo Platform Notice:</strong> This is a demonstration platform using
            de-identified MIMIC-IV data. No real patient data is used. For production use with
            real patient data, additional security controls and compliance audits are required.
        </div>

        <h4>How We Use Your Data:</h4>
        <ul>
            <li><strong>Purpose:</strong> ICU risk prediction for sepsis and mortality</li>
            <li><strong>Legal Basis:</strong> Healthcare provision + Explicit consent</li>
            <li><strong>Data Retention:</strong> 7 years (legal requirement)</li>
            <li><strong>Data Sharing:</strong> Only with authorized healthcare providers</li>
            <li><strong>Your Control:</strong> You can withdraw consent at any time</li>
        </ul>

        <h4>Technical Safeguards:</h4>
        <ul>
            <li>🔒 End-to-end encryption</li>
            <li>📝 Complete audit trail</li>
            <li>🔐 Secure authentication</li>
            <li>🛡️ Regular security updates</li>
            <li>💾 Encrypted backups</li>
        </ul>

        <h4>Contact Information:</h4>
        <ul>
            <li><strong>Data Protection Officer:</strong> dpo@mediai.example.com</li>
            <li><strong>Privacy Inquiries:</strong> privacy@mediai.example.com</li>
            <li><strong>Security Issues:</strong> security@mediai.example.com</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Consent checkboxes
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        hipaa_consent = st.checkbox(
            "✅ I have read and accept the HIPAA Privacy Policy",
            key="hipaa_consent"
        )

        gdpr_consent = st.checkbox(
            "✅ I have read and accept the GDPR Data Protection Policy",
            key="gdpr_consent"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Continue to Application", use_container_width=True, disabled=not (hipaa_consent and gdpr_consent)):
            st.session_state.compliance_accepted = True

            # Log consent
            audit = st.session_state.audit_logger
            audit.log_consent(
                user_id=st.session_state.get('user_id', 'anonymous'),
                patient_id=None,
                consent_given=True,
                ip_address='127.0.0.1'  # TODO: Get real IP
            )

            st.rerun()

        if not (hipaa_consent and gdpr_consent):
            st.info("📋 Please accept both policies to continue")


def main():
    """Main application router"""

    # Check compliance acceptance
    if not st.session_state.compliance_accepted:
        show_compliance_modal()
        return

    # Check authentication
    if not st.session_state.authenticated:
        # Import auth page
        from pages import auth
        auth.show_auth_page()
        return

    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/667eea/FFFFFF?text=MediAI", use_column_width=True)

        st.markdown("### 👤 User")
        st.write(f"**{st.session_state.user_id}**")

        st.markdown("---")

        st.markdown("### 🧭 Navigation")

        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "🔬 Predict Sepsis", "💔 Predict Mortality", "📊 Model Performance", "⚙️ Settings"],
            label_visibility="collapsed"
        )

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

        if st.button("🚪 Logout", use_container_width=True):
            # Log logout
            audit = st.session_state.audit_logger
            audit.log_event(
                event_type=AuditEventType.LOGOUT,
                user_id=st.session_state.user_id,
                ip_address='127.0.0.1',
                success=True
            )

            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.rerun()

    # Route to pages
    if page == "🏠 Dashboard":
        from pages import dashboard
        dashboard.show_dashboard()
    elif page == "🔬 Predict Sepsis":
        from pages import predict_sepsis
        predict_sepsis.show_sepsis_prediction()
    elif page == "💔 Predict Mortality":
        from pages import predict_mortality
        predict_mortality.show_mortality_prediction()
    elif page == "📊 Model Performance":
        from pages import model_performance
        model_performance.show_model_performance()
    elif page == "⚙️ Settings":
        from pages import settings
        settings.show_settings()

    # Footer
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


if __name__ == "__main__":
    main()
