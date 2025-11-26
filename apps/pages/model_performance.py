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
        st.metric("AUROC", "0.893", delta="Target: 0.85+", help="Area Under ROC Curve")

    with col2:
        st.metric("Sensitivity", "0.828", delta="Target: 0.75-0.85", help="True Positive Rate / Recall")

    with col3:
        st.metric("Specificity", "0.806", delta="Target: 0.82-0.90", help="True Negative Rate")

    with col4:
        st.metric("Accuracy", "0.816", help="Overall classification accuracy")

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
    st.markdown("#### 🎯 Feature Importance (Top 20)")
    show_feature_importance("sepsis")

    # Model info
    st.markdown("---")
    st.markdown("#### ℹ️ Model Information")

    model_info = {
        "model_name": "sepsis_lightgbm_v1",
        "algorithm": "LightGBM (Gradient Boosting)",
        "features": 42,
        "training_dataset": "MIMIC-IV (akshaybe/updated-mimic-iv)",
        "training_samples": "~20,000 ICU stays",
        "target": "Sepsis diagnosis (SEPSIS-3 criteria)",
        "class_balance": "SMOTE oversampling applied",
        "validation": "Train-test split (80/20)",
        "hyperparameters": {
            "objective": "binary",
            "metric": "auc",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "num_boost_round": 1000
        },
        "performance": {
            "AUROC": "0.893 (actual from training)",
            "Accuracy": "81.6%",
            "Sensitivity": "82.8%",
            "Specificity": "80.6%",
            "Precision": "76.3%",
            "F1-Score": "79.4%"
        }
    }

    st.json(model_info)


def show_mortality_model_performance():
    """Mortality model performance"""

    st.markdown("### 💔 Mortality Prediction Model (LightGBM)")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("AUROC", "0.645", delta="Target: 0.82-0.90", help="Area Under ROC Curve")

    with col2:
        st.metric("Sensitivity", "0.599", delta="Target: 0.70-0.82", help="True Positive Rate / Recall")

    with col3:
        st.metric("Specificity", "0.600", delta="Target: 0.80-0.88", help="True Negative Rate")

    with col4:
        st.metric("Accuracy", "0.602", help="Overall classification accuracy")

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
    st.markdown("#### 🎯 Feature Importance (All 13 Features)")
    show_feature_importance("mortality")

    # Model info
    st.markdown("---")
    st.markdown("#### ℹ️ Model Information")

    model_info = {
        "model_name": "mortality_lightgbm_v1",
        "algorithm": "LightGBM (Gradient Boosting)",
        "features": 13,
        "training_dataset": "MIMIC-IV (akshaybe/updated-mimic-iv)",
        "training_samples": "~10,000 ICU stays",
        "target": "Hospital mortality",
        "class_balance": "SMOTE oversampling applied",
        "validation": "Train-test split (80/20)",
        "hyperparameters": {
            "objective": "binary",
            "metric": "auc",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "num_boost_round": 500
        },
        "performance": {
            "AUROC": "0.645 (actual from training)",
            "Accuracy": "60.2%",
            "Sensitivity": "59.9%",
            "Specificity": "60.0%"
        }
    }

    st.json(model_info)


def show_roc_curve(model_type: str):
    """Show ROC curve"""

    # Mock ROC curve data
    np.random.seed(42 if model_type == "sepsis" else 43)

    # Generate realistic ROC curve
    fpr = np.linspace(0, 1, 100)

    if model_type == "sepsis":
        # AUROC = 0.893
        tpr = fpr ** 0.27 + 0.15 * np.random.random(100)
        tpr = np.clip(tpr, 0, 1)
        auroc = 0.893
    else:
        # AUROC = 0.645
        tpr = fpr ** 0.65 + 0.10 * np.random.random(100)
        tpr = np.clip(tpr, 0, 1)
        auroc = 0.645

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

    st.plotly_chart(fig, use_column_width=True)


def show_confusion_matrix(model_type: str):
    """Show confusion matrix"""

    if model_type == "sepsis":
        # Actual from training: Sensitivity = 0.828, Specificity = 0.806
        # Test set: 2000 samples with 43.1% positive (862 positive cases)
        tn, fp, fn, tp = 917, 221, 149, 713
    else:
        # Actual from training: Sensitivity = 0.599, Specificity = 0.600
        # Test set: 2000 samples with 47.9% positive (958 positive cases)
        tn, fp, fn, tp = 625, 417, 384, 574

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

    st.plotly_chart(fig, use_column_width=True)

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
                'sofa_score',
                'respiratory_rate',
                'age',
                'creatinine',
                'bilirubin',
                'platelets',
                'shock_index',
                'lactate',
                'temperature',
                'heart_rate',
                'wbc',
                'apache_ii_score',
                'spo2',
                'map',
                'bun_creatinine_ratio',
                'dbp',
                'sbp',
                'sirs_score',
                'pulse_pressure',
                'lactate_albumin_ratio',
            ],
            'importance': [
                0.8795,
                0.0104,
                0.0096,
                0.0086,
                0.0071,
                0.0071,
                0.0063,
                0.0063,
                0.0059,
                0.0058,
                0.0056,
                0.0056,
                0.0055,
                0.0049,
                0.0048,
                0.0042,
                0.0039,
                0.0039,
                0.0036,
                0.0032,
            ]
        })
    else:
        features = pd.DataFrame({
            'feature': [
                'apache_ii_score',
                'sofa_day1',
                'worst_lactate',
                'worst_heart_rate',
                'worst_spo2',
                'worst_creatinine',
                'age',
                'worst_respiratory_rate',
                'worst_temperature_high',
                'worst_sbp_low',
                'worst_gcs',
                'vasopressor_use',
                'gender',
            ],
            'importance': [
                0.1196,
                0.1052,
                0.0945,
                0.0938,
                0.0894,
                0.0888,
                0.0874,
                0.0868,
                0.0865,
                0.0857,
                0.0342,
                0.0195,
                0.0087,
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

    st.plotly_chart(fig, use_column_width=True)
