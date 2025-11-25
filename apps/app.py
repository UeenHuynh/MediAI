"""
MediAI Streamlit Application
ICU Risk Prediction Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import os
from datetime import datetime

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="MediAI - ICU Risk Prediction",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF4B4B;
    }
    .risk-low { color: #28a745; }
    .risk-medium { color: #ffc107; }
    .risk-high { color: #fd7e14; }
    .risk-critical { color: #dc3545; }
    </style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Main application"""

    # Header
    st.markdown('<div class="main-header">🏥 MediAI - ICU Risk Prediction Platform</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/FF4B4B/FFFFFF?text=MediAI", use_column_width=True)
        st.markdown("### Navigation")

        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "🔬 Predict Sepsis", "💔 Predict Mortality", "📊 Model Performance"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### System Status")

        # API health check
        api_healthy = check_api_health()
        if api_healthy:
            st.success("✅ API: Online")
        else:
            st.error("❌ API: Offline")
            st.info(f"API URL: {API_URL}")

        st.markdown("---")
        st.markdown("### About")
        st.info("""
        **MediAI** uses machine learning to predict:
        - Sepsis risk (6-hour early warning)
        - ICU mortality risk

        Built with:
        - FastAPI
        - PostgreSQL
        - Redis
        - LightGBM
        - Streamlit
        """)

    # Page routing
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🔬 Predict Sepsis":
        show_sepsis_prediction()
    elif page == "💔 Predict Mortality":
        show_mortality_prediction()
    elif page == "📊 Model Performance":
        show_model_performance()


def show_dashboard():
    """Dashboard page"""
    st.header("📊 ICU Overview Dashboard")

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Patients", "1,247", delta="↑ 23")

    with col2:
        st.metric("High Risk", "87", delta="↓ 5", delta_color="inverse")

    with col3:
        st.metric("Sepsis Cases", "34", delta="↑ 2", delta_color="inverse")

    with col4:
        st.metric("Mortality Rate", "8.2%", delta="↓ 0.3%", delta_color="inverse")

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Distribution")
        risk_data = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High', 'Critical'],
            'Count': [850, 285, 87, 25]
        })

        fig = go.Figure(data=[
            go.Bar(
                x=risk_data['Risk Level'],
                y=risk_data['Count'],
                marker_color=['#28a745', '#ffc107', '#fd7e14', '#dc3545']
            )
        ])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Recent Predictions")
        recent_data = pd.DataFrame({
            'Patient ID': ['P-1001', 'P-1002', 'P-1003', 'P-1004', 'P-1005'],
            'Risk Score': [0.75, 0.45, 0.89, 0.32, 0.61],
            'Risk Level': ['HIGH', 'MEDIUM', 'CRITICAL', 'LOW', 'HIGH'],
            'Model': ['Sepsis', 'Mortality', 'Sepsis', 'Mortality', 'Sepsis']
        })
        st.dataframe(recent_data, use_container_width=True)


def show_sepsis_prediction():
    """Sepsis prediction page"""
    st.header("🔬 Sepsis Risk Prediction")

    st.info("**Sepsis Early Warning System**: Predicts sepsis onset within 6 hours using 42 clinical features")

    with st.form("sepsis_form"):
        st.subheader("Patient Information")

        col1, col2 = st.columns(2)

        with col1:
            patient_id = st.text_input("Patient ID", value="P-TEST-001")
            age = st.number_input("Age (years)", min_value=18, max_value=120, value=65)
            gender = st.selectbox("Gender", ["M", "F"])
            bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=25.5)

        with col2:
            st.markdown("### Vital Signs")
            heart_rate = st.number_input("Heart Rate (bpm)", min_value=0, max_value=300, value=95)
            sbp = st.number_input("Systolic BP (mmHg)", min_value=40, max_value=250, value=120)
            dbp = st.number_input("Diastolic BP (mmHg)", min_value=20, max_value=150, value=80)
            temperature = st.number_input("Temperature (°C)", min_value=32.0, max_value=42.0, value=37.0)
            respiratory_rate = st.number_input("Respiratory Rate", min_value=0, max_value=60, value=16)

        st.markdown("### Laboratory Values (Required)")
        col1, col2, col3 = st.columns(3)

        with col1:
            wbc = st.number_input("WBC (10^9/L)", min_value=0.0, max_value=100.0, value=10.5)
            lactate = st.number_input("Lactate (mmol/L)", min_value=0.0, max_value=30.0, value=1.5)
            creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.0, max_value=20.0, value=1.0)

        with col2:
            platelets = st.number_input("Platelets (10^9/L)", min_value=0.0, max_value=1000.0, value=250.0)
            bilirubin = st.number_input("Bilirubin (mg/dL)", min_value=0.0, max_value=50.0, value=0.8)
            sodium = st.number_input("Sodium (mmol/L)", min_value=100.0, max_value=180.0, value=140.0)

        with col3:
            potassium = st.number_input("Potassium (mmol/L)", min_value=2.0, max_value=8.0, value=4.0)
            glucose = st.number_input("Glucose (mg/dL)", min_value=0.0, max_value=1000.0, value=100.0)
            hemoglobin = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=25.0, value=13.5)

        # Simplified: Use default values for remaining features
        bicarbonate = 24.0
        pao2 = None
        paco2 = None
        ph = None
        anion_gap = None
        albumin = None
        troponin = None
        bnp = None
        inr = None
        ast = None
        alt = None

        st.markdown("### SOFA Scores")
        col1, col2, col3 = st.columns(3)
        with col1:
            respiratory_sofa = st.number_input("Respiratory", min_value=0, max_value=4, value=0)
            cardiovascular_sofa = st.number_input("Cardiovascular", min_value=0, max_value=4, value=0)
        with col2:
            hepatic_sofa = st.number_input("Hepatic", min_value=0, max_value=4, value=0)
            coagulation_sofa = st.number_input("Coagulation", min_value=0, max_value=4, value=0)
        with col3:
            renal_sofa = st.number_input("Renal", min_value=0, max_value=4, value=0)
            neurological_sofa = st.number_input("Neurological", min_value=0, max_value=4, value=0)

        st.markdown("### Temporal Trends & Time Features")
        col1, col2 = st.columns(2)
        with col1:
            lactate_trend_12h = st.number_input("Lactate Trend (12h)", value=0.0)
            hr_trend_6h = st.number_input("HR Trend (6h)", value=0.0)
            wbc_trend_12h = st.number_input("WBC Trend (12h)", value=0.0)
        with col2:
            sbp_trend_6h = st.number_input("SBP Trend (6h)", value=0.0)
            temperature_trend_6h = st.number_input("Temp Trend (6h)", value=0.0)
            rr_trend_6h = st.number_input("RR Trend (6h)", value=0.0)

        hour_of_admission = st.slider("Hour of Admission", 0, 23, 12)
        icu_los_so_far = st.number_input("ICU LOS so far (hours)", min_value=0.0, value=12.0)

        submitted = st.form_submit_button("🔬 Predict Sepsis Risk", use_container_width=True)

        if submitted:
            # Build request
            request_data = {
                "patient_id": patient_id,
                "features": {
                    "age": age,
                    "gender": gender,
                    "bmi": bmi,
                    "heart_rate": heart_rate,
                    "sbp": sbp,
                    "dbp": dbp,
                    "temperature": temperature,
                    "respiratory_rate": respiratory_rate,
                    "wbc": wbc,
                    "lactate": lactate,
                    "creatinine": creatinine,
                    "platelets": platelets,
                    "bilirubin": bilirubin,
                    "sodium": sodium,
                    "potassium": potassium,
                    "glucose": glucose,
                    "hemoglobin": hemoglobin,
                    "bicarbonate": bicarbonate,
                    "pao2": pao2,
                    "paco2": paco2,
                    "ph": ph,
                    "anion_gap": anion_gap,
                    "albumin": albumin,
                    "troponin": troponin,
                    "bnp": bnp,
                    "inr": inr,
                    "ast": ast,
                    "alt": alt,
                    "respiratory_sofa": respiratory_sofa,
                    "cardiovascular_sofa": cardiovascular_sofa,
                    "hepatic_sofa": hepatic_sofa,
                    "coagulation_sofa": coagulation_sofa,
                    "renal_sofa": renal_sofa,
                    "neurological_sofa": neurological_sofa,
                    "lactate_trend_12h": lactate_trend_12h,
                    "hr_trend_6h": hr_trend_6h,
                    "wbc_trend_12h": wbc_trend_12h,
                    "sbp_trend_6h": sbp_trend_6h,
                    "temperature_trend_6h": temperature_trend_6h,
                    "rr_trend_6h": rr_trend_6h,
                    "hour_of_admission": hour_of_admission,
                    "icu_los_so_far": icu_los_so_far
                }
            }

            # Call API
            with st.spinner("Analyzing patient data..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/v1/predict/sepsis",
                        json=request_data,
                        timeout=10
                    )

                    if response.status_code == 200:
                        result = response.json()
                        show_prediction_result(result, "Sepsis")
                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.json(response.json())

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Make sure the API service is running.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def show_mortality_prediction():
    """Mortality prediction page (simplified)"""
    st.header("💔 Mortality Risk Prediction")
    st.info("This page would contain a similar form for mortality prediction with 65 features")
    st.warning("Implementation in progress - Use Sepsis Prediction for demo")


def show_model_performance():
    """Model performance metrics page"""
    st.header("📊 Model Performance Metrics")

    tab1, tab2 = st.tabs(["Sepsis Model", "Mortality Model"])

    with tab1:
        st.subheader("Sepsis Model Performance")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AUROC", "0.87")
        with col2:
            st.metric("Sensitivity", "0.82")
        with col3:
            st.metric("Specificity", "0.85")

        st.markdown("### Model Information")
        st.json({
            "model_name": "sepsis_lightgbm_v1",
            "algorithm": "LightGBM",
            "features": 42,
            "training_samples": "20,000",
            "target": "sepsis_onset_within_6h",
            "last_updated": "2025-01-20"
        })

    with tab2:
        st.subheader("Mortality Model Performance")
        st.info("Performance metrics will be displayed here")


def show_prediction_result(result: dict, model_type: str):
    """Display prediction results"""
    st.markdown("---")
    st.success("✅ Prediction Complete")

    # Main result
    prediction = result['prediction']
    risk_score = prediction['risk_score']
    risk_level = prediction['risk_level']

    # Risk gauge
    col1, col2 = st.columns([1, 2])

    with col1:
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Risk Score (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 20], 'color': "#28a745"},
                    {'range': [20, 50], 'color': "#ffc107"},
                    {'range': [50, 80], 'color': "#fd7e14"},
                    {'range': [80, 100], 'color': "#dc3545"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        risk_class = f"risk-{risk_level.lower()}"
        st.markdown(f'<h1 class="{risk_class}">Risk Level: {risk_level}</h1>', unsafe_allow_html=True)
        st.markdown(f"**Recommendation:** {prediction['recommendation']}")

        st.markdown("### Top Contributing Features")
        if 'top_features' in result:
            features_df = pd.DataFrame(result['top_features'])
            if not features_df.empty:
                st.dataframe(features_df, use_container_width=True)

    # Metadata
    with st.expander("ℹ️ Prediction Metadata"):
        st.json(result.get('metadata', {}))


if __name__ == "__main__":
    main()
