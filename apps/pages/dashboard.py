"""
Dashboard Page
Main monitoring dashboard with patient list and risk scores
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils.audit_logger import AuditEventType


# Mock patient data (adapted from UI.md MOCK_PATIENTS)
def get_mock_patients():
    """Generate mock patient data for demonstration"""
    return pd.DataFrame([
        {
            'patient_id': 'P-100234',
            'name': 'Nguyễn Văn A',
            'age': 65,
            'gender': 'M',
            'admission_time': '2 hours ago',
            'sepsis_score': 0.89,
            'mortality_score': 0.45,
            'sepsis_risk': 'CRITICAL',
            'mortality_risk': 'MEDIUM',
            'hr': 115,
            'bp_sys': 90,
            'bp_dia': 60,
            'spo2': 92,
            'temp': 38.9,
            'rr': 28,
            'wbc': 16.5,
            'lactate': 4.2,
            'creatinine': 1.8,
            'platelets': 120,
            'bilirubin': 2.1,
            'status': 'Active',
            'icu_unit': 'ICU-3'
        },
        {
            'patient_id': 'P-100235',
            'name': 'Trần Thị B',
            'age': 58,
            'gender': 'F',
            'admission_time': '5 hours ago',
            'sepsis_score': 0.72,
            'mortality_score': 0.38,
            'sepsis_risk': 'HIGH',
            'mortality_risk': 'MEDIUM',
            'hr': 105,
            'bp_sys': 95,
            'bp_dia': 65,
            'spo2': 94,
            'temp': 38.2,
            'rr': 24,
            'wbc': 14.2,
            'lactate': 3.5,
            'creatinine': 1.4,
            'platelets': 150,
            'bilirubin': 1.5,
            'status': 'Active',
            'icu_unit': 'ICU-2'
        },
        {
            'patient_id': 'P-100236',
            'name': 'Lê Văn C',
            'age': 72,
            'gender': 'M',
            'admission_time': '1 day ago',
            'sepsis_score': 0.35,
            'mortality_score': 0.52,
            'sepsis_risk': 'MEDIUM',
            'mortality_risk': 'MEDIUM',
            'hr': 88,
            'bp_sys': 120,
            'bp_dia': 75,
            'spo2': 96,
            'temp': 37.5,
            'rr': 18,
            'wbc': 11.5,
            'lactate': 2.1,
            'creatinine': 1.2,
            'platelets': 180,
            'bilirubin': 1.0,
            'status': 'Stable',
            'icu_unit': 'ICU-1'
        },
        {
            'patient_id': 'P-100237',
            'name': 'Phạm Thị D',
            'age': 45,
            'gender': 'F',
            'admission_time': '3 days ago',
            'sepsis_score': 0.15,
            'mortality_score': 0.22,
            'sepsis_risk': 'LOW',
            'mortality_risk': 'LOW',
            'hr': 75,
            'bp_sys': 125,
            'bp_dia': 80,
            'spo2': 98,
            'temp': 36.8,
            'rr': 16,
            'wbc': 9.5,
            'lactate': 1.2,
            'creatinine': 0.9,
            'platelets': 220,
            'bilirubin': 0.8,
            'status': 'Recovering',
            'icu_unit': 'ICU-1'
        },
        {
            'patient_id': 'P-100238',
            'name': 'Hoàng Văn E',
            'age': 80,
            'gender': 'M',
            'admission_time': '6 hours ago',
            'sepsis_score': 0.68,
            'mortality_score': 0.71,
            'sepsis_risk': 'HIGH',
            'mortality_risk': 'HIGH',
            'hr': 110,
            'bp_sys': 85,
            'bp_dia': 55,
            'spo2': 90,
            'temp': 39.2,
            'rr': 30,
            'wbc': 18.5,
            'lactate': 4.8,
            'creatinine': 2.2,
            'platelets': 95,
            'bilirubin': 2.8,
            'status': 'Critical',
            'icu_unit': 'ICU-3'
        }
    ])


def get_risk_color(risk_level: str) -> str:
    """Get color for risk level"""
    colors = {
        'LOW': '#10b981',
        'MEDIUM': '#f59e0b',
        'HIGH': '#ef4444',
        'CRITICAL': '#dc2626'
    }
    return colors.get(risk_level, '#6b7280')


def show_dashboard():
    """Main dashboard view (adapted from UI.md Dashboard)"""

    # Log page access
    audit = st.session_state.audit_logger
    audit.log_event(
        event_type=AuditEventType.VIEW_PATIENT,
        user_id=st.session_state.user_id,
        ip_address='127.0.0.1',
        details={'page': 'dashboard'}
    )

    st.markdown('<div class="page-header">🏠 ICU Patient Monitoring Dashboard</div>', unsafe_allow_html=True)

    # Get patient data
    patients_df = get_mock_patients()

    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Patients</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(len(patients_df)), unsafe_allow_html=True)

    with col2:
        critical_count = len(patients_df[patients_df['sepsis_risk'] == 'CRITICAL'])
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);">
            <div class="metric-label">Critical</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(critical_count), unsafe_allow_html=True)

    with col3:
        high_count = len(patients_df[patients_df['sepsis_risk'] == 'HIGH'])
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
            <div class="metric-label">High Risk</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(high_count), unsafe_allow_html=True)

    with col4:
        medium_count = len(patients_df[patients_df['sepsis_risk'] == 'MEDIUM'])
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
            <div class="metric-label">Medium Risk</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(medium_count), unsafe_allow_html=True)

    with col5:
        low_count = len(patients_df[patients_df['sepsis_risk'] == 'LOW'])
        st.markdown("""
        <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
            <div class="metric-label">Low Risk</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(low_count), unsafe_allow_html=True)

    st.markdown("---")

    # Filter controls
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search = st.text_input("🔍 Search Patient ID", placeholder="P-100234")

    with col2:
        risk_filter = st.multiselect(
            "Risk Level",
            options=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
            default=['CRITICAL', 'HIGH']
        )

    with col3:
        status_filter = st.multiselect(
            "Status",
            options=['Active', 'Stable', 'Critical', 'Recovering'],
            default=['Active', 'Critical']
        )

    with col4:
        icu_filter = st.multiselect(
            "ICU Unit",
            options=['ICU-1', 'ICU-2', 'ICU-3'],
            default=['ICU-1', 'ICU-2', 'ICU-3']
        )

    # Apply filters
    filtered_df = patients_df.copy()

    if search:
        filtered_df = filtered_df[filtered_df['patient_id'].str.contains(search, case=False)]

    if risk_filter:
        filtered_df = filtered_df[filtered_df['sepsis_risk'].isin(risk_filter)]

    if status_filter:
        filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]

    if icu_filter:
        filtered_df = filtered_df[filtered_df['icu_unit'].isin(icu_filter)]

    st.markdown(f"### 📊 Showing {len(filtered_df)} of {len(patients_df)} patients")

    # Patient table
    for idx, patient in filtered_df.iterrows():
        with st.expander(
            f"**{patient['patient_id']}** - {patient['name']} | "
            f"Sepsis: {patient['sepsis_score']:.2f} | "
            f"Mortality: {patient['mortality_score']:.2f}",
            expanded=(patient['sepsis_risk'] == 'CRITICAL')
        ):
            show_patient_detail(patient)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📈 Risk Distribution Over Time")
        show_risk_trend_chart()

    with col2:
        st.markdown("### 🎯 Sepsis vs Mortality Risk")
        show_risk_scatter(patients_df)


def show_patient_detail(patient: pd.Series):
    """Show detailed patient information"""

    # Log patient access
    audit = st.session_state.audit_logger
    audit.log_patient_access(
        user_id=st.session_state.user_id,
        patient_id=patient['patient_id'],
        action='view_detail',
        ip_address='127.0.0.1'
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 👤 Patient Information")
        st.write(f"**ID:** {patient['patient_id']}")
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']} years")
        st.write(f"**Gender:** {patient['gender']}")
        st.write(f"**ICU Unit:** {patient['icu_unit']}")
        st.write(f"**Admission:** {patient['admission_time']}")
        st.write(f"**Status:** {patient['status']}")

    with col2:
        st.markdown("#### 🫀 Vital Signs")
        st.metric("Heart Rate", f"{patient['hr']} bpm", delta=None if patient['hr'] < 100 else "High")
        st.metric("Blood Pressure", f"{patient['bp_sys']}/{patient['bp_dia']} mmHg")
        st.metric("SpO2", f"{patient['spo2']}%", delta=None if patient['spo2'] >= 95 else "Low")
        st.metric("Temperature", f"{patient['temp']}°C", delta=None if patient['temp'] < 38 else "Fever")
        st.metric("Respiratory Rate", f"{patient['rr']}/min", delta=None if patient['rr'] < 20 else "High")

    with col3:
        st.markdown("#### 🧪 Laboratory Values")
        st.metric("WBC", f"{patient['wbc']} ×10⁹/L", delta=None if patient['wbc'] < 12 else "High")
        st.metric("Lactate", f"{patient['lactate']} mmol/L", delta=None if patient['lactate'] < 2 else "High")
        st.metric("Creatinine", f"{patient['creatinine']} mg/dL", delta=None if patient['creatinine'] < 1.5 else "High")
        st.metric("Platelets", f"{patient['platelets']} ×10⁹/L", delta=None if patient['platelets'] > 150 else "Low")
        st.metric("Bilirubin", f"{patient['bilirubin']} mg/dL", delta=None if patient['bilirubin'] < 1.5 else "High")

    st.markdown("---")

    # Risk scores
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔬 Sepsis Risk")
        sepsis_color = get_risk_color(patient['sepsis_risk'])
        st.markdown(f"<h2 style='color: {sepsis_color};'>{patient['sepsis_score']:.1%}</h2>", unsafe_allow_html=True)
        st.markdown(f"**Risk Level:** <span style='color: {sepsis_color}; font-weight: bold;'>{patient['sepsis_risk']}</span>", unsafe_allow_html=True)

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=patient['sepsis_score'] * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Sepsis Risk (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': sepsis_color},
                'steps': [
                    {'range': [0, 20], 'color': "#d1fae5"},
                    {'range': [20, 50], 'color': "#fef3c7"},
                    {'range': [50, 80], 'color': "#fed7aa"},
                    {'range': [80, 100], 'color': "#fee2e2"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 80}
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 💔 Mortality Risk")
        mortality_color = get_risk_color(patient['mortality_risk'])
        st.markdown(f"<h2 style='color: {mortality_color};'>{patient['mortality_score']:.1%}</h2>", unsafe_allow_html=True)
        st.markdown(f"**Risk Level:** <span style='color: {mortality_color}; font-weight: bold;'>{patient['mortality_risk']}</span>", unsafe_allow_html=True)

        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=patient['mortality_score'] * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Mortality Risk (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': mortality_color},
                'steps': [
                    {'range': [0, 20], 'color': "#d1fae5"},
                    {'range': [20, 50], 'color': "#fef3c7"},
                    {'range': [50, 80], 'color': "#fed7aa"},
                    {'range': [80, 100], 'color': "#fee2e2"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}
            }
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Recommendation
    st.markdown("---")
    st.markdown("#### 💡 Recommendations")

    if patient['sepsis_risk'] == 'CRITICAL':
        st.error("""
        **🚨 IMMEDIATE ACTION REQUIRED:**
        - Start sepsis protocol immediately
        - Blood cultures before antibiotics
        - Broad-spectrum antibiotics within 1 hour
        - Lactate clearance protocol
        - ICU intensivist consultation
        """)
    elif patient['sepsis_risk'] == 'HIGH':
        st.warning("""
        **⚠️ CLOSE MONITORING:**
        - Repeat vitals every hour
        - Consider blood cultures
        - Monitor lactate trend
        - Prepare for potential escalation
        """)
    else:
        st.info("""
        **✅ STANDARD CARE:**
        - Continue current treatment
        - Regular monitoring
        - Reassess in 4 hours
        """)


def show_risk_trend_chart():
    """Show risk trend over time"""
    # Mock trend data
    hours = list(range(-24, 1))
    np.random.seed(42)

    critical = [max(0, 1 + np.random.randint(-1, 2)) for _ in hours]
    high = [max(0, 2 + np.random.randint(-1, 2)) for _ in hours]
    medium = [max(0, 1 + np.random.randint(0, 2)) for _ in hours]
    low = [max(0, 1 + np.random.randint(0, 1)) for _ in hours]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=critical, name='Critical', fill='tonexty', line=dict(color='#dc2626')))
    fig.add_trace(go.Scatter(x=hours, y=high, name='High', fill='tonexty', line=dict(color='#ef4444')))
    fig.add_trace(go.Scatter(x=hours, y=medium, name='Medium', fill='tonexty', line=dict(color='#f59e0b')))
    fig.add_trace(go.Scatter(x=hours, y=low, name='Low', fill='tozeroy', line=dict(color='#10b981')))

    fig.update_layout(
        xaxis_title="Hours from Now",
        yaxis_title="Number of Patients",
        height=300,
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)


def show_risk_scatter(df: pd.DataFrame):
    """Show sepsis vs mortality risk scatter plot"""
    fig = px.scatter(
        df,
        x='sepsis_score',
        y='mortality_score',
        color='sepsis_risk',
        size='age',
        hover_data=['patient_id', 'name', 'status'],
        color_discrete_map={
            'LOW': '#10b981',
            'MEDIUM': '#f59e0b',
            'HIGH': '#ef4444',
            'CRITICAL': '#dc2626'
        }
    )

    fig.update_layout(
        xaxis_title="Sepsis Risk Score",
        yaxis_title="Mortality Risk Score",
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
