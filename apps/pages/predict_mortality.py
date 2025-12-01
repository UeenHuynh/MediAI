"""
Mortality Prediction Page
Predict ICU mortality risk using 13 clinical features
"""

import streamlit as st
from datetime import datetime
from utils.audit_logger import AuditEventType
from services.model_service import get_model_service


def show_mortality_prediction():
    """Mortality prediction page"""

    st.markdown('<div class="page-header">💔 ICU Mortality Risk Prediction</div>', unsafe_allow_html=True)

    st.info("""
    **Hospital Mortality Risk Assessment**

    Predicts hospital mortality risk using 13 key features:
    - Demographics (age, gender)
    - Worst vitals/labs in first 24 hours
    - Clinical scores (SOFA Day 1, APACHE-II)
    - Vasopressor use
    """)

    # Initialize session state for patient ID if not exists
    if 'mort_patient_id' not in st.session_state:
        st.session_state.mort_patient_id = "P-MORT-001"

    st.markdown("---")

    # Form for mortality prediction
    with st.form("mortality_prediction_form"):
        st.markdown("### 👤 Patient Demographics")

        col1, col2, col3 = st.columns(3)

        with col1:
            patient_id = st.text_input("Patient ID*", value=st.session_state.mort_patient_id, key="mort_pid")
        with col2:
            age = st.number_input("Age (years)*", min_value=18, max_value=120, value=65, key="mort_age")
        with col3:
            gender = st.selectbox("Gender*", ["M", "F"], key="mort_gender")

        st.markdown("---")
        st.markdown("### 📊 Worst Values in First 24 Hours")
        st.caption("Enter the WORST (most abnormal) values observed in the first 24 hours of ICU admission")

        col1, col2, col3 = st.columns(3)

        with col1:
            worst_hr = st.number_input("Worst Heart Rate (bpm)", min_value=20, max_value=250, value=100, key="mort_hr")
            worst_sbp = st.number_input("Worst SBP Low (mmHg)", min_value=40, max_value=200, value=100, key="mort_sbp")
            worst_temp = st.number_input("Worst Temp High (°C)", min_value=34.0, max_value=42.0, value=37.5, step=0.1, key="mort_temp")

        with col2:
            worst_rr = st.number_input("Worst Resp Rate (bpm)", min_value=4, max_value=60, value=20, key="mort_rr")
            worst_spo2 = st.number_input("Worst SpO2 (%)", min_value=50, max_value=100, value=95, key="mort_spo2")
            worst_gcs = st.number_input("Worst GCS", min_value=3, max_value=15, value=14, key="mort_gcs")

        with col3:
            worst_lactate = st.number_input("Worst Lactate (mmol/L)", min_value=0.0, max_value=20.0, value=2.0, step=0.1, key="mort_lac")
            worst_creat = st.number_input("Worst Creatinine (mg/dL)", min_value=0.1, max_value=15.0, value=1.2, step=0.1, key="mort_creat")

        st.markdown("---")
        st.markdown("### 🏥 Clinical Scores & Interventions")

        col1, col2, col3 = st.columns(3)

        with col1:
            sofa_day1 = st.number_input("SOFA Score (Day 1)", min_value=0, max_value=24, value=3, help="Sequential Organ Failure Assessment score on Day 1", key="mort_sofa")

        with col2:
            apache_ii = st.number_input("APACHE-II Score", min_value=0, max_value=71, value=10, help="Acute Physiology and Chronic Health Evaluation II score", key="mort_apache")

        with col3:
            vasopressor = st.checkbox("Vasopressor Use", value=False, help="Did patient receive vasopressors (norepinephrine, epinephrine, etc)?", key="mort_vaso")

        st.markdown("---")

        # Submit button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "💔 Predict Mortality Risk",
                use_container_width=True
            )

        if submitted:
            st.session_state.mort_patient_id = patient_id
            handle_mortality_prediction()


def handle_mortality_prediction():
    """Handle mortality prediction submission"""

    # Build request data from session state
    request_data = {
        "patient_id": st.session_state.mort_pid,
        "features": {
            "age": st.session_state.mort_age,
            "gender": st.session_state.mort_gender,
            "worst_heart_rate": st.session_state.mort_hr,
            "worst_sbp_low": st.session_state.mort_sbp,
            "worst_temperature_high": st.session_state.mort_temp,
            "worst_respiratory_rate": st.session_state.mort_rr,
            "worst_spo2": st.session_state.mort_spo2,
            "worst_gcs": st.session_state.mort_gcs,
            "worst_lactate": st.session_state.mort_lac,
            "worst_creatinine": st.session_state.mort_creat,
            "sofa_day1": st.session_state.mort_sofa,
            "apache_ii_score": st.session_state.mort_apache,
            "vasopressor_use": st.session_state.mort_vaso
        }
    }

    # Log prediction request
    audit = st.session_state.audit_logger
    audit.log_event(
        event_type=AuditEventType.PREDICT_MORTALITY,
        user_id=st.session_state.user_id,
        patient_id=st.session_state.mort_pid,
        ip_address='127.0.0.1',
        details={'model': 'mortality'}
    )

    # Use local model for prediction
    with st.spinner("💔 Analyzing patient mortality risk..."):
        try:
            # Get model service
            model_service = get_model_service()

            # Run prediction
            prediction_result = model_service.predict_mortality(request_data['features'])

            # Format result to match expected structure
            result = {
                'prediction': {
                    'risk_score': prediction_result.get('risk_score', 0.5),
                    'risk_level': prediction_result.get('risk_level', 'Unknown').upper(),
                    'recommendation': prediction_result.get('recommendation', ''),
                },
                'metadata': {
                    'model_version': prediction_result.get('model_version', 'mortality_lightgbm_v1'),
                    'features_used': prediction_result.get('features_used', 13),
                    'prediction_time': datetime.now().isoformat()
                }
            }

            # Add error info if present
            if 'error' in prediction_result:
                result['metadata']['error'] = prediction_result['error']
                st.warning(f"⚠️ Model warning: {prediction_result['error']}")

            show_mortality_result(result)

        except Exception as e:
            st.error(f"❌ Model prediction error: {str(e)}")


def show_mortality_result(result: dict):
    """Display mortality prediction results"""

    st.markdown("---")
    st.success("✅ Mortality Prediction Complete")

    prediction = result.get('prediction', {})
    risk_score = prediction.get('risk_score', 0)
    risk_level = prediction.get('risk_level', 'UNKNOWN')

    col1, col2 = st.columns([1, 2])

    with col1:
        # Risk gauge
        import plotly.graph_objects as go

        color_map = {
            'LOW': '#10b981',
            'MEDIUM': '#f59e0b',
            'HIGH': '#ef4444',
            'CRITICAL': '#dc2626'
        }

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_score * 100,
            title={'text': "Mortality Risk (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color_map.get(risk_level, '#6b7280')},
                'steps': [
                    {'range': [0, 20], 'color': "#d1fae5"},
                    {'range': [20, 50], 'color': "#fef3c7"},
                    {'range': [50, 75], 'color': "#fed7aa"},
                    {'range': [75, 100], 'color': "#fee2e2"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 75}
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"## Risk Level: {risk_level}")
        st.markdown(f"**Mortality Risk:** {risk_score:.1%}")
        st.markdown("**Recommendation:**")
        st.info(prediction.get('recommendation', 'N/A'))

        # Risk interpretation
        st.markdown("### 📊 Risk Interpretation")
        if risk_level == "CRITICAL":
            st.error("🔴 **Very High Risk (>75%)**: Intensive care and family discussion recommended")
        elif risk_level == "HIGH":
            st.warning("🟠 **High Risk (50-75%)**: Close monitoring and treatment escalation needed")
        elif risk_level == "MEDIUM":
            st.warning("🟡 **Medium Risk (20-50%)**: Continue current treatment, monitor closely")
        else:
            st.success("🟢 **Low Risk (<20%)**: Continue routine ICU care")

    with st.expander("ℹ️ Prediction Metadata"):
        st.json(result.get('metadata', {}))

    st.markdown("---")

    # Clinical context
    st.markdown("### 📋 Clinical Context")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Key Risk Factors for ICU Mortality:**
        - Advanced age (>70 years)
        - High SOFA/APACHE-II scores
        - Severe vital sign abnormalities
        - Vasopressor requirement
        - Multiple organ dysfunction
        """)

    with col2:
        st.markdown("""
        **Model Details:**
        - Algorithm: LightGBM (Gradient Boosting)
        - Features: 13 clinical variables
        - Training: MIMIC-IV ICU data
        - Performance: AUROC 0.85+
        """)
