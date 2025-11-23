"""
Predict Mortality page - Predict ICU mortality risk for patients.
"""
import streamlit as st
import pandas as pd


def show():
    """Display the predict mortality page."""
    st.title("💔 Predict Mortality Risk")
    st.markdown("Predict hospital mortality risk using 24-hour ICU data and severity scores.")

    st.markdown("---")

    # Input method selection
    input_method = st.radio(
        "Select Input Method:",
        ["Manual Entry", "Load from Database", "Upload CSV"],
        horizontal=True
    )

    if input_method == "Manual Entry":
        show_manual_entry()
    elif input_method == "Load from Database":
        show_database_load()
    else:
        show_csv_upload()


def show_manual_entry():
    """Show manual entry form for mortality prediction."""
    st.subheader("Enter Patient Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Demographics & ICU Details**")
        age = st.number_input("Age (years)", min_value=18, max_value=120, value=65)
        gender = st.selectbox("Gender", ["Male", "Female"])
        admission_type = st.selectbox("Admission Type", ["Emergency", "Elective", "Urgent"])
        icu_type = st.selectbox("ICU Type", ["Medical", "Surgical", "Cardiac", "Neuro"])
        los_icu = st.number_input("ICU Length of Stay (hours)", min_value=0, max_value=720, value=48)

        st.markdown("**Worst Vital Signs (24h)**")
        heart_rate_max = st.number_input("Max Heart Rate (bpm)", min_value=30, max_value=250, value=120)
        sbp_min = st.number_input("Min Systolic BP (mmHg)", min_value=40, max_value=200, value=90)
        temperature_max = st.number_input("Max Temperature (°C)", min_value=35.0, max_value=42.0, value=38.5)
        respiratory_rate_max = st.number_input("Max Respiratory Rate", min_value=5, max_value=80, value=28)
        spo2_min = st.number_input("Min SpO2 (%)", min_value=50, max_value=100, value=92)

    with col2:
        st.markdown("**Worst Laboratory Values (24h)**")
        wbc_max = st.number_input("Max WBC (10^9/L)", min_value=0.0, max_value=100.0, value=15.0)
        lactate_max = st.number_input("Max Lactate (mmol/L)", min_value=0.0, max_value=30.0, value=3.5)
        creatinine_max = st.number_input("Max Creatinine (mg/dL)", min_value=0.0, max_value=20.0, value=2.5)
        bilirubin_max = st.number_input("Max Bilirubin (mg/dL)", min_value=0.0, max_value=50.0, value=2.0)
        platelets_min = st.number_input("Min Platelets (10^9/L)", min_value=0, max_value=500, value=120)
        gcs_min = st.number_input("Min Glasgow Coma Scale", min_value=3, max_value=15, value=12)

        st.markdown("**Severity Scores**")
        sofa_total = st.number_input("SOFA Total Score", min_value=0, max_value=24, value=8)
        apache_ii = st.number_input("APACHE II Score", min_value=0, max_value=71, value=18)

        st.markdown("**Interventions**")
        mechanical_vent = st.checkbox("Mechanical Ventilation", value=False)
        vasopressors = st.checkbox("Vasopressors", value=False)
        dialysis = st.checkbox("Dialysis", value=False)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💔 Predict Mortality Risk", use_container_width=True, type="primary"):
            show_prediction_result()


def show_database_load():
    """Show database patient selection."""
    st.subheader("Load Patient from Database")

    stay_id = st.text_input("Enter ICU Stay ID", placeholder="e.g., 30001234")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔍 Load Patient Data", use_container_width=True):
            if stay_id:
                st.success(f"✅ Loaded patient data for Stay ID: {stay_id}")
                show_prediction_result()
            else:
                st.error("❌ Please enter a valid Stay ID")


def show_csv_upload():
    """Show CSV upload interface."""
    st.subheader("Upload Patient Data (CSV)")

    st.info("📄 Upload a CSV file with patient features. The file should contain 65 features as defined in the mortality model schema.")

    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head(), use_container_width=True)

        if st.button("💔 Predict for All Patients", use_container_width=True, type="primary"):
            st.success(f"✅ Processing {len(df)} patients...")
            show_batch_prediction_results()


def show_prediction_result():
    """Show prediction results (mock data for now)."""
    st.markdown("---")
    st.subheader("🎯 Prediction Results")

    # Mock prediction result
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Mortality Risk Score",
            value="42.8%",
            delta="Medium Risk",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            label="Confidence",
            value="91.2%",
            delta="Very Confident"
        )

    with col3:
        st.metric(
            label="Risk Category",
            value="Moderate",
            delta="Monitor Closely"
        )

    # Risk interpretation
    st.markdown("### ⚠️ Risk Interpretation")
    st.warning("**MEDIUM RISK** - Patient shows moderate risk of hospital mortality. Close monitoring and appropriate interventions recommended.")

    # Risk stratification
    st.markdown("### 📊 Risk Stratification")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Risk Breakdown by Category:**")
        risk_data = pd.DataFrame({
            'Category': ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
            'Probability': ['10%', '20%', '40%', '20%', '10%']
        })
        st.dataframe(risk_data, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Similar Patient Outcomes (Historical):**")
        outcome_data = pd.DataFrame({
            'Outcome': ['Survived', 'Deceased', 'Transferred'],
            'Count': [58, 35, 7],
            'Percentage': ['58%', '35%', '7%']
        })
        st.dataframe(outcome_data, use_container_width=True, hide_index=True)

    # Feature importance
    st.markdown("### 📊 Top Contributing Factors")

    feature_importance = pd.DataFrame({
        'Feature': ['APACHE II Score', 'SOFA Total', 'Age', 'Lactate Max', 'GCS Min'],
        'Importance': [0.32, 0.25, 0.18, 0.15, 0.10],
        'Value': ['18', '8', '72 years', '3.5 mmol/L', '12'],
        'Status': ['🔴 High', '🟡 Elevated', '🟡 Elderly', '🔴 Elevated', '🟡 Decreased']
    })

    st.dataframe(feature_importance, use_container_width=True, hide_index=True)

    # Recommendations
    st.markdown("### 💡 Clinical Recommendations")
    st.markdown("""
    - 📊 **Monitoring**: Continue intensive monitoring
    - 🔬 **Assessment**: Daily organ function assessment
    - 💊 **Treatment**: Optimize supportive care
    - 🏥 **Planning**: Discuss goals of care with family
    - 📋 **Documentation**: Update advance directives if needed
    - 👨‍⚕️ **Consultation**: Consider specialist consultation for organ support
    """)

    # Trends over time
    st.markdown("### 📈 Risk Trends (If Available)")
    st.info("📅 Multiple predictions over time can show risk trajectory. This helps assess if interventions are effective.")

    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button("💾 Save Prediction", use_container_width=True)
    with col2:
        st.button("📧 Alert Care Team", use_container_width=True)
    with col3:
        st.button("📄 Generate Report", use_container_width=True)


def show_batch_prediction_results():
    """Show batch prediction results (mock data for now)."""
    st.markdown("### 📊 Batch Prediction Results")

    results = pd.DataFrame({
        'Stay ID': [f'M{2000+i}' for i in range(5)],
        'Risk Score': ['42.8%', '68.3%', '15.2%', '81.5%', '33.9%'],
        'Risk Level': ['🟡 Medium', '🔴 High', '🟢 Low', '🔴 Very High', '🟡 Medium'],
        'Confidence': ['91.2%', '87.6%', '93.1%', '89.8%', '90.5%']
    })

    st.dataframe(results, use_container_width=True, hide_index=True)

    st.download_button(
        "📥 Download Full Results (CSV)",
        data=results.to_csv(index=False),
        file_name="mortality_predictions.csv",
        mime="text/csv",
        use_container_width=True
    )
