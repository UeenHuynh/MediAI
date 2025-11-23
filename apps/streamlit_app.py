"""
MediAI Healthcare ML Platform - Streamlit UI
Main entry point for the Streamlit application.
"""
import streamlit as st

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="MediAI Healthcare ML Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main header
st.title("🏥 MediAI Healthcare ML Platform")
st.markdown("### ICU Patient Risk Prediction System")

st.markdown("---")

# Welcome section
st.markdown("""
## Welcome to MediAI

An end-to-end MLOps platform for ICU patient risk prediction using MIMIC-IV data.

### 🎯 Key Features

- **🔬 Sepsis Risk Prediction** - 6-hour early warning system using 42 clinical features
- **💔 Mortality Risk Prediction** - Hospital mortality assessment using 65 clinical features
- **📊 Model Performance Monitoring** - Real-time model metrics and analytics
- **⚙️ Configurable Settings** - Customize alert thresholds and system preferences

### 🚀 Quick Start

Use the navigation menu in the sidebar to:

1. **📊 View Dashboard** - See recent predictions and system status
2. **🔬 Predict Sepsis** - Run sepsis risk predictions for ICU patients
3. **💔 Predict Mortality** - Assess mortality risk using 24-hour ICU data
4. **📈 Monitor Performance** - Track model performance metrics
5. **⚙️ Configure Settings** - Adjust system preferences and thresholds

### 🛠️ Technology Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **ML Tracking:** MLflow
- **Models:** LightGBM

### 📊 Model Performance

**Sepsis Prediction Model (v1.2.0)**
- AUROC: 0.872
- Sensitivity: 0.835
- Specificity: 0.812

**Mortality Prediction Model (v1.1.0)**
- AUROC: 0.828
- Sensitivity: 0.782
- Specificity: 0.795

---

### 📖 Documentation

For more information, please refer to:
- [Architecture Design](../ARCHITECTURE_DESIGN.md)
- [Database Schema](../DATABASE_SCHEMA.md)
- [API Documentation](http://localhost:8000/docs)

""")

# System status
st.markdown("---")
st.markdown("### 💻 System Status")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.success("✅ API Server Online")

with col2:
    st.success("✅ Database Connected")

with col3:
    st.success("✅ ML Models Loaded")

with col4:
    st.info("ℹ️ Version 1.0.0")
