"""
Legal Documents Page
Terms & Conditions and Privacy Policy
"""

from pathlib import Path

import streamlit as st


def show_legal():
    """Show legal documents"""

    st.markdown('<div class="page-header">📄 Legal Documents</div>', unsafe_allow_html=True)

    # Check if there's a request for specific tab
    if 'legal_tab' in st.session_state:
        if st.session_state.legal_tab == 'privacy':
            pass
        st.session_state.legal_tab = None  # Reset after use

    # Tabs for different documents
    tabs = st.tabs(["📋 Terms & Conditions", "🔒 Privacy Policy"])

    with tabs[0]:
        show_terms_and_conditions()

    with tabs[1]:
        show_privacy_policy()


def show_terms_and_conditions():
    """Display Terms and Conditions"""

    terms_file = Path(__file__).parent.parent / "docs" / "terms_and_conditions.md"

    if terms_file.exists():
        with open(terms_file, 'r', encoding='utf-8') as f:
            terms_content = f.read()

        st.markdown(terms_content)
    else:
        st.error("Terms and Conditions document not found.")


def show_privacy_policy():
    """Display Privacy Policy"""

    privacy_file = Path(__file__).parent.parent / "docs" / "privacy_policy.md"

    if privacy_file.exists():
        with open(privacy_file, 'r', encoding='utf-8') as f:
            privacy_content = f.read()

        st.markdown(privacy_content)
    else:
        st.error("Privacy Policy document not found.")
