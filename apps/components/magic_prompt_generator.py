"""
Magic Prompt Generator Component
Interactive UI for selecting and customizing medical prompt templates
"""

import streamlit as st
from typing import Optional, Dict
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.prompt_templates import MagicPromptTemplates


def show_magic_prompt_generator() -> Optional[str]:
    """
    Display magic prompt generator UI

    Returns:
        Generated prompt string if user clicks Generate, None otherwise
    """
    st.markdown("### ✨ Magic Prompt Generator")
    st.markdown("*Choose a template and customize it with your patient data*")

    # Get categories
    categories = MagicPromptTemplates.get_categories()

    # Category selection with emojis
    category_options = [f"{emoji} {name}" for emoji, name in categories.items()]
    category_display_to_key = {f"{emoji} {name}": key for key, (emoji, name) in
                                [(k, (v.split()[0], ' '.join(v.split()[1:])))
                                 for k, v in categories.items()]}

    selected_category_display = st.selectbox(
        "🏥 Select Category",
        options=category_options,
        help="Choose the clinical area for your question"
    )

    selected_category = category_display_to_key[selected_category_display]

    # Get templates for selected category
    templates = MagicPromptTemplates.get_templates_by_category(selected_category)

    if not templates:
        st.warning("No templates available for this category")
        return None

    # Template selection
    template_names = {key: data["name"] for key, data in templates.items()}
    template_key = st.selectbox(
        "📋 Select Template",
        options=list(template_names.keys()),
        format_func=lambda x: template_names[x],
        help="Choose a specific clinical scenario"
    )

    template_data = templates[template_key]

    # Show template description
    st.info(f"**Description:** {template_data['description']}")

    # Expandable section for data input
    with st.expander("📝 Fill in Patient Data (Optional)", expanded=True):
        st.markdown("*You can fill in the available data. Leave fields blank to keep as placeholders.*")

        placeholders = template_data.get("placeholders", [])
        user_values = {}

        # Create input fields for each placeholder
        if placeholders:
            # Group placeholders in 2 columns for better UX
            cols = st.columns(2)
            for idx, placeholder in enumerate(placeholders):
                with cols[idx % 2]:
                    # Format placeholder name for display
                    label = placeholder.replace("_", " ").title()
                    value = st.text_input(
                        label,
                        key=f"prompt_field_{template_key}_{placeholder}",
                        placeholder=f"Enter {label.lower()}..."
                    )
                    if value:
                        user_values[placeholder] = value

    # Preview section
    with st.expander("👀 Preview Generated Prompt", expanded=False):
        preview_prompt = MagicPromptTemplates.format_template(
            selected_category,
            template_key,
            **user_values
        )
        st.text_area(
            "Generated Prompt:",
            value=preview_prompt,
            height=300,
            disabled=True,
            key=f"preview_{template_key}"
        )

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("✨ Generate & Use This Prompt",
                     use_container_width=True,
                     type="primary",
                     key=f"generate_{template_key}"):
            generated_prompt = MagicPromptTemplates.format_template(
                selected_category,
                template_key,
                **user_values
            )
            return generated_prompt

    return None


def show_magic_prompt_sidebar():
    """
    Show a compact version of magic prompt generator in sidebar
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ✨ Quick Prompts")

        # Popular templates shortcuts
        if st.button("🦠 Sepsis Screening", use_container_width=True):
            st.session_state.selected_magic_template = ("sepsis", "sepsis_screening")

        if st.button("💔 Mortality Risk", use_container_width=True):
            st.session_state.selected_magic_template = ("mortality", "mortality_risk")

        if st.button("🔬 Critical Labs", use_container_width=True):
            st.session_state.selected_magic_template = ("labs", "critical_labs")

        if st.button("💊 Vasopressor Guide", use_container_width=True):
            st.session_state.selected_magic_template = ("medications", "vasopressor")

        if st.button("🚨 Cardiac Arrest", use_container_width=True):
            st.session_state.selected_magic_template = ("emergency", "cardiac_arrest")

        # Link to full generator
        st.markdown("---")
        if st.button("✨ Open Full Generator", use_container_width=True, key="open_full_gen"):
            st.session_state.show_magic_generator = True


def inject_magic_prompt_to_chat(prompt: str):
    """
    Inject a magic-generated prompt into the chat input

    Args:
        prompt: The generated prompt to inject
    """
    if "magic_prompt_to_send" not in st.session_state:
        st.session_state.magic_prompt_to_send = prompt
    else:
        st.session_state.magic_prompt_to_send = prompt


def get_quick_template_prompt(category: str, template_key: str) -> str:
    """
    Get a template prompt with empty placeholders

    Args:
        category: Template category
        template_key: Template identifier

    Returns:
        Template prompt string with placeholders
    """
    template_data = MagicPromptTemplates.get_template(category, template_key)
    if template_data:
        return template_data["template"]
    return ""
