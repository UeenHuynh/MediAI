"""
MediAI Healthcare ML Platform - Streamlit UI
Main entry point for the Streamlit application.
"""
import streamlit as st
import sys
from pathlib import Path

# Add the apps directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration
st.set_page_config(
    page_title="MediAI Healthcare ML Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed
)

# Custom CSS to hide the default Streamlit navigation and style the app
st.markdown("""
    <style>
        /* Hide the default Streamlit sidebar navigation */
        [data-testid="stSidebarNav"] {
            display: none;
        }

        /* Hide the sidebar collapse button when not needed */
        [data-testid="collapsedControl"] {
            display: none;
        }

        /* Custom styling for the navigation menu */
        .nav-menu {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }

        /* Style for the main header */
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 0.5rem;
        }

        .sub-header {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }

        /* Remove extra padding from Streamlit */
        .block-container {
            padding-top: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Dashboard"

# Main header
st.markdown('<div class="main-header">🏥 MediAI Healthcare ML Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">ICU Patient Risk Prediction System</div>', unsafe_allow_html=True)

# Create the navigation menu in the sidebar
with st.sidebar:
    st.markdown("### Navigation")

    # Navigation options with icons
    nav_options = [
        "🏠 Dashboard",
        "🔬 Predict Sepsis",
        "💔 Predict Mortality",
        "📊 Model Performance",
        "⚙️ Settings"
    ]

    # Create radio buttons for navigation
    selected_page = st.radio(
        "Go to",
        nav_options,
        index=nav_options.index(st.session_state.current_page),
        label_visibility="collapsed"
    )

    # Update session state if page changed
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()

    st.markdown("---")
    st.markdown("**Version:** 1.0.0")
    st.markdown("**Status:** 🟢 Online")

# Main content area - load the selected page
if st.session_state.current_page == "🏠 Dashboard":
    from pages import dashboard
    dashboard.show()

elif st.session_state.current_page == "🔬 Predict Sepsis":
    from pages import predict_sepsis
    predict_sepsis.show()

elif st.session_state.current_page == "💔 Predict Mortality":
    from pages import predict_mortality
    predict_mortality.show()

elif st.session_state.current_page == "📊 Model Performance":
    from pages import model_performance
    model_performance.show()

elif st.session_state.current_page == "⚙️ Settings":
    from pages import settings
    settings.show()
