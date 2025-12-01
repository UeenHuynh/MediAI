"""
Professional Medical AI Chatbot Assistant
Floating chatbot with advanced features for clinical workflow
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st


class MedicalChatbot:
    """Professional medical AI chatbot assistant"""

    def __init__(self):
        self.history_file = (
            Path(__file__).parent.parent / ".streamlit" / "chat_history.json"
        )
        self.templates_file = (
            Path(__file__).parent.parent / ".streamlit" / "templates.json"
        )
        self._init_session_state()
        self._load_history()
        self._load_templates()

    def _init_session_state(self):
        """Initialize session state for chatbot"""
        if "chat_open" not in st.session_state:
            st.session_state.chat_open = False
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "current_context" not in st.session_state:
            st.session_state.current_context = None

    def _load_history(self):
        """Load chat history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r") as f:
                    st.session_state.chat_history = json.load(f)
        except Exception:
            st.session_state.chat_history = []

    def _save_history(self):
        """Save chat history to file"""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w") as f:
                json.dump(
                    st.session_state.chat_history[-100:], f, indent=2
                )  # Keep last 100
        except Exception:
            pass

    def _load_templates(self):
        """Load clinical note templates"""
        if "templates" not in st.session_state:
            st.session_state.templates = {
                "Sepsis Assessment": {
                    "prompt": "Assess sepsis risk for patient with: [vital signs]. Provide clinical interpretation and recommendations.",
                    "category": "Clinical Assessment",
                    "icon": "🔬",
                },
                "Mortality Risk": {
                    "prompt": "Evaluate mortality risk for ICU patient with: [clinical data]. Include risk stratification and intervention recommendations.",
                    "category": "Risk Assessment",
                    "icon": "💔",
                },
                "SOFA Score Interpretation": {
                    "prompt": "Interpret SOFA score of [X] for patient. Explain organ dysfunction severity and prognosis.",
                    "category": "Clinical Scores",
                    "icon": "📊",
                },
                "Treatment Protocol": {
                    "prompt": "Recommend treatment protocol for [condition]. Include evidence-based guidelines and monitoring parameters.",
                    "category": "Treatment",
                    "icon": "💊",
                },
                "Lab Interpretation": {
                    "prompt": "Interpret lab results: [values]. Explain clinical significance and differential diagnosis.",
                    "category": "Diagnostics",
                    "icon": "🧪",
                },
                "Discharge Planning": {
                    "prompt": "Create discharge plan for patient recovering from [condition]. Include follow-up care and red flags.",
                    "category": "Care Planning",
                    "icon": "🏥",
                },
            }

    def render(self):
        """Render the floating chatbot"""

        # Floating button CSS
        st.markdown(
            """
        <style>
        .chatbot-toggle {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
            z-index: 9999;
            transition: all 0.3s ease;
        }

        .chatbot-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
        }

        .chatbot-toggle-icon {
            color: white;
            font-size: 28px;
            font-weight: bold;
        }

        .chatbot-window {
            position: fixed;
            bottom: 100px;
            right: 30px;
            width: 420px;
            height: 650px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            z-index: 9998;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chatbot-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            font-weight: 600;
            font-size: 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chatbot-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            opacity: 0.9;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .chatbot-body {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8fafc;
        }

        .chat-message {
            margin-bottom: 16px;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message-user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 16px;
            border-radius: 16px 16px 4px 16px;
            margin-left: 40px;
        }

        .message-assistant {
            background: white;
            color: #1e293b;
            padding: 12px 16px;
            border-radius: 16px 16px 16px 4px;
            margin-right: 40px;
            border: 1px solid #e2e8f0;
        }

        .message-time {
            font-size: 11px;
            opacity: 0.6;
            margin-top: 6px;
        }

        .quick-actions {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
            margin-bottom: 16px;
        }

        .quick-action-btn {
            background: white;
            border: 2px solid #e2e8f0;
            padding: 12px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
            font-size: 13px;
            font-weight: 500;
        }

        .quick-action-btn:hover {
            border-color: #667eea;
            background: #f0f4ff;
            transform: translateY(-2px);
        }

        .template-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .template-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
            transform: translateX(4px);
        }

        .template-icon {
            font-size: 24px;
            margin-bottom: 8px;
        }

        .template-title {
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 4px;
        }

        .template-category {
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .context-banner {
            background: #fef3c7;
            border: 1px solid #fbbf24;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 13px;
            color: #92400e;
        }

        .disclaimer {
            background: #fee2e2;
            border: 1px solid #fca5a5;
            padding: 12px;
            border-radius: 8px;
            font-size: 12px;
            color: #991b1b;
            margin-top: 12px;
            line-height: 1.5;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

        # Toggle button
        if st.button("", key="chatbot_toggle", help="Open AI Assistant"):
            st.session_state.chat_open = not st.session_state.chat_open

        # Render chatbot window if open
        if st.session_state.chat_open:
            self._render_chatbot_window()

    def _render_chatbot_window(self):
        """Render the chatbot window"""

        with st.container():
            st.markdown('<div class="chatbot-window">', unsafe_allow_html=True)

            # Header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### 🤖 MediAI Assistant")
                st.markdown(
                    '<div class="chatbot-status"><span class="status-dot"></span>Active</div>',
                    unsafe_allow_html=True,
                )
            with col2:
                if st.button("✕", key="close_chat"):
                    st.session_state.chat_open = False
                    st.rerun()

            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(
                ["💬 Chat", "⚡ Quick", "📋 Templates", "📊 History"]
            )

            with tab1:
                self._render_chat_tab()

            with tab2:
                self._render_quick_actions()

            with tab3:
                self._render_templates()

            with tab4:
                self._render_history()

            st.markdown("</div>", unsafe_allow_html=True)

    def _render_chat_tab(self):
        """Render main chat interface"""

        # Context banner if exists
        if st.session_state.current_context:
            st.info(f"📍 Context: {st.session_state.current_context}")

        # Chat messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    st.markdown(
                        f"""
                    <div class="chat-message">
                        <div class="message-user">
                            {msg['content']}
                            <div class="message-time">{msg['time']}</div>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                    <div class="chat-message">
                        <div class="message-assistant">
                            {msg['content']}
                            <div class="message-time">{msg['time']}</div>
                        </div>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # Input
        st.markdown("---")
        user_input = st.text_area(
            "Ask me anything about patient care, clinical guidelines, or MediAI features...",
            height=100,
            key="chat_input",
        )

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("Send", type="primary", use_container_width=True):
                if user_input.strip():
                    self._send_message(user_input)
                    st.rerun()
        with col2:
            if st.button("Clear", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()
        with col3:
            if st.button("🎤", use_container_width=True):
                st.info("Voice input coming soon")

        # Disclaimer
        st.markdown(
            """
        <div class="disclaimer">
            ⚠️ <strong>Medical Disclaimer:</strong> This AI assistant provides general information only.
            Always verify critical decisions with qualified healthcare professionals.
            Not a substitute for professional medical advice.
        </div>
        """,
            unsafe_allow_html=True,
        )

    def _render_quick_actions(self):
        """Render quick action shortcuts"""

        st.markdown("### ⚡ Quick Actions")
        st.caption("Common tasks and shortcuts")

        quick_actions = [
            {"icon": "🔬", "title": "Predict Sepsis", "page": "Predict_Sepsis"},
            {"icon": "💔", "title": "Predict Mortality", "page": "Predict_Mortality"},
            {"icon": "📊", "title": "View Performance", "page": "Model_Performance"},
            {"icon": "📈", "title": "Dashboard", "page": "Dashboard"},
            {"icon": "📋", "title": "Generate Report", "action": "report"},
            {"icon": "🔍", "title": "Explain Prediction", "action": "explain"},
            {"icon": "📚", "title": "Guidelines", "action": "guidelines"},
            {"icon": "⚙️", "title": "Settings", "page": "Settings"},
        ]

        for i in range(0, len(quick_actions), 2):
            col1, col2 = st.columns(2)

            with col1:
                action = quick_actions[i]
                if st.button(
                    f"{action['icon']} {action['title']}",
                    key=f"qa_{i}",
                    use_container_width=True,
                ):
                    if "page" in action:
                        st.switch_page(f"pages/{action['page']}.py")
                    else:
                        self._handle_quick_action(action["action"])

            if i + 1 < len(quick_actions):
                with col2:
                    action = quick_actions[i + 1]
                    if st.button(
                        f"{action['icon']} {action['title']}",
                        key=f"qa_{i+1}",
                        use_container_width=True,
                    ):
                        if "page" in action:
                            st.switch_page(f"pages/{action['page']}.py")
                        else:
                            self._handle_quick_action(action["action"])

    def _render_templates(self):
        """Render template library"""

        st.markdown("### 📋 Clinical Templates")
        st.caption("Pre-built prompts for common scenarios")

        # Category filter
        categories = list(
            set(t["category"] for t in st.session_state.templates.values())
        )
        selected_category = st.selectbox(
            "Filter by category", ["All"] + sorted(categories)
        )

        # Display templates
        for name, template in st.session_state.templates.items():
            if selected_category == "All" or template["category"] == selected_category:
                with st.expander(f"{template['icon']} {name}"):
                    st.markdown(f"**Category:** {template['category']}")
                    st.code(template["prompt"], language=None)

                    if st.button("Use Template", key=f"use_{name}"):
                        st.session_state.chat_messages.append(
                            {
                                "role": "user",
                                "content": template["prompt"],
                                "time": datetime.now().strftime("%H:%M"),
                            }
                        )
                        self._send_message(template["prompt"])
                        st.rerun()

    def _render_history(self):
        """Render chat history"""

        st.markdown("### 📊 Chat History")
        st.caption("Your recent conversations")

        if not st.session_state.chat_history:
            st.info("No history yet. Start chatting to build your history!")
            return

        # Display history (last 20)
        for i, entry in enumerate(reversed(st.session_state.chat_history[-20:])):
            with st.expander(f"{entry['time']} - {entry['query'][:50]}..."):
                st.markdown(f"**Query:** {entry['query']}")
                st.markdown(f"**Response:** {entry['response']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Reuse", key=f"reuse_{i}"):
                        self._send_message(entry["query"])
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"del_{i}"):
                        st.session_state.chat_history.remove(entry)
                        self._save_history()
                        st.rerun()

        if st.button("Clear All History", type="secondary"):
            st.session_state.chat_history = []
            self._save_history()
            st.rerun()

    def _send_message(self, message: str):
        """Send message and get response"""

        # Add user message
        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": message,
                "time": datetime.now().strftime("%H:%M"),
            }
        )

        # Generate response (mock for now - integrate with real AI)
        response = self._generate_response(message)

        # Add assistant message
        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": response,
                "time": datetime.now().strftime("%H:%M"),
            }
        )

        # Save to history
        st.session_state.chat_history.append(
            {
                "query": message,
                "response": response,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "context": st.session_state.current_context,
            }
        )
        self._save_history()

    def _generate_response(self, message: str) -> str:
        """Generate AI response (mock implementation)"""

        message_lower = message.lower()

        # Context-aware responses
        if "sepsis" in message_lower:
            return """
**Sepsis Assessment Guidance:**

MediAI's sepsis prediction model uses 42 clinical features including:
- Vital signs (HR, BP, temp, RR, SpO2)
- Lab values (lactate, WBC, platelets)
- Clinical scores (SOFA, qSOFA, SIRS)

**Key Points:**
• AUROC: 0.893 (excellent discrimination)
• Early detection: 6-hour prediction window
• Risk stratification: Low/Medium/High/Critical

**Recommendations:**
1. Enter current vital signs
2. Include recent lab results
3. Review risk assessment
4. Follow clinical protocol

📍 Navigate to: Predict Sepsis page
            """

        elif "mortality" in message_lower:
            return """
**Mortality Risk Assessment:**

Our mortality model evaluates 13 key factors:
- Worst values in first 24h
- SOFA Day 1 score
- APACHE-II score
- Vasopressor requirements

**Performance:**
• AUROC: 0.645
• Risk categories: Low (<20%), Medium (20-50%), High (50-75%), Critical (>75%)

**Clinical Use:**
1. Collect worst physiological values
2. Calculate clinical scores
3. Review risk stratification
4. Adjust care intensity

📍 Navigate to: Predict Mortality page
            """

        elif "model" in message_lower or "performance" in message_lower:
            return """
**Model Performance Metrics:**

**Sepsis Model (LightGBM):**
- AUROC: 0.893
- Sensitivity: 82.8%
- Specificity: 80.6%
- Features: 42

**Mortality Model (LightGBM):**
- AUROC: 0.645
- Sensitivity: 59.9%
- Specificity: 60.0%
- Features: 13

View detailed metrics, ROC curves, and feature importance on the Model Performance page.

📊 Navigate to: Model Performance page
            """

        elif any(word in message_lower for word in ["help", "how", "guide"]):
            return """
**MediAI Quick Guide:**

**Main Features:**
1. 🔬 Sepsis Prediction - Early warning system
2. 💔 Mortality Risk - ICU outcome prediction
3. 📊 Model Performance - Metrics & validation
4. ⚙️ Settings - Customize experience

**How to Use:**
• Enter patient data in prediction forms
• Review risk scores and recommendations
• Check model performance metrics
• Adjust settings as needed

**Need Help?**
• Use Quick Actions for common tasks
• Browse Templates for clinical scenarios
• Check History for past queries

💡 Tip: All predictions are logged for audit compliance
            """

        else:
            return f"""
I understand you're asking about: "{message}"

**Available Resources:**
• Sepsis prediction and risk assessment
• Mortality risk stratification
• Model performance metrics
• Clinical guidelines and protocols

**How can I help?**
- Ask about specific clinical scenarios
- Request feature explanations
- Get guidance on model interpretation
- Access quick actions and templates

💬 Try asking: "How do I predict sepsis?" or "Explain mortality model"
            """

    def _handle_quick_action(self, action: str):
        """Handle quick action"""

        responses = {
            "report": "Report generation feature coming soon! You'll be able to generate PDF reports with predictions and explanations.",
            "explain": "To explain a prediction, navigate to the prediction page and submit your patient data. The results page will show risk factors and SHAP explanations.",
            "guidelines": "Clinical guidelines are integrated into our prediction recommendations. Each risk assessment includes evidence-based guidance.",
        }

        st.info(responses.get(action, "Feature coming soon!"))


def render_chatbot():
    """Main function to render chatbot"""
    chatbot = MedicalChatbot()
    chatbot.render()
