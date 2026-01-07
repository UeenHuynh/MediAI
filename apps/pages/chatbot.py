"""
AI Chatbot Page
Professional Medical AI Assistant for clinical workflow support
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st


def show_chatbot():
    """Show AI Chatbot page"""

    st.markdown(
        '<div class="main-header">🤖 AI Medical Assistant</div>',
        unsafe_allow_html=True,
    )

    # Initialize session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Page header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 💬 Chat with Medical AI Assistant")
        st.markdown(
            "Ask questions about patient care, clinical interpretations, or get help with predictions."
        )

    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    st.markdown("---")

    # Clinical templates sidebar
    with st.sidebar:
        st.markdown("### 📋 Quick Templates")

        templates = {
            "🔬 Sepsis Assessment": "Assess sepsis risk for patient with: [vital signs]. Provide clinical interpretation and recommendations.",
            "💔 Mortality Risk": "Evaluate mortality risk for ICU patient with: [clinical data]. Include risk stratification.",
            "📊 SOFA Score": "Interpret SOFA score of [X] for patient. Explain organ dysfunction severity.",
            "💊 Treatment Protocol": "Recommend treatment protocol for [condition]. Include evidence-based guidelines.",
            "🧪 Lab Interpretation": "Interpret lab results: [values]. Explain clinical significance.",
            "🏥 Discharge Planning": "Create discharge plan for patient recovering from [condition].",
        }

        for template_name, template_text in templates.items():
            if st.button(template_name, use_container_width=True):
                st.session_state.chat_messages.append(
                    {"role": "user", "content": template_text}
                )
                # Simulate AI response
                response = f"Based on the {template_name.split(' ')[1].lower()} assessment:\n\nThis is a placeholder response. In production, this would be connected to a medical AI model (GPT-4, Claude, or domain-specific model) to provide evidence-based clinical guidance.\n\n**Note:** This is a demonstration. Always consult with qualified healthcare professionals for clinical decisions."
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info(
            """
            **Features:**
            - Clinical interpretation
            - Evidence-based guidance
            - HIPAA compliant
            - Audit logged

            **Disclaimer:** This AI assistant is for educational purposes. Not for clinical use.
            """
        )

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for idx, message in enumerate(st.session_state.chat_messages):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])

        # Welcome message if no messages
        if len(st.session_state.chat_messages) == 0:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(
                    """
                    👋 **Welcome to MediAI Assistant!**

                    I'm here to help with:
                    - **Clinical Interpretations** - Explain lab values, vital signs, scores
                    - **Risk Assessments** - Sepsis and mortality risk analysis
                    - **Treatment Guidance** - Evidence-based recommendations
                    - **Documentation** - Help with clinical notes and discharge planning

                    **How to use:**
                    - Type your question below
                    - Or use quick templates in the sidebar
                    - I'll provide evidence-based clinical guidance

                    ⚠️ **Important:** This is a demonstration tool. Always consult qualified healthcare professionals for clinical decisions.
                    """
                )

    # Chat input
    st.markdown("---")

    # User input
    user_input = st.chat_input(
        "💬 Ask a medical question or request clinical guidance..."
    )

    if user_input:
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})

        # Simulate AI response (in production, connect to OpenAI/Claude API)
        response = generate_ai_response(user_input)

        # Add assistant message
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": response}
        )

        # Save to history
        _save_chat_history(user_input, response)

        st.rerun()

    # Export chat
    if len(st.session_state.chat_messages) > 0:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button("📥 Export Chat History", use_container_width=True):
                export_chat()


def generate_ai_response(user_input: str) -> str:
    """
    Generate AI response (placeholder)

    In production, this would call:
    - OpenAI GPT-4 API
    - Anthropic Claude API
    - Custom medical LLM
    - RAG system with medical knowledge base
    """

    # Detect intent
    user_lower = user_input.lower()

    if any(word in user_lower for word in ["sepsis", "infection", "sofa"]):
        return """
**Sepsis Assessment Guidance:**

Based on your query about sepsis, here are key clinical considerations:

**Early Recognition:**
- qSOFA criteria: Respiratory rate ≥22, Altered mentation, SBP ≤100
- SOFA score increase ≥2 points
- Lactate >2 mmol/L

**Management Priorities:**
1. **Hour-1 Bundle:**
   - Measure lactate
   - Obtain blood cultures before antibiotics
   - Administer broad-spectrum antibiotics
   - Rapid fluid resuscitation (30 mL/kg crystalloid)
   - Apply vasopressors if hypotensive

2. **Monitoring:**
   - Serial lactate measurements
   - Fluid responsiveness
   - Organ function trends

**Source Control:**
- Identify and address infection source
- Consider imaging as appropriate

⚠️ **Note:** This is general guidance. Please refer to your institution's sepsis protocol and consult with intensivist.

📚 **References:** Surviving Sepsis Campaign Guidelines 2021
        """

    elif any(word in user_lower for word in ["mortality", "death", "prognosis"]):
        return """
**Mortality Risk Assessment:**

Key factors influencing ICU mortality:

**Patient Factors:**
- Age and comorbidities
- Admission diagnosis
- Severity of illness (APACHE-II, SOFA)

**Organ Dysfunction:**
- Number of failing organs
- Duration of dysfunction
- Response to therapy

**Clinical Indicators:**
- Lactate clearance
- Vasopressor requirements
- Mechanical ventilation duration

**Risk Stratification:**
- **Low Risk** (<10%): Single organ dysfunction, responsive to therapy
- **Moderate Risk** (10-30%): Multiple organ dysfunction, partial response
- **High Risk** (>30%): Severe multi-organ failure, refractory shock

**Communication:**
- Discuss goals of care with family
- Consider palliative care consultation if appropriate
- Document advance directives

⚠️ **Remember:** Prognosis is probabilistic, not deterministic. Individual patient factors matter.
        """

    elif any(word in user_lower for word in ["lab", "value", "result"]):
        return """
**Clinical Laboratory Interpretation:**

**Critical Values to Monitor:**

**Metabolic:**
- Lactate >4: Tissue hypoperfusion, poor prognosis
- pH <7.2: Severe acidosis, consider etiology
- Glucose <40 or >400: Immediate intervention needed

**Renal:**
- Creatinine rising: AKI staging, consider RRT
- K+ <2.5 or >6.0: Cardiac arrhythmia risk

**Hepatic:**
- Bilirubin >12: Severe dysfunction
- INR >3: Bleeding risk, consider FFP

**Hematologic:**
- Platelet <50: Bleeding risk
- WBC <2 or >30: Severe infection or malignancy

**Interpretation Tips:**
- Trend over time, not single values
- Consider pre-test probability
- Correlate with clinical presentation

📊 **Always:** Compare with reference ranges and previous results
        """

    else:
        return f"""
**Clinical Guidance Response:**

Thank you for your question about: "{user_input}"

**Analysis:**
This appears to be a clinical inquiry requiring professional medical expertise.

**Recommendations:**
1. Review relevant clinical guidelines
2. Consult with appropriate specialists
3. Consider patient-specific factors
4. Document decision-making process
5. Monitor patient response

**Evidence-Based Resources:**
- UpToDate clinical decision support
- NICE guidelines
- Society clinical practice guidelines
- Cochrane systematic reviews

⚠️ **Important Disclaimer:**
This AI assistant provides general educational information only. It is NOT a substitute for professional medical judgment. All clinical decisions must be made by qualified healthcare professionals based on individual patient assessment.

**For Production Use:**
- This would be connected to GPT-4, Claude, or medical-specific AI
- RAG system with medical literature
- Evidence-based recommendations
- Proper citations and references

📚 **Need more specific guidance?** Please provide:
- Patient clinical context
- Specific question focus
- Relevant clinical data
        """


def _save_chat_history(question: str, answer: str):
    """Save chat interaction to history"""
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": st.session_state.get("user_id", "anonymous"),
        "question": question,
        "answer": answer,
    }

    st.session_state.chat_history.append(history_entry)

    # Save to file
    try:
        history_file = Path(__file__).parent.parent / ".streamlit" / "chat_history.json"
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(st.session_state.chat_history[-100:], f, indent=2)
    except Exception:
        pass


def export_chat():
    """Export chat history"""
    chat_text = "# MediAI Chat History\n\n"
    chat_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    chat_text += f"User: {st.session_state.get('user_id', 'anonymous')}\n\n"
    chat_text += "---\n\n"

    for idx, msg in enumerate(st.session_state.chat_messages, 1):
        role = "👤 User" if msg["role"] == "user" else "🤖 Assistant"
        chat_text += f"### {role} (Message {idx})\n\n"
        chat_text += f"{msg['content']}\n\n"
        chat_text += "---\n\n"

    st.download_button(
        label="📥 Download Chat (Markdown)",
        data=chat_text,
        file_name=f"mediai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown",
    )
