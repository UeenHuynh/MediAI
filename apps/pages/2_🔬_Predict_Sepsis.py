"""
Predict Sepsis page - Predict sepsis risk for ICU patients.
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Predict Sepsis", page_icon="🔬")

st.title("🔬 Predict Sepsis Risk")
st.markdown("Predict sepsis onset within 6 hours using patient vitals and lab values.")

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
    """Show manual entry form for sepsis prediction."""
    st.subheader("Enter Patient Information")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Demographics**")
        age = st.number_input("Age (years)", min_value=18, max_value=120, value=65)
        gender = st.selectbox("Gender", ["Male", "Female"])
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=70.0)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)

        st.markdown("**Vital Signs**")
        heart_rate = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=80)
        sbp = st.number_input("Systolic BP (mmHg)", min_value=50, max_value=250, value=120)
        dbp = st.number_input("Diastolic BP (mmHg)", min_value=30, max_value=150, value=80)
        temperature = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0)
        respiratory_rate = st.number_input("Respiratory Rate (breaths/min)", min_value=5, max_value=60, value=16)
        spo2 = st.number_input("SpO2 (%)", min_value=50, max_value=100, value=98)

    with col2:
        st.markdown("**Laboratory Values**")
        wbc = st.number_input("WBC (10^9/L)", min_value=0.0, max_value=50.0, value=8.0, format="%.2f")
        lactate = st.number_input("Lactate (mmol/L)", min_value=0.0, max_value=20.0, value=1.5, format="%.2f")
        creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.0, max_value=15.0, value=1.0, format="%.2f")
        bilirubin = st.number_input("Bilirubin (mg/dL)", min_value=0.0, max_value=30.0, value=1.0, format="%.2f")
        platelets = st.number_input("Platelets (10^9/L)", min_value=0, max_value=1000, value=200)

        st.markdown("**SOFA Score Components**")
        sofa_resp = st.number_input("SOFA Respiratory", min_value=0, max_value=4, value=0)
        sofa_coag = st.number_input("SOFA Coagulation", min_value=0, max_value=4, value=0)
        sofa_liver = st.number_input("SOFA Liver", min_value=0, max_value=4, value=0)
        sofa_cardio = st.number_input("SOFA Cardiovascular", min_value=0, max_value=4, value=0)
        sofa_cns = st.number_input("SOFA CNS", min_value=0, max_value=4, value=0)
        sofa_renal = st.number_input("SOFA Renal", min_value=0, max_value=4, value=0)

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔬 Predict Sepsis Risk", use_container_width=True, type="primary"):
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
                # In production, this would fetch data from the database
                show_prediction_result()
            else:
                st.error("❌ Please enter a valid Stay ID")


def show_csv_upload():
    """Show CSV upload interface."""
    st.subheader("Upload Patient Data (CSV)")

    st.info("📄 Upload a CSV file with patient features. The file should contain 42 features as defined in the sepsis model schema.")

    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(df.head(), use_container_width=True)

        if st.button("🔬 Predict for All Patients", use_container_width=True, type="primary"):
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
            label="Sepsis Risk Score",
            value="73.2%",
            delta="High Risk",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            label="Confidence",
            value="89.5%",
            delta="Very Confident"
        )

    with col3:
        st.metric(
            label="Time to Onset (Est.)",
            value="4.2 hrs",
            delta="Urgent"
        )

    # Risk interpretation
    st.markdown("### 🚨 Risk Interpretation")
    st.error("**HIGH RISK** - Patient shows significant risk of sepsis within 6 hours. Immediate clinical review recommended.")

    # Feature importance
    st.markdown("### 📊 Top Contributing Factors")

    feature_importance = pd.DataFrame({
        'Feature': ['Lactate', 'WBC Count', 'SOFA Score', 'Temperature', 'Heart Rate'],
        'Importance': [0.28, 0.22, 0.18, 0.15, 0.12],
        'Value': ['3.2 mmol/L', '14.5 10^9/L', '8', '38.5°C', '115 bpm'],
        'Status': ['🔴 Elevated', '🔴 High', '🔴 High', '🟡 Elevated', '🟡 Elevated']
    })

    st.dataframe(feature_importance, use_container_width=True, hide_index=True)

    # Recommendations
    st.markdown("### 💡 Clinical Recommendations")
    st.markdown("""
    - ⚠️ **Immediate**: Start sepsis protocol
    - 🔬 **Lab Work**: Repeat lactate and blood cultures
    - 💉 **Treatment**: Consider early antibiotic administration
    - 📊 **Monitoring**: Increase vital signs monitoring frequency
    - 🏥 **Escalation**: Notify attending physician
    """)

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
        'Stay ID': [f'S{1000+i}' for i in range(5)],
        'Risk Score': ['73.2%', '45.8%', '88.1%', '32.5%', '61.7%'],
        'Risk Level': ['🔴 High', '🟡 Medium', '🔴 High', '🟢 Low', '🟡 Medium'],
        'Confidence': ['89.5%', '82.1%', '91.3%', '78.9%', '85.2%']
    })

    st.dataframe(results, use_container_width=True, hide_index=True)

    st.download_button(
        "📥 Download Full Results (CSV)",
        data=results.to_csv(index=False),
        file_name="sepsis_predictions.csv",
        mime="text/csv",
        use_container_width=True
    )
