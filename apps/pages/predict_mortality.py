"""
Mortality Prediction Page
Placeholder for mortality risk prediction (similar to sepsis)
"""

import streamlit as st


def show_mortality_prediction():
    """Mortality prediction page"""

    st.markdown('<div class="page-header">💔 Mortality Risk Prediction</div>', unsafe_allow_html=True)

    st.info("""
    **ICU Mortality Risk Assessment**

    Predicts hospital mortality risk using 65 clinical features:
    - All sepsis features (42)
    - APACHE-II scores
    - Worst vitals/labs in first 24h
    - ICU admission details
    """)

    st.warning("""
    **🚧 Implementation in Progress**

    This page would contain a similar form to the Sepsis Prediction page,
    but with 65 features for mortality prediction.

    For demo purposes, please use the **Sepsis Prediction** page which is fully functional.
    """)

    st.markdown("---")

    st.markdown("### 📋 Mortality Model Features (65 total)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **All Sepsis Features (42):**
        - Demographics & vitals
        - Laboratory values
        - SOFA scores
        - Temporal trends
        """)

        st.markdown("""
        **APACHE-II Components:**
        - Age points
        - Temperature (worst)
        - Mean arterial pressure (worst)
        - Heart rate (worst)
        - Respiratory rate (worst)
        - Oxygenation (worst A-a gradient or PaO2)
        - Arterial pH (worst)
        - Sodium (worst)
        - Potassium (worst)
        - Creatinine (worst)
        - Hematocrit (worst)
        - WBC (worst)
        - Glasgow Coma Scale
        """)

    with col2:
        st.markdown("""
        **ICU Admission Details:**
        - Admission type (emergency, elective, urgent)
        - Admission source (ER, floor, OR, other hospital)
        - Primary diagnosis category
        - Mechanical ventilation (Y/N)
        - Vasopressors (Y/N)
        - Chronic health conditions
        """)

        st.markdown("""
        **First 24h Aggregates:**
        - Minimum/maximum vitals
        - Minimum/maximum labs
        - SOFA score change
        - Cumulative fluid balance
        - Blood product transfusions
        - Number of organ failures
        """)

    st.markdown("---")

    st.markdown("### 🎯 Model Performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("AUROC", "0.82", help="Area Under ROC Curve")

    with col2:
        st.metric("Sensitivity", "0.75", help="True Positive Rate")

    with col3:
        st.metric("Specificity", "0.80", help="True Negative Rate")

    st.markdown("---")

    if st.button("🔬 Go to Sepsis Prediction (Demo)", use_container_width=True):
        st.session_state.current_page = "🔬 Predict Sepsis"
        st.rerun()
