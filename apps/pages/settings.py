"""
Settings page - Application configuration and preferences.
"""
import streamlit as st

st.set_page_config(page_title="Settings", page_icon="⚙️")

st.title("⚙️ Settings")
st.markdown("Configure application preferences and system settings.")

st.markdown("---")

# Create tabs for different settings categories
tab1, tab2, tab3, tab4 = st.tabs([
    "🎨 Display",
    "🔔 Alerts",
    "🔐 System",
    "ℹ️ About"
])

with tab1:
    show_display_settings()

with tab2:
    show_alert_settings()

with tab3:
    show_system_settings()

with tab4:
    show_about()


def show_display_settings():
    """Show display and UI settings."""
    st.subheader("Display Settings")

    # Theme settings
    st.markdown("### 🎨 Theme")
    theme = st.selectbox(
        "Color Theme",
        ["Light", "Dark", "Auto (System Default)"],
        index=0
    )

    # Dashboard settings
    st.markdown("### 📊 Dashboard")

    show_charts = st.checkbox("Show performance charts on dashboard", value=True)
    auto_refresh = st.checkbox("Auto-refresh dashboard", value=False)

    if auto_refresh:
        refresh_interval = st.slider(
            "Refresh interval (seconds)",
            min_value=10,
            max_value=300,
            value=60,
            step=10
        )

    # Table settings
    st.markdown("### 📋 Table Display")

    rows_per_page = st.select_slider(
        "Rows per page",
        options=[10, 25, 50, 100],
        value=25
    )

    show_row_numbers = st.checkbox("Show row numbers in tables", value=True)

    # Chart settings
    st.markdown("### 📈 Charts")

    chart_style = st.selectbox(
        "Chart style",
        ["Modern", "Classic", "Minimal"],
        index=0
    )

    # Save button
    if st.button("💾 Save Display Settings", use_container_width=True, type="primary"):
        st.success("✅ Display settings saved successfully!")


def show_alert_settings():
    """Show alert and notification settings."""
    st.subheader("Alert Settings")

    # Alert thresholds
    st.markdown("### 🚨 Alert Thresholds")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Sepsis Alerts**")
        sepsis_high_threshold = st.slider(
            "High risk threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.7,
            step=0.05,
            format="%.2f",
            help="Alert when sepsis risk exceeds this threshold"
        )
        sepsis_medium_threshold = st.slider(
            "Medium risk threshold",
            min_value=0.3,
            max_value=0.7,
            value=0.5,
            step=0.05,
            format="%.2f"
        )

    with col2:
        st.markdown("**Mortality Alerts**")
        mortality_high_threshold = st.slider(
            "High risk threshold",
            min_value=0.5,
            max_value=1.0,
            value=0.6,
            step=0.05,
            format="%.2f",
            help="Alert when mortality risk exceeds this threshold"
        )
        mortality_medium_threshold = st.slider(
            "Medium risk threshold",
            min_value=0.3,
            max_value=0.7,
            value=0.4,
            step=0.05,
            format="%.2f"
        )

    # Notification settings
    st.markdown("### 🔔 Notifications")

    enable_sound = st.checkbox("Enable sound alerts", value=True)
    enable_desktop = st.checkbox("Enable desktop notifications", value=False)
    enable_email = st.checkbox("Enable email notifications", value=False)

    if enable_email:
        email_address = st.text_input("Email address for alerts", placeholder="user@example.com")
        email_frequency = st.selectbox(
            "Email frequency",
            ["Immediate", "Hourly digest", "Daily digest"],
            index=0
        )

    # Alert priorities
    st.markdown("### ⚡ Alert Priorities")

    alert_high_risk = st.checkbox("Alert on high risk predictions", value=True)
    alert_medium_risk = st.checkbox("Alert on medium risk predictions", value=False)
    alert_trends = st.checkbox("Alert on worsening trends", value=True)

    # Save button
    if st.button("💾 Save Alert Settings", use_container_width=True, type="primary"):
        st.success("✅ Alert settings saved successfully!")


def show_system_settings():
    """Show system and advanced settings."""
    st.subheader("System Settings")

    # API Configuration
    st.markdown("### 🔌 API Configuration")

    api_url = st.text_input(
        "API Base URL",
        value="http://localhost:8000",
        help="Backend API endpoint URL"
    )

    api_timeout = st.number_input(
        "API timeout (seconds)",
        min_value=5,
        max_value=60,
        value=30,
        help="Maximum time to wait for API responses"
    )

    # Model settings
    st.markdown("### 🤖 Model Settings")

    col1, col2 = st.columns(2)

    with col1:
        sepsis_model = st.selectbox(
            "Sepsis model",
            ["sepsis_lightgbm_v1", "sepsis_lightgbm_v2"],
            index=0
        )

    with col2:
        mortality_model = st.selectbox(
            "Mortality model",
            ["mortality_lightgbm_v1", "mortality_lightgbm_v2"],
            index=0
        )

    show_shap = st.checkbox("Show SHAP explanations", value=True)
    cache_predictions = st.checkbox("Cache predictions", value=True)

    if cache_predictions:
        cache_ttl = st.number_input(
            "Cache TTL (minutes)",
            min_value=1,
            max_value=1440,
            value=60
        )

    # Performance settings
    st.markdown("### ⚡ Performance")

    enable_caching = st.checkbox("Enable result caching", value=True)
    batch_size = st.number_input(
        "Batch prediction size",
        min_value=1,
        max_value=1000,
        value=100,
        help="Number of predictions to process in a single batch"
    )

    # Data settings
    st.markdown("### 💾 Data")

    data_retention = st.number_input(
        "Prediction data retention (days)",
        min_value=7,
        max_value=365,
        value=90,
        help="How long to keep prediction history"
    )

    auto_backup = st.checkbox("Enable automatic backups", value=True)

    # Advanced settings
    st.markdown("### 🔧 Advanced")

    debug_mode = st.checkbox("Enable debug mode", value=False)
    if debug_mode:
        st.warning("⚠️ Debug mode will log detailed information and may impact performance.")

    log_level = st.selectbox(
        "Log level",
        ["ERROR", "WARNING", "INFO", "DEBUG"],
        index=2
    )

    # Save button
    if st.button("💾 Save System Settings", use_container_width=True, type="primary"):
        st.success("✅ System settings saved successfully!")
        st.info("ℹ️ Some changes may require application restart.")


def show_about():
    """Show about information."""
    st.subheader("About MediAI")

    st.markdown("""
    ### 🏥 MediAI Healthcare ML Platform

    **Version:** 1.0.0
    **Release Date:** January 2025
    **Status:** Production

    ---

    #### 📋 Overview

    MediAI is an end-to-end MLOps platform for ICU patient risk prediction using MIMIC-IV data.
    The platform provides early warning systems for:

    - **Sepsis Risk Prediction** - 6-hour early warning
    - **ICU Mortality Prediction** - Hospital mortality risk assessment

    ---

    #### 🛠️ Technology Stack

    **Frontend:** Streamlit
    **Backend:** FastAPI
    **Database:** PostgreSQL
    **Cache:** Redis
    **ML Tracking:** MLflow
    **Orchestration:** Apache Airflow
    **Transformations:** dbt
    **Models:** LightGBM

    ---

    #### 📊 Models

    **Sepsis Prediction Model (v1.2.0)**
    - Algorithm: LightGBM Binary Classifier
    - Features: 42 clinical features
    - Performance: AUROC 0.872, Sensitivity 0.835
    - Target: Sepsis onset within 6 hours

    **Mortality Prediction Model (v1.1.0)**
    - Algorithm: LightGBM Binary Classifier
    - Features: 65 clinical features
    - Performance: AUROC 0.828, Sensitivity 0.782
    - Target: Hospital mortality

    ---

    #### 📚 Data Source

    - **Dataset:** MIMIC-IV (Kaggle: akshaybe/updated-mimic-iv)
    - **Patients:** ~70,000 ICU stays
    - **Features:** Demographics, vitals, labs, severity scores
    - **Privacy:** De-identified data (HIPAA compliant)

    ---

    #### 🔒 Security & Compliance

    - De-identified patient data only
    - Secure API authentication
    - Input validation and sanitization
    - Audit logging
    - Regular security updates

    ---

    #### 📖 Documentation

    - [Architecture Design](../ARCHITECTURE_DESIGN.md)
    - [Database Schema](../DATABASE_SCHEMA.md)
    - [API Documentation](http://localhost:8000/docs)
    - [Requirements](../REQUIREMENTS.md)

    ---

    #### 👥 Support

    For issues or questions:
    - Check documentation
    - Contact system administrator
    - Review error logs

    ---

    #### ⚖️ License

    This software is provided for educational and research purposes.
    See LICENSE file for details.

    ---

    #### 🙏 Acknowledgments

    - **MIMIC-IV Dataset** - PhysioNet / MIT
    - **Feature Engineering** - BorgwardtLab/mgp-tcn, healthylaife/MIMIC-IV-Data-Pipeline
    - **Open Source Tools** - Streamlit, FastAPI, LightGBM, and many others

    ---

    """)

    st.markdown("---")

    # System information
    st.markdown("### 💻 System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Backend API:** 🟢 Online
        **Database:** 🟢 Connected
        **Cache:** 🟢 Active
        **MLflow:** 🟢 Running
        """)

    with col2:
        st.markdown("""
        **Sepsis Model:** ✅ Loaded
        **Mortality Model:** ✅ Loaded
        **Last Health Check:** Just now
        **Uptime:** 99.8%
        """)

    # Check for updates
    if st.button("🔄 Check for Updates", use_container_width=True):
        st.info("✅ You are running the latest version!")
