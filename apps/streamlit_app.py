"""
MediAI Healthcare ML Platform - Streamlit UI
Main entry point for the Streamlit application.

IMPORTANT ARCHITECTURE NOTES:
- This is a SINGLE-PAGE app with custom navigation (NOT multi-page)
- Views are in 'views/' directory (NOT 'pages/') to prevent Streamlit auto-detection
- Custom CSS + JavaScript aggressively hide default sidebar navigation
- Configuration files (.pages.toml, config.toml) also disable navigation
- The sidebar ONLY contains our custom navigation menu with icons
"""
import streamlit as st
import sys
from pathlib import Path

# Add the apps directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="MediAI Healthcare ML Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"  # Keep sidebar expanded to show our custom nav
)

# Load CSS from external file and inject it
css_file_path = Path(__file__).parent / ".streamlit" / "hide_navigation.css"
try:
    with open(css_file_path, "r") as f:
        navigation_css = f.read()
except:
    navigation_css = ""  # Fallback if file doesn't exist

# Inject CSS to hide navigation
st.markdown(f"""
    <style>
        {navigation_css}

        /* Additional inline CSS */
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavLink"],
        [data-testid="stSidebarNavItems"],
        [data-testid="stSidebarNav"] *,
        [data-testid="stSidebarNavLink"] *,
        [data-testid="stSidebarNavItems"] *,
        section[data-testid="stSidebarNav"],
        div[data-testid="stSidebarNav"],
        nav[data-testid="stSidebarNav"],
        section[data-testid="stSidebarNav"] *,
        div[data-testid="stSidebarNav"] *,
        nav[data-testid="stSidebarNav"] * {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            width: 0px !important;
            max-height: 0px !important;
            max-width: 0px !important;
            overflow: hidden !important;
            opacity: 0 !important;
            position: absolute !important;
            left: -10000px !important;
            top: -10000px !important;
            z-index: -9999 !important;
            pointer-events: none !important;
        }

        /* Target specific emotion-cache classes from your screenshot */
        div.st-emotion-cache-79elbk,
        .st-emotion-cache-79elbk,
        div.eczjsme10,
        .eczjsme10,
        div.st-emotion-cache-79elbk *,
        .eczjsme10 * {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            opacity: 0 !important;
        }

        /* All children of stSidebarNav */
        [data-testid="stSidebarNav"] *,
        [data-testid="stSidebarNav"] ul,
        [data-testid="stSidebarNav"] li,
        [data-testid="stSidebarNav"] a {
            display: none !important;
            visibility: hidden !important;
        }

        /* Common CSS classes used by Streamlit navigation */
        .css-1544g2n,
        .css-17lntkn,
        .css-pkbazv,
        .st-emotion-cache-1544g2n,
        .st-emotion-cache-17lntkn {
            display: none !important;
            visibility: hidden !important;
        }

        /* Hide any nav elements in sidebar that are not our custom one */
        section[data-testid="stSidebar"] nav:not([id="custom-nav"]) {
            display: none !important;
        }

        /* Hide navigation links/lists in sidebar (except our radio group) */
        section[data-testid="stSidebar"] > div:first-child > div:first-child {
            /* This might be the default nav container */
        }

        /* Pattern matching for navigation-like structures */
        [class*="SidebarNav"],
        [class*="sidebar-nav"],
        [class*="nav-link"],
        [data-testid*="Nav"]:not([data-testid*="Radio"]) {
            display: none !important;
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
    from views import dashboard
    dashboard.show()

elif st.session_state.current_page == "🔬 Predict Sepsis":
    from views import predict_sepsis
    predict_sepsis.show()

elif st.session_state.current_page == "💔 Predict Mortality":
    from views import predict_mortality
    predict_mortality.show()

elif st.session_state.current_page == "📊 Model Performance":
    from views import model_performance
    model_performance.show()

elif st.session_state.current_page == "⚙️ Settings":
    from views import settings
    settings.show()
