"""
Dashboard page - Overview of the MediAI platform.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon="🏠")

st.title("🏠 Dashboard")

# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Predictions Today",
        value="127",
        delta="12 from yesterday"
    )

with col2:
    st.metric(
        label="Sepsis Alerts",
        value="8",
        delta="-2",
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="Mortality Predictions",
        value="45",
        delta="5"
    )

with col4:
    st.metric(
        label="System Uptime",
        value="99.8%",
        delta="0.1%"
    )

st.markdown("---")

# Recent activity section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Recent Predictions")

    # Sample data for recent predictions
    recent_data = pd.DataFrame({
        'Time': [
            (datetime.now() - timedelta(minutes=i*5)).strftime('%H:%M')
            for i in range(10)
        ],
        'Stay ID': [f'S{1000+i}' for i in range(10)],
        'Prediction Type': ['Sepsis' if i % 2 == 0 else 'Mortality' for i in range(10)],
        'Risk Score': [f'{85-i*3}%' for i in range(10)],
        'Status': ['🔴 High' if i < 3 else '🟡 Medium' if i < 7 else '🟢 Low' for i in range(10)]
    })

    st.dataframe(
        recent_data,
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("🔔 System Status")
    st.success("✅ API Server: Online")
    st.success("✅ Database: Connected")
    st.success("✅ ML Models: Loaded")
    st.info("ℹ️ Last Update: " + datetime.now().strftime('%H:%M:%S'))

st.markdown("---")

# Charts section
st.subheader("📈 Prediction Trends (Last 7 Days)")

col1, col2 = st.columns(2)

with col1:
    # Sample chart data for sepsis predictions
    chart_data = pd.DataFrame({
        'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'Sepsis Predictions': [45, 52, 48, 61, 58, 43, 39],
        'High Risk': [8, 12, 9, 15, 11, 7, 8]
    })
    st.bar_chart(chart_data.set_index('Day'))
    st.caption("Sepsis Predictions per Day")

with col2:
    # Sample chart data for mortality predictions
    chart_data = pd.DataFrame({
        'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'Mortality Predictions': [62, 58, 71, 69, 75, 54, 45],
        'High Risk': [15, 12, 18, 17, 19, 11, 9]
    })
    st.bar_chart(chart_data.set_index('Day'))
    st.caption("Mortality Predictions per Day")
