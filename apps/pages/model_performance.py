"""
Model Performance Page
Display model metrics, confusion matrix, and feature importance
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def show_model_performance():
    """Model performance metrics page"""

    st.markdown('<div class="page-header">📊 Model Performance Metrics</div>', unsafe_allow_html=True)

    # Model selection
    model_tab1, model_tab2 = st.tabs(["🔬 Sepsis Model", "💔 Mortality Model"])

    with model_tab1:
        show_sepsis_model_performance()

    with model_tab2:
        show_mortality_model_performance()


def show_sepsis_model_performance():
    """Sepsis model performance"""

    st.markdown("### 🔬 Sepsis Prediction Model (LightGBM)")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("AUROC", "0.87", delta="0.02 vs baseline", help="Area Under ROC Curve")

    with col2:
        st.metric("Sensitivity", "0.82", delta="Target: 0.80", help="True Positive Rate / Recall")

    with col3:
        st.metric("Specificity", "0.85", delta="Target: 0.80", help="True Negative Rate")

    with col4:
        st.metric("F1 Score", "0.78", help="Harmonic mean of precision and recall")

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📈 ROC Curve")
        show_roc_curve("sepsis")

    with col2:
        st.markdown("#### 📊 Confusion Matrix")
        show_confusion_matrix("sepsis")

    # Feature importance
    st.markdown("---")
    st.markdown("#### 🎯 Top 20 Feature Importance")
    show_feature_importance("sepsis")

    # Model info
    st.markdown("---")
    st.markdown("#### ℹ️ Model Information")

    model_info = {
        "model_name": "sepsis_lightgbm_v1",
        "algorithm": "LightGBM (Gradient Boosting)",
        "features": 42,
        "training_samples": "20,000 ICU stays",
        "target": "Sepsis onset within 6 hours (SEPSIS-3 criteria)",
        "class_balance": "6% positive (SMOTE oversampling applied)",
        "validation": "5-fold cross-validation",
        "hyperparameters": {
            "num_leaves": 31,
            "learning_rate": 0.05,
            "n_estimators": 200,
            "max_depth": 7
        },
        "last_trained": "2025-01-20",
        "mlflow_run_id": "abc123def456"
    }

    st.json(model_info)


def show_mortality_model_performance():
    """Mortality model performance"""

    st.markdown("### 💔 Mortality Prediction Model (LightGBM)")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("AUROC", "0.82", delta="0.03 vs APACHE-II", help="Area Under ROC Curve")

    with col2:
        st.metric("Sensitivity", "0.75", delta="Target: 0.75", help="True Positive Rate / Recall")

    with col3:
        st.metric("Specificity", "0.80", delta="Target: 0.75", help="True Negative Rate")

    with col4:
        st.metric("F1 Score", "0.72", help="Harmonic mean of precision and recall")

    st.markdown("---")

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📈 ROC Curve")
        show_roc_curve("mortality")

    with col2:
        st.markdown("#### 📊 Confusion Matrix")
        show_confusion_matrix("mortality")

    # Feature importance
    st.markdown("---")
    st.markdown("#### 🎯 Top 20 Feature Importance")
    show_feature_importance("mortality")

    # Model info
    st.markdown("---")
    st.markdown("#### ℹ️ Model Information")

    model_info = {
        "model_name": "mortality_lightgbm_v1",
        "algorithm": "LightGBM (Gradient Boosting)",
        "features": 65,
        "training_samples": "70,000 ICU stays",
        "target": "Hospital mortality",
        "class_balance": "10% positive (class weights applied)",
        "validation": "Temporal validation (train on 2019-2020, test on 2021)",
        "hyperparameters": {
            "num_leaves": 31,
            "learning_rate": 0.03,
            "n_estimators": 300,
            "max_depth": 8
        },
        "last_trained": "2025-01-20",
        "mlflow_run_id": "def456ghi789"
    }

    st.json(model_info)


def show_roc_curve(model_type: str):
    """Show ROC curve"""

    # Mock ROC curve data
    np.random.seed(42 if model_type == "sepsis" else 43)

    # Generate realistic ROC curve
    fpr = np.linspace(0, 1, 100)

    if model_type == "sepsis":
        # AUROC = 0.87
        tpr = fpr ** 0.3 + 0.15 * np.random.random(100)
        tpr = np.clip(tpr, 0, 1)
        auroc = 0.87
    else:
        # AUROC = 0.82
        tpr = fpr ** 0.4 + 0.12 * np.random.random(100)
        tpr = np.clip(tpr, 0, 1)
        auroc = 0.82

    fig = go.Figure()

    # ROC curve
    fig.add_trace(go.Scatter(
        x=fpr,
        y=tpr,
        name=f'Model (AUROC = {auroc:.2f})',
        line=dict(color='#667eea', width=3)
    ))

    # Diagonal reference line
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        name='Random (AUROC = 0.50)',
        line=dict(color='gray', width=2, dash='dash')
    ))

    fig.update_layout(
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Sensitivity)",
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=True,
        legend=dict(x=0.6, y=0.1)
    )

    st.plotly_chart(fig, use_container_width=True)


def show_confusion_matrix(model_type: str):
    """Show confusion matrix"""

    if model_type == "sepsis":
        # Sensitivity = 0.82, Specificity = 0.85
        # Assuming 1000 validation samples with 6% positive
        tn, fp, fn, tp = 799, 141, 11, 49
    else:
        # Sensitivity = 0.75, Specificity = 0.80
        # Assuming 1000 validation samples with 10% positive
        tn, fp, fn, tp = 720, 180, 25, 75

    matrix = np.array([[tn, fp], [fn, tp]])

    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=['Predicted Negative', 'Predicted Positive'],
        y=['Actual Negative', 'Actual Positive'],
        text=matrix,
        texttemplate='%{text}',
        textfont={"size": 20},
        colorscale='Blues',
        showscale=False
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Metrics from confusion matrix
    col1, col2, col3, col4 = st.columns(4)

    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    npv = tn / (tn + fn)
    accuracy = (tp + tn) / (tp + tn + fp + fn)

    with col1:
        st.metric("Precision (PPV)", f"{precision:.2f}", help="Positive Predictive Value")

    with col2:
        st.metric("Recall (Sensitivity)", f"{recall:.2f}", help="True Positive Rate")

    with col3:
        st.metric("NPV", f"{npv:.2f}", help="Negative Predictive Value")

    with col4:
        st.metric("Accuracy", f"{accuracy:.2f}", help="Overall Accuracy")


def show_feature_importance(model_type: str):
    """Show feature importance chart"""

    if model_type == "sepsis":
        features = pd.DataFrame({
            'feature': [
                'lactate', 'heart_rate', 'temperature', 'wbc', 'sbp',
                'respiratory_sofa', 'creatinine', 'lactate_trend_12h',
                'platelets', 'bilirubin', 'age', 'cardiovascular_sofa',
                'dbp', 'respiratory_rate', 'hr_trend_6h', 'potassium',
                'sodium', 'coagulation_sofa', 'glucose', 'renal_sofa'
            ],
            'importance': [
                0.145, 0.128, 0.112, 0.095, 0.082,
                0.071, 0.065, 0.058, 0.052, 0.048,
                0.042, 0.038, 0.034, 0.031, 0.028,
                0.025, 0.022, 0.019, 0.017, 0.015
            ]
        })
    else:
        features = pd.DataFrame({
            'feature': [
                'apache_ii_score', 'age', 'gcs', 'lactate', 'mechanical_ventilation',
                'worst_sbp_24h', 'worst_hr_24h', 'worst_temp_24h',
                'cardiovascular_sofa', 'respiratory_sofa', 'admission_type',
                'worst_creatinine_24h', 'worst_wbc_24h', 'num_organ_failures',
                'vasopressors', 'chronic_health', 'worst_platelets_24h',
                'fluid_balance_24h', 'renal_sofa', 'hepatic_sofa'
            ],
            'importance': [
                0.165, 0.142, 0.118, 0.095, 0.088,
                0.075, 0.068, 0.062, 0.055, 0.048,
                0.042, 0.038, 0.035, 0.032, 0.028,
                0.025, 0.022, 0.019, 0.017, 0.015
            ]
        })

    fig = px.bar(
        features,
        x='importance',
        y='feature',
        orientation='h',
        color='importance',
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        xaxis_title="Importance",
        yaxis_title="Feature",
        height=500,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
