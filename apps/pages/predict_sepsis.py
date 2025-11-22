"""
Sepsis Prediction Page
Form for sepsis risk prediction with 42 clinical features
"""

import streamlit as st
import requests
import os
from utils.audit_logger import AuditEventType
from utils.encryption import DataEncryption

API_URL = os.getenv("API_URL", "http://localhost:8000")


def show_sepsis_prediction():
    """Sepsis prediction page"""

    st.markdown('<div class="page-header">🔬 Sepsis Risk Prediction</div>', unsafe_allow_html=True)

    st.info("""
    **Sepsis Early Warning System**

    Predicts sepsis onset within 6 hours using 42 clinical features:
    - Demographics (age, gender, BMI)
    - Vital signs (HR, BP, temp, RR, SpO2)
    - Laboratory values (WBC, lactate, creatinine, etc.)
    - SOFA scores (6 organ systems)
    - Temporal trends (6-12 hour changes)
    """)

    # Create form with tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Demographics & Vitals",
        "🧪 Laboratory Values",
        "📊 SOFA Scores",
        "📈 Trends & Time"
    ])

    with st.form("sepsis_prediction_form"):

        with tab1:
            show_demographics_vitals()

        with tab2:
            show_laboratory_values()

        with tab3:
            show_sofa_scores()

        with tab4:
            show_trends_time()

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🔬 Predict Sepsis Risk",
                use_container_width=True
            )

        if submitted:
            handle_prediction()


def show_demographics_vitals():
    """Demographics and vital signs inputs"""

    st.markdown("### 👤 Patient Information")
    col1, col2, col3 = st.columns(3)

    with col1:
        patient_id = st.text_input("Patient ID*", value="P-TEST-001", key="patient_id")
    with col2:
        age = st.number_input("Age (years)*", min_value=18, max_value=120, value=65, key="age")
    with col3:
        gender = st.selectbox("Gender*", ["M", "F"], key="gender")

    bmi = st.number_input("BMI*", min_value=10.0, max_value=60.0, value=25.5, step=0.1, key="bmi")

    st.markdown("### 🫀 Vital Signs")
    col1, col2, col3 = st.columns(3)

    with col1:
        heart_rate = st.number_input("Heart Rate (bpm)*", min_value=0, max_value=300, value=95, key="hr")
        sbp = st.number_input("Systolic BP (mmHg)*", min_value=40, max_value=250, value=120, key="sbp")

    with col2:
        dbp = st.number_input("Diastolic BP (mmHg)*", min_value=20, max_value=150, value=80, key="dbp")
        temperature = st.number_input("Temperature (°C)*", min_value=32.0, max_value=42.0, value=37.0, step=0.1, key="temp")

    with col3:
        respiratory_rate = st.number_input("Respiratory Rate*", min_value=0, max_value=60, value=16, key="rr")
        spo2 = st.number_input("SpO2 (%)", min_value=0, max_value=100, value=98, key="spo2")


def show_laboratory_values():
    """Laboratory values inputs"""

    st.markdown("### 🧪 Required Lab Values")
    col1, col2, col3 = st.columns(3)

    with col1:
        wbc = st.number_input("WBC (×10⁹/L)*", min_value=0.0, max_value=100.0, value=10.5, step=0.1, key="wbc")
        platelets = st.number_input("Platelets (×10⁹/L)*", min_value=0.0, max_value=1000.0, value=250.0, step=1.0, key="platelets")
        hemoglobin = st.number_input("Hemoglobin (g/dL)*", min_value=0.0, max_value=25.0, value=13.5, step=0.1, key="hgb")

    with col2:
        lactate = st.number_input("Lactate (mmol/L)*", min_value=0.0, max_value=30.0, value=1.5, step=0.1, key="lactate")
        creatinine = st.number_input("Creatinine (mg/dL)*", min_value=0.0, max_value=20.0, value=1.0, step=0.1, key="creat")
        bilirubin = st.number_input("Bilirubin (mg/dL)*", min_value=0.0, max_value=50.0, value=0.8, step=0.1, key="bili")

    with col3:
        sodium = st.number_input("Sodium (mmol/L)*", min_value=100.0, max_value=180.0, value=140.0, step=0.1, key="na")
        potassium = st.number_input("Potassium (mmol/L)*", min_value=2.0, max_value=8.0, value=4.0, step=0.1, key="k")
        glucose = st.number_input("Glucose (mg/dL)*", min_value=0.0, max_value=1000.0, value=100.0, step=1.0, key="glucose")

    st.markdown("### 🧪 Optional Lab Values")
    col1, col2, col3 = st.columns(3)

    with col1:
        bicarbonate = st.number_input("Bicarbonate (mmol/L)", min_value=0.0, max_value=50.0, value=24.0, step=0.1, key="hco3")
        pao2 = st.number_input("PaO2 (mmHg)", min_value=0.0, max_value=700.0, value=0.0, step=1.0, key="pao2")

    with col2:
        paco2 = st.number_input("PaCO2 (mmHg)", min_value=0.0, max_value=150.0, value=0.0, step=1.0, key="paco2")
        ph = st.number_input("pH", min_value=6.8, max_value=8.0, value=0.0, step=0.01, key="ph")

    with col3:
        albumin = st.number_input("Albumin (g/dL)", min_value=0.0, max_value=6.0, value=0.0, step=0.1, key="albumin")
        troponin = st.number_input("Troponin (ng/mL)", min_value=0.0, max_value=100.0, value=0.0, step=0.01, key="trop")


def show_sofa_scores():
    """SOFA score inputs"""

    st.markdown("### 📊 SOFA Scores (Sequential Organ Failure Assessment)")
    st.info("Score each organ system from 0 (normal) to 4 (severe dysfunction)")

    col1, col2, col3 = st.columns(3)

    with col1:
        respiratory_sofa = st.select_slider(
            "Respiratory",
            options=[0, 1, 2, 3, 4],
            value=0,
            key="sofa_resp"
        )
        cardiovascular_sofa = st.select_slider(
            "Cardiovascular",
            options=[0, 1, 2, 3, 4],
            value=0,
            key="sofa_cardio"
        )

    with col2:
        hepatic_sofa = st.select_slider(
            "Hepatic",
            options=[0, 1, 2, 3, 4],
            value=0,
            key="sofa_hepatic"
        )
        coagulation_sofa = st.select_slider(
            "Coagulation",
            options=[0, 1, 2, 3, 4],
            value=0,
            key="sofa_coag"
        )

    with col3:
        renal_sofa = st.select_slider(
            "Renal",
            options=[0, 1, 2, 3, 4],
            value=0,
            key="sofa_renal"
        )
        neurological_sofa = st.select_slider(
            "Neurological (GCS)",
            options=[0, 1, 2, 3, 4],
            value=0,
            key="sofa_neuro"
        )

    total_sofa = (respiratory_sofa + cardiovascular_sofa + hepatic_sofa +
                  coagulation_sofa + renal_sofa + neurological_sofa)

    st.metric("Total SOFA Score", total_sofa)


def show_trends_time():
    """Temporal trends and time features"""

    st.markdown("### 📈 Temporal Trends (Changes over time)")
    st.info("Enter the change in value over the specified time period (positive = increase, negative = decrease)")

    col1, col2 = st.columns(2)

    with col1:
        lactate_trend_12h = st.number_input(
            "Lactate Trend (12h)",
            min_value=-10.0, max_value=10.0, value=0.0, step=0.1,
            key="lactate_trend_12h"
        )
        hr_trend_6h = st.number_input(
            "HR Trend (6h)",
            min_value=-100.0, max_value=100.0, value=0.0, step=1.0,
            key="hr_trend_6h"
        )
        wbc_trend_12h = st.number_input(
            "WBC Trend (12h)",
            min_value=-50.0, max_value=50.0, value=0.0, step=0.1,
            key="wbc_trend_12h"
        )

    with col2:
        sbp_trend_6h = st.number_input(
            "SBP Trend (6h)",
            min_value=-100.0, max_value=100.0, value=0.0, step=1.0,
            key="sbp_trend_6h"
        )
        temperature_trend_6h = st.number_input(
            "Temperature Trend (6h)",
            min_value=-5.0, max_value=5.0, value=0.0, step=0.1,
            key="temp_trend_6h"
        )
        rr_trend_6h = st.number_input(
            "RR Trend (6h)",
            min_value=-30.0, max_value=30.0, value=0.0, step=1.0,
            key="rr_trend_6h"
        )

    st.markdown("### ⏰ Time Features")
    col1, col2 = st.columns(2)

    with col1:
        hour_of_admission = st.slider(
            "Hour of Admission (0-23)",
            min_value=0, max_value=23, value=12,
            key="hour_admission"
        )

    with col2:
        icu_los_so_far = st.number_input(
            "ICU Length of Stay (hours)",
            min_value=0.0, max_value=2000.0, value=12.0, step=0.5,
            key="icu_los"
        )


def handle_prediction():
    """Handle sepsis prediction submission"""

    # Build request data from session state
    request_data = {
        "patient_id": st.session_state.patient_id,
        "features": {
            "age": st.session_state.age,
            "gender": st.session_state.gender,
            "bmi": st.session_state.bmi,
            "heart_rate": st.session_state.hr,
            "sbp": st.session_state.sbp,
            "dbp": st.session_state.dbp,
            "temperature": st.session_state.temp,
            "respiratory_rate": st.session_state.rr,
            "wbc": st.session_state.wbc,
            "lactate": st.session_state.lactate,
            "creatinine": st.session_state.creat,
            "platelets": st.session_state.platelets,
            "bilirubin": st.session_state.bili,
            "sodium": st.session_state.na,
            "potassium": st.session_state.k,
            "glucose": st.session_state.glucose,
            "hemoglobin": st.session_state.hgb,
            "bicarbonate": st.session_state.hco3 if st.session_state.hco3 > 0 else None,
            "pao2": st.session_state.pao2 if st.session_state.pao2 > 0 else None,
            "paco2": st.session_state.paco2 if st.session_state.paco2 > 0 else None,
            "ph": st.session_state.ph if st.session_state.ph > 0 else None,
            "albumin": st.session_state.albumin if st.session_state.albumin > 0 else None,
            "troponin": st.session_state.trop if st.session_state.trop > 0 else None,
            "respiratory_sofa": st.session_state.sofa_resp,
            "cardiovascular_sofa": st.session_state.sofa_cardio,
            "hepatic_sofa": st.session_state.sofa_hepatic,
            "coagulation_sofa": st.session_state.sofa_coag,
            "renal_sofa": st.session_state.sofa_renal,
            "neurological_sofa": st.session_state.sofa_neuro,
            "lactate_trend_12h": st.session_state.lactate_trend_12h,
            "hr_trend_6h": st.session_state.hr_trend_6h,
            "wbc_trend_12h": st.session_state.wbc_trend_12h,
            "sbp_trend_6h": st.session_state.sbp_trend_6h,
            "temperature_trend_6h": st.session_state.temp_trend_6h,
            "rr_trend_6h": st.session_state.rr_trend_6h,
            "hour_of_admission": st.session_state.hour_admission,
            "icu_los_so_far": st.session_state.icu_los
        }
    }

    # Log prediction request
    audit = st.session_state.audit_logger
    audit.log_event(
        event_type=AuditEventType.PREDICT_SEPSIS,
        user_id=st.session_state.user_id,
        patient_id=st.session_state.patient_id,
        ip_address='127.0.0.1',
        details={'model': 'sepsis'}
    )

    # Call API
    with st.spinner("🔬 Analyzing patient data..."):
        try:
            response = requests.post(
                f"{API_URL}/api/v1/predict/sepsis",
                json=request_data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                show_prediction_result(result, "Sepsis")
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.json(response.json())

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Using mock prediction for demo.")
            show_mock_prediction(request_data)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def show_prediction_result(result: dict, model_type: str):
    """Display prediction results"""

    st.markdown("---")
    st.success(f"✅ {model_type} Prediction Complete")

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
            title={'text': f"{model_type} Risk (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color_map.get(risk_level, '#6b7280')},
                'steps': [
                    {'range': [0, 20], 'color': "#d1fae5"},
                    {'range': [20, 50], 'color': "#fef3c7"},
                    {'range': [50, 80], 'color': "#fed7aa"},
                    {'range': [80, 100], 'color': "#fee2e2"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"## Risk Level: {risk_level}")
        st.markdown(f"**Risk Score:** {risk_score:.1%}")
        st.markdown(f"**Recommendation:** {prediction.get('recommendation', 'N/A')}")

        st.markdown("### 📊 Top Contributing Features")
        if 'top_features' in result:
            import pandas as pd
            features_df = pd.DataFrame(result['top_features'])
            if not features_df.empty:
                st.dataframe(features_df, use_container_width=True)

    with st.expander("ℹ️ Prediction Metadata"):
        st.json(result.get('metadata', {}))


def show_mock_prediction(request_data: dict):
    """Show mock prediction when API is unavailable"""

    import random
    import numpy as np

    # Simple risk scoring based on vitals
    hr = request_data['features']['heart_rate']
    temp = request_data['features']['temperature']
    lactate = request_data['features']['lactate']
    wbc = request_data['features']['wbc']

    risk_score = 0.0
    if hr > 100: risk_score += 0.2
    if temp > 38: risk_score += 0.3
    if lactate > 2: risk_score += 0.25
    if wbc > 12: risk_score += 0.15

    risk_score = min(risk_score + random.uniform(0, 0.1), 1.0)

    if risk_score >= 0.8:
        risk_level = 'CRITICAL'
    elif risk_score >= 0.5:
        risk_level = 'HIGH'
    elif risk_score >= 0.2:
        risk_level = 'MEDIUM'
    else:
        risk_level = 'LOW'

    mock_result = {
        'prediction': {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'recommendation': f"Risk level {risk_level} - Monitor closely"
        },
        'top_features': [
            {'feature': 'lactate', 'importance': 0.25},
            {'feature': 'heart_rate', 'importance': 0.20},
            {'feature': 'temperature', 'importance': 0.18}
        ],
        'metadata': {
            'model': 'mock_sepsis_model',
            'timestamp': str(np.datetime64('now')),
            'note': 'Mock prediction - API unavailable'
        }
    }

    show_prediction_result(mock_result, "Sepsis")
