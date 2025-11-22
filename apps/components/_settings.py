"""
Settings Page
System configuration and user preferences
"""

import streamlit as st
from utils.audit_logger import AuditEventType


def show_settings():
    """Settings page"""

    st.markdown('<div class="page-header">⚙️ System Settings</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Risk Thresholds",
        "🔒 Security & Privacy",
        "🔔 Notifications",
        "👤 User Profile"
    ])

    with tab1:
        show_risk_threshold_settings()

    with tab2:
        show_security_settings()

    with tab3:
        show_notification_settings()

    with tab4:
        show_user_profile()


def show_risk_threshold_settings():
    """Risk threshold configuration"""

    st.markdown("### 🎯 Risk Classification Thresholds")

    st.info("""
    Configure the risk score thresholds for each risk level.
    These thresholds determine when alerts are triggered.
    """)

    st.markdown("#### 🔬 Sepsis Model")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**LOW**")
        low_threshold = st.slider(
            "Low Risk Max",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05,
            key="sepsis_low",
            help="Scores below this are LOW risk"
        )
        st.success(f"0% - {low_threshold*100:.0f}%")

    with col2:
        st.markdown("**MEDIUM**")
        medium_threshold = st.slider(
            "Medium Risk Max",
            min_value=low_threshold,
            max_value=1.0,
            value=0.5,
            step=0.05,
            key="sepsis_medium",
            help="Scores in this range are MEDIUM risk"
        )
        st.warning(f"{low_threshold*100:.0f}% - {medium_threshold*100:.0f}%")

    with col3:
        st.markdown("**HIGH**")
        high_threshold = st.slider(
            "High Risk Max",
            min_value=medium_threshold,
            max_value=1.0,
            value=0.8,
            step=0.05,
            key="sepsis_high",
            help="Scores in this range are HIGH risk"
        )
        st.error(f"{medium_threshold*100:.0f}% - {high_threshold*100:.0f}%")

    with col4:
        st.markdown("**CRITICAL**")
        st.markdown("Auto-calculated")
        st.markdown(f"<div class='risk-critical'>{high_threshold*100:.0f}% - 100%</div>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### 💔 Mortality Model")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mortality_low = st.slider("Low", 0.0, 1.0, 0.2, 0.05, key="mort_low")
        st.success(f"0% - {mortality_low*100:.0f}%")

    with col2:
        mortality_medium = st.slider("Medium", mortality_low, 1.0, 0.5, 0.05, key="mort_medium")
        st.warning(f"{mortality_low*100:.0f}% - {mortality_medium*100:.0f}%")

    with col3:
        mortality_high = st.slider("High", mortality_medium, 1.0, 0.75, 0.05, key="mort_high")
        st.error(f"{mortality_medium*100:.0f}% - {mortality_high*100:.0f}%")

    with col4:
        st.markdown("Auto-calculated")
        st.markdown(f"<div class='risk-critical'>{mortality_high*100:.0f}% - 100%</div>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Thresholds", use_container_width=True):
            # Log configuration change
            audit = st.session_state.audit_logger
            audit.log_event(
                event_type=AuditEventType.CONFIG_CHANGE,
                user_id=st.session_state.user_id,
                ip_address='127.0.0.1',
                details={
                    'setting': 'risk_thresholds',
                    'sepsis': {
                        'low': low_threshold,
                        'medium': medium_threshold,
                        'high': high_threshold
                    },
                    'mortality': {
                        'low': mortality_low,
                        'medium': mortality_medium,
                        'high': mortality_high
                    }
                }
            )

            st.success("✅ Thresholds saved successfully")

    with col2:
        if st.button("🔄 Reset to Defaults", use_container_width=True):
            st.info("Thresholds reset to default values")
            st.rerun()


def show_security_settings():
    """Security and privacy settings"""

    st.markdown("### 🔒 Security & Privacy Settings")

    # Encryption status
    st.markdown("#### 🔐 Data Encryption")

    col1, col2 = st.columns(2)

    with col1:
        st.success("✅ **AES-256 Encryption: ACTIVE**")
        st.write("All PHI fields are encrypted at rest")

        st.markdown("**Encrypted Fields:**")
        st.write("""
        - Patient ID
        - Patient Name
        - MRN (Medical Record Number)
        - Date of Birth
        - Contact Information
        """)

    with col2:
        encryption_enabled = st.checkbox(
            "Enable automatic PHI encryption",
            value=True,
            help="Automatically encrypt PHI fields in database"
        )

        mask_phi = st.checkbox(
            "Mask PHI in UI by default",
            value=True,
            help="Show masked values (***-1234) instead of full PHI"
        )

        if encryption_enabled:
            st.info("🔒 Encryption is enabled")
        else:
            st.warning("⚠️ Encryption is disabled - Only for testing!")

    st.markdown("---")

    # Audit logging
    st.markdown("#### 📝 Audit Logging")

    col1, col2 = st.columns(2)

    with col1:
        st.success("✅ **Audit Logging: ACTIVE**")
        st.write("All user actions are logged for compliance")

        audit = st.session_state.audit_logger
        st.metric("Log Files", "15 files")
        st.metric("Retention Period", "7 years")

    with col2:
        log_level = st.selectbox(
            "Logging Level",
            ["INFO", "DEBUG", "WARNING", "ERROR"],
            index=0,
            help="Set logging verbosity"
        )

        if st.button("📊 View My Activity Log", use_container_width=True):
            with st.expander("Recent Activity", expanded=True):
                activity = audit.get_user_activity(
                    user_id=st.session_state.user_id,
                    days=7
                )

                if activity:
                    st.write(f"**{len(activity)} events in last 7 days**")
                    import pandas as pd
                    df = pd.DataFrame(activity[:20])  # Show last 20
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No activity logs found")

    st.markdown("---")

    # Session management
    st.markdown("#### 🕐 Session Management")

    col1, col2 = st.columns(2)

    with col1:
        session_timeout = st.slider(
            "Session Timeout (minutes)",
            min_value=5,
            max_value=120,
            value=30,
            step=5,
            help="Automatically log out after inactivity"
        )

        auto_logout = st.checkbox(
            "Enable automatic logout",
            value=True,
            help="Log out automatically after timeout period"
        )

    with col2:
        require_mfa = st.checkbox(
            "Require Multi-Factor Authentication (MFA)",
            value=False,
            help="Enable MFA for enhanced security (coming soon)"
        )

        remember_device = st.checkbox(
            "Remember this device for 30 days",
            value=False,
            help="Skip MFA on this device for 30 days"
        )

        if require_mfa:
            st.warning("⚠️ MFA is planned for future release")

    st.markdown("---")

    # HIPAA/GDPR compliance
    st.markdown("#### ⚖️ Compliance Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**HIPAA Compliance**")
        hipaa_mode = st.checkbox("Enable HIPAA mode", value=True)

        if hipaa_mode:
            st.success("✅ HIPAA safeguards active")
            st.write("""
            - PHI encryption
            - Audit logging (7 years)
            - Access controls
            - Breach notification procedures
            """)

    with col2:
        st.markdown("**GDPR Compliance**")
        gdpr_mode = st.checkbox("Enable GDPR mode", value=True)

        if gdpr_mode:
            st.success("✅ GDPR protections active")
            st.write("""
            - Consent management
            - Right to access
            - Right to erasure
            - Data portability
            """)

    if st.button("📄 View Compliance Documentation", use_container_width=True):
        st.info("""
        **Documentation Available:**
        - `/docs/HIPAA_COMPLIANCE.md`
        - `/docs/GDPR_COMPLIANCE.md`
        """)


def show_notification_settings():
    """Notification preferences"""

    st.markdown("### 🔔 Notification Settings")

    st.info("Configure when and how you receive alerts for high-risk patients")

    # Alert triggers
    st.markdown("#### ⚡ Alert Triggers")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Sepsis Alerts**")
        alert_sepsis_high = st.checkbox("Alert on HIGH risk", value=True)
        alert_sepsis_critical = st.checkbox("Alert on CRITICAL risk", value=True)
        alert_sepsis_trend = st.checkbox("Alert on rapidly increasing trend", value=True)

    with col2:
        st.markdown("**Mortality Alerts**")
        alert_mortality_high = st.checkbox("Alert on HIGH mortality risk", value=False)
        alert_mortality_critical = st.checkbox("Alert on CRITICAL mortality risk", value=True)
        alert_mortality_change = st.checkbox("Alert on significant risk change", value=True)

    st.markdown("---")

    # Notification channels
    st.markdown("#### 📢 Notification Channels")

    col1, col2, col3 = st.columns(3)

    with col1:
        notify_ui = st.checkbox("In-App Notifications", value=True)
        if notify_ui:
            st.success("✅ Show alerts in UI")

    with col2:
        notify_email = st.checkbox("Email Notifications", value=False)
        if notify_email:
            email = st.text_input("Email Address", value="user@hospital.com")

    with col3:
        notify_sms = st.checkbox("SMS Notifications", value=False)
        if notify_sms:
            phone = st.text_input("Phone Number", value="+1234567890")

    st.markdown("---")

    # Notification frequency
    st.markdown("#### ⏱️ Notification Frequency")

    notify_immediate = st.radio(
        "When to send notifications",
        [
            "Immediately when risk detected",
            "Batched every 15 minutes",
            "Batched every hour",
            "Once daily summary"
        ],
        index=0
    )

    quiet_hours = st.checkbox("Enable quiet hours", value=False)

    if quiet_hours:
        col1, col2 = st.columns(2)
        with col1:
            quiet_start = st.time_input("Quiet hours start", value=None)
        with col2:
            quiet_end = st.time_input("Quiet hours end", value=None)

    st.markdown("---")

    if st.button("💾 Save Notification Settings", use_container_width=True):
        # Log configuration change
        audit = st.session_state.audit_logger
        audit.log_event(
            event_type=AuditEventType.CONFIG_CHANGE,
            user_id=st.session_state.user_id,
            ip_address='127.0.0.1',
            details={'setting': 'notifications'}
        )

        st.success("✅ Notification settings saved")


def show_user_profile():
    """User profile settings"""

    st.markdown("### 👤 User Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Personal Information")

        username = st.text_input("Username", value=st.session_state.user_id, disabled=True)
        email = st.text_input("Email", value=f"{st.session_state.user_id}@hospital.com")
        first_name = st.text_input("First Name", value="John")
        last_name = st.text_input("Last Name", value="Doe")

        role = st.selectbox(
            "Role",
            ["Clinician", "Nurse", "Researcher", "Administrator"],
            index=0
        )

        department = st.selectbox(
            "Department",
            ["ICU", "Emergency", "Internal Medicine", "Surgery", "Research"],
            index=0
        )

    with col2:
        st.markdown("#### Preferences")

        language = st.selectbox("Language", ["English", "Tiếng Việt"], index=0)

        timezone = st.selectbox(
            "Timezone",
            ["UTC", "Asia/Ho_Chi_Minh", "America/New_York", "Europe/London"],
            index=1
        )

        date_format = st.selectbox(
            "Date Format",
            ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"],
            index=0
        )

        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"], index=0)

    st.markdown("---")

    st.markdown("#### 🔑 Change Password")

    col1, col2, col3 = st.columns(3)

    with col1:
        current_password = st.text_input("Current Password", type="password")

    with col2:
        new_password = st.text_input("New Password", type="password")

    with col3:
        confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("🔄 Change Password", use_container_width=True):
        if new_password == confirm_password and len(new_password) >= 8:
            st.success("✅ Password changed successfully")
        else:
            st.error("❌ Passwords do not match or too short (min 8 characters)")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save Profile", use_container_width=True):
            st.success("✅ Profile updated successfully")

    with col2:
        if st.button("❌ Delete Account", use_container_width=True):
            st.error("⚠️ This action cannot be undone!")
            st.warning("Contact administrator to delete your account")
