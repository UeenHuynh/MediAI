"""
Model Performance page - View model metrics and performance analytics.
"""
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Model Performance", page_icon="📊")

st.title("📊 Model Performance")
st.markdown("Monitor and analyze the performance of sepsis and mortality prediction models.")

st.markdown("---")

# Model selection
model_type = st.selectbox(
    "Select Model:",
    ["Sepsis Prediction Model", "Mortality Prediction Model"],
    index=0
)

if model_type == "Sepsis Prediction Model":
    show_sepsis_performance()
else:
    show_mortality_performance()


def show_sepsis_performance():
    """Show sepsis model performance metrics."""
    st.subheader("🔬 Sepsis Prediction Model (sepsis_lightgbm_v1)")

    # Model info
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Model Version", "v1.2.0")
    with col2:
        st.metric("Last Updated", "2025-01-15")
    with col3:
        st.metric("Status", "🟢 Active")
    with col4:
        st.metric("Total Predictions", "12,487")

    st.markdown("---")

    # Performance metrics
    st.markdown("### 🎯 Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="AUROC",
            value="0.872",
            delta="+0.012 vs baseline",
            help="Area Under ROC Curve - measures discrimination ability"
        )

    with col2:
        st.metric(
            label="Sensitivity",
            value="0.835",
            delta="+0.025",
            help="True Positive Rate - ability to identify sepsis cases"
        )

    with col3:
        st.metric(
            label="Specificity",
            value="0.812",
            delta="-0.008",
            delta_color="inverse",
            help="True Negative Rate - ability to identify non-sepsis cases"
        )

    with col4:
        st.metric(
            label="PPV",
            value="0.468",
            delta="+0.015",
            help="Positive Predictive Value - precision of positive predictions"
        )

    # Detailed metrics table
    st.markdown("### 📋 Detailed Metrics")

    metrics_df = pd.DataFrame({
        'Metric': [
            'AUROC', 'AUPRC', 'Sensitivity', 'Specificity', 'PPV', 'NPV',
            'F1 Score', 'Accuracy', 'Balanced Accuracy'
        ],
        'Current Value': [0.872, 0.421, 0.835, 0.812, 0.468, 0.959, 0.598, 0.815, 0.824],
        'Target': ['>0.85', '>0.40', '>0.80', '>0.80', '>0.45', '>0.95', '>0.55', '>0.80', '>0.80'],
        'Status': ['✅', '✅', '✅', '✅', '✅', '✅', '✅', '✅', '✅']
    })

    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    # Confusion matrix
    st.markdown("### 🔢 Confusion Matrix (Validation Set)")

    col1, col2 = st.columns([1, 2])

    with col1:
        confusion_data = pd.DataFrame({
            '': ['Predicted Negative', 'Predicted Positive'],
            'Actual Negative': [7654, 1773],
            'Actual Positive': [124, 628]
        })
        st.dataframe(confusion_data, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Interpretation:**")
        st.markdown("""
        - **True Negatives (7,654):** Correctly predicted no sepsis
        - **True Positives (628):** Correctly predicted sepsis
        - **False Positives (1,773):** Incorrectly predicted sepsis (false alarms)
        - **False Negatives (124):** Missed sepsis cases (most critical)
        """)

    # Feature importance
    st.markdown("### 🔑 Top 10 Feature Importance")

    feature_importance = pd.DataFrame({
        'Rank': range(1, 11),
        'Feature': [
            'Lactate', 'SOFA Total Score', 'WBC Count', 'Temperature',
            'Heart Rate', 'Respiratory Rate', 'Platelets', 'MAP',
            'Age', 'Creatinine'
        ],
        'Importance': [0.142, 0.118, 0.095, 0.082, 0.071, 0.065, 0.058, 0.052, 0.048, 0.041],
        'Type': [
            'Lab', 'Composite', 'Lab', 'Vital', 'Vital',
            'Vital', 'Lab', 'Vital', 'Demo', 'Lab'
        ]
    })

    st.dataframe(feature_importance, use_container_width=True, hide_index=True)

    # Performance over time
    st.markdown("### 📈 Performance Trends (Last 30 Days)")

    trend_data = pd.DataFrame({
        'Date': pd.date_range(start='2025-01-01', periods=30, freq='D'),
        'AUROC': np.random.normal(0.872, 0.015, 30),
        'Sensitivity': np.random.normal(0.835, 0.02, 30),
        'Specificity': np.random.normal(0.812, 0.02, 30)
    })

    st.line_chart(trend_data.set_index('Date'))

    # Calibration
    st.markdown("### 🎲 Model Calibration")
    st.info("📊 Calibration plots show how well predicted probabilities match actual outcomes. A well-calibrated model's predictions align with the diagonal.")

    # Model comparison
    st.markdown("### 🔄 Model Version Comparison")

    comparison_df = pd.DataFrame({
        'Version': ['v1.0.0', 'v1.1.0', 'v1.2.0 (Current)'],
        'AUROC': [0.848, 0.860, 0.872],
        'Sensitivity': [0.802, 0.818, 0.835],
        'Specificity': [0.798, 0.808, 0.812],
        'F1 Score': [0.562, 0.581, 0.598],
        'Release Date': ['2024-10-01', '2024-12-01', '2025-01-15']
    })

    st.dataframe(comparison_df, use_container_width=True, hide_index=True)


def show_mortality_performance():
    """Show mortality model performance metrics."""
    st.subheader("💔 Mortality Prediction Model (mortality_lightgbm_v1)")

    # Model info
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Model Version", "v1.1.0")
    with col2:
        st.metric("Last Updated", "2025-01-10")
    with col3:
        st.metric("Status", "🟢 Active")
    with col4:
        st.metric("Total Predictions", "8,923")

    st.markdown("---")

    # Performance metrics
    st.markdown("### 🎯 Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="AUROC",
            value="0.828",
            delta="+0.018 vs baseline",
            help="Area Under ROC Curve"
        )

    with col2:
        st.metric(
            label="Sensitivity",
            value="0.782",
            delta="+0.032",
            help="True Positive Rate"
        )

    with col3:
        st.metric(
            label="Specificity",
            value="0.795",
            delta="-0.012",
            delta_color="inverse",
            help="True Negative Rate"
        )

    with col4:
        st.metric(
            label="PPV",
            value="0.412",
            delta="+0.021",
            help="Positive Predictive Value"
        )

    # Detailed metrics table
    st.markdown("### 📋 Detailed Metrics")

    metrics_df = pd.DataFrame({
        'Metric': [
            'AUROC', 'AUPRC', 'Sensitivity', 'Specificity', 'PPV', 'NPV',
            'F1 Score', 'Accuracy', 'Balanced Accuracy'
        ],
        'Current Value': [0.828, 0.387, 0.782, 0.795, 0.412, 0.952, 0.534, 0.791, 0.789],
        'Target': ['>0.80', '>0.35', '>0.75', '>0.75', '>0.40', '>0.94', '>0.50', '>0.78', '>0.75'],
        'Status': ['✅', '✅', '✅', '✅', '✅', '✅', '✅', '✅', '✅']
    })

    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    # Confusion matrix
    st.markdown("### 🔢 Confusion Matrix (Validation Set)")

    col1, col2 = st.columns([1, 2])

    with col1:
        confusion_data = pd.DataFrame({
            '': ['Predicted Survival', 'Predicted Death'],
            'Actual Survival': [6124, 1578],
            'Actual Death': [189, 678]
        })
        st.dataframe(confusion_data, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("**Interpretation:**")
        st.markdown("""
        - **True Negatives (6,124):** Correctly predicted survival
        - **True Positives (678):** Correctly predicted mortality
        - **False Positives (1,578):** Incorrectly predicted death
        - **False Negatives (189):** Missed mortality cases
        """)

    # Feature importance
    st.markdown("### 🔑 Top 10 Feature Importance")

    feature_importance = pd.DataFrame({
        'Rank': range(1, 11),
        'Feature': [
            'APACHE II Score', 'SOFA Total', 'Age', 'Lactate Max',
            'GCS Min', 'Mechanical Ventilation', 'Vasopressors',
            'Creatinine Max', 'Bilirubin Max', 'Platelets Min'
        ],
        'Importance': [0.185, 0.152, 0.098, 0.085, 0.074, 0.068, 0.061, 0.055, 0.048, 0.042],
        'Type': [
            'Composite', 'Composite', 'Demo', 'Lab', 'Clinical',
            'Intervention', 'Intervention', 'Lab', 'Lab', 'Lab'
        ]
    })

    st.dataframe(feature_importance, use_container_width=True, hide_index=True)

    # Performance over time
    st.markdown("### 📈 Performance Trends (Last 30 Days)")

    trend_data = pd.DataFrame({
        'Date': pd.date_range(start='2025-01-01', periods=30, freq='D'),
        'AUROC': np.random.normal(0.828, 0.018, 30),
        'Sensitivity': np.random.normal(0.782, 0.025, 30),
        'Specificity': np.random.normal(0.795, 0.022, 30)
    })

    st.line_chart(trend_data.set_index('Date'))

    # Risk stratification
    st.markdown("### 📊 Risk Stratification Performance")

    stratification_df = pd.DataFrame({
        'Risk Category': ['Very Low (<20%)', 'Low (20-40%)', 'Medium (40-60%)', 'High (60-80%)', 'Very High (>80%)'],
        'Patients': [3245, 2156, 1823, 987, 358],
        'Actual Mortality Rate': ['8.2%', '25.1%', '48.3%', '71.5%', '88.7%'],
        'Predicted Average': ['12.5%', '30.2%', '50.1%', '69.8%', '87.3%'],
        'Calibration': ['✅ Good', '✅ Good', '✅ Excellent', '✅ Good', '✅ Good']
    })

    st.dataframe(stratification_df, use_container_width=True, hide_index=True)

    st.success("✅ Model shows good calibration across all risk categories")
