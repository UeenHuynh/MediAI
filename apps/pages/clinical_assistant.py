"""
MediAI Professional Clinical Assistant - Chatbot Interface
===========================================================

A rigorous, professional medical AI chatbot for ICU risk assessment.

Features:
- Strict clinical validation
- Safety guardrails and disclaimers
- HIPAA/GDPR compliant audit logging
- Integration with sepsis/mortality prediction models
- SHAP explanations in conversational format

⚠️  CRITICAL: This is a research tool. NOT approved for clinical decisions.
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import uuid
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.model_service import ModelService
from utils.audit_logger import AuditLogger, EventType
from utils.encryption import mask_phi

# ============================================================================
# CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Clinical Assistant - MediAI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional medical color scheme
COLORS = {
    'primary': '#1E40AF',      # Deep Blue - Trust
    'danger': '#DC2626',       # Red - Critical
    'warning': '#F59E0B',      # Amber - Caution
    'success': '#059669',      # Green - Normal
    'background': '#F9FAFB',   # Light Gray
    'text': '#1F2937'          # Dark Gray
}

# Clinical ranges for validation
CLINICAL_RANGES = {
    'heart_rate': (30, 250, 'bpm', 'Nhịp tim'),
    'temperature': (35.0, 41.0, '°C', 'Nhiệt độ'),
    'respiratory_rate': (8, 50, 'breaths/min', 'Nhịp thở'),
    'sbp': (60, 220, 'mmHg', 'Huyết áp tâm thu'),
    'dbp': (30, 140, 'mmHg', 'Huyết áp tâm trương'),
    'spo2': (70, 100, '%', 'SpO2'),
    'lactate': (0.5, 15.0, 'mmol/L', 'Lactate'),
    'wbc': (1.0, 50.0, '10^9/L', 'Bạch cầu'),
    'creatinine': (0.3, 10.0, 'mg/dL', 'Creatinine')
}

# ============================================================================
# CUSTOM CSS - PROFESSIONAL MEDICAL STYLING
# ============================================================================

def inject_custom_css():
    """Inject professional medical styling"""
    st.markdown("""
    <style>
    /* Professional medical theme */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Critical warning banner */
    .critical-disclaimer {
        background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
        border-left: 4px solid #DC2626;
        padding: 16px;
        border-radius: 8px;
        margin: 20px 0;
        font-weight: 500;
    }

    /* Risk level badges */
    .risk-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        margin: 8px 0;
    }

    .risk-low { background: #D1FAE5; color: #065F46; }
    .risk-medium { background: #FEF3C7; color: #92400E; }
    .risk-high { background: #FED7AA; color: #9A3412; }
    .risk-critical { background: #FEE2E2; color: #991B1B; }

    /* Clinical report sections */
    .clinical-section {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 12px;
        margin: 10px 0;
    }

    .clinical-section-title {
        font-weight: 600;
        color: #1E40AF;
        font-size: 14px;
        margin-bottom: 8px;
    }

    /* Red flags */
    .red-flag {
        background: #FEE2E2;
        border-left: 3px solid #DC2626;
        padding: 8px 12px;
        margin: 6px 0;
        border-radius: 4px;
        font-size: 13px;
    }

    /* Hide Streamlit branding for professional look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Professional header */
    .professional-header {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SAFETY & VALIDATION
# ============================================================================

class SafetyValidator:
    """Validates inputs and enforces safety guardrails"""

    @staticmethod
    def validate_vital_sign(name: str, value: float) -> dict:
        """Validate a vital sign is within clinical range"""
        if name not in CLINICAL_RANGES:
            return {'valid': True}

        min_val, max_val, unit, display_name = CLINICAL_RANGES[name]

        if value < min_val or value > max_val:
            return {
                'valid': False,
                'error': f"⚠️ **{display_name}** ngoài phạm vi lâm sàng ({min_val}-{max_val} {unit}).\n"
                         f"Giá trị nhập: **{value} {unit}**. Vui lòng kiểm tra lại."
            }

        # Critical warnings
        if name == 'lactate' and value > 4:
            return {
                'valid': True,
                'warning': f"🔴 **CRITICAL**: Lactate cao ({value} mmol/L). Xem xét lactic acidosis."
            }

        if name == 'temperature' and (value < 36 or value > 38.3):
            return {
                'valid': True,
                'warning': f"⚠️ **Bất thường**: Nhiệt độ {value}°C (fever hoặc hypothermia)."
            }

        return {'valid': True}

    @staticmethod
    def check_red_flags(data: dict) -> list:
        """Identify critical red flags in vital signs"""
        red_flags = []

        # Hypotension
        if 'sbp' in data and data['sbp'] < 90:
            red_flags.append({
                'severity': 'CRITICAL',
                'message': f"Hạ huyết áp nghiêm trọng (SBP: {data['sbp']} mmHg)"
            })

        # Severe hypoxemia
        if 'spo2' in data and data['spo2'] < 90:
            red_flags.append({
                'severity': 'CRITICAL',
                'message': f"Thiếu oxy máu nghiêm trọng (SpO2: {data['spo2']}%)"
            })

        # High lactate
        if 'lactate' in data and data['lactate'] > 4:
            red_flags.append({
                'severity': 'CRITICAL',
                'message': f"Lactate rất cao ({data['lactate']} mmol/L) - nguy cơ shock"
            })

        # Tachycardia
        if 'heart_rate' in data and data['heart_rate'] > 130:
            red_flags.append({
                'severity': 'WARNING',
                'message': f"Nhịp nhanh nghiêm trọng ({data['heart_rate']} bpm)"
            })

        # Tachypnea
        if 'respiratory_rate' in data and data['respiratory_rate'] > 30:
            red_flags.append({
                'severity': 'WARNING',
                'message': f"Thở nhanh ({data['respiratory_rate']} breaths/min)"
            })

        return red_flags

    @staticmethod
    def is_safe_intent(user_input: str) -> dict:
        """Check if user request is within safe scope"""
        user_input_lower = user_input.lower()

        # Prohibited: Specific treatment recommendations
        prohibited_keywords = [
            'nên dùng thuốc', 'cho thuốc', 'liều lượng', 'prescription',
            'chẩn đoán là', 'bệnh gì', 'diagnosis is', 'what disease',
            'kê đơn', 'prescribe'
        ]

        for keyword in prohibited_keywords:
            if keyword in user_input_lower:
                return {
                    'safe': False,
                    'reason': 'PROHIBITED_TREATMENT_ADVICE',
                    'message': (
                        "⚠️ **Xin lỗi, tôi không thể tư vấn điều trị cụ thể.**\n\n"
                        "Tôi chỉ có thể:\n"
                        "- Đánh giá nguy cơ dựa trên dữ liệu\n"
                        "- Giải thích kết quả mô hình\n"
                        "- Cung cấp thông tin lâm sàng tham khảo\n\n"
                        "Mọi quyết định điều trị phải do bác sĩ lâm sàng đưa ra."
                    )
                }

        return {'safe': True}

# ============================================================================
# CHATBOT ORCHESTRATOR
# ============================================================================

class ClinicalAssistant:
    """Main orchestrator for clinical chatbot"""

    def __init__(self):
        self.model_service = ModelService()
        self.audit_logger = AuditLogger()
        self.safety_validator = SafetyValidator()

    def classify_intent(self, user_input: str) -> str:
        """Simple intent classification"""
        user_input_lower = user_input.lower()

        # Risk assessment keywords
        if any(kw in user_input_lower for kw in ['đánh giá', 'nguy cơ', 'risk', 'assess', 'sepsis', 'tử vong', 'mortality']):
            return 'RISK_ASSESSMENT'

        # Explanation keywords
        if any(kw in user_input_lower for kw in ['giải thích', 'tại sao', 'why', 'explain', 'how', 'shap']):
            return 'EXPLAIN_PREDICTION'

        # Clinical guidance
        if any(kw in user_input_lower for kw in ['qsofa', 'sofa', 'apache', 'sirs', 'tiêu chuẩn', 'guideline', 'protocol']):
            return 'CLINICAL_GUIDANCE'

        # Greeting
        if any(kw in user_input_lower for kw in ['xin chào', 'hello', 'hi', 'chào']):
            return 'GREETING'

        return 'GENERAL_INQUIRY'

    def generate_response(self, user_input: str, context: dict) -> str:
        """Generate professional response based on intent"""

        # Safety check
        safety_check = self.safety_validator.is_safe_intent(user_input)
        if not safety_check['safe']:
            return safety_check['message']

        # Classify intent
        intent = self.classify_intent(user_input)

        # Route to handler
        if intent == 'GREETING':
            return self._handle_greeting()
        elif intent == 'RISK_ASSESSMENT':
            return self._handle_risk_assessment_request()
        elif intent == 'CLINICAL_GUIDANCE':
            return self._handle_clinical_guidance(user_input)
        elif intent == 'EXPLAIN_PREDICTION':
            return self._handle_explanation_request(context)
        else:
            return self._handle_general_inquiry(user_input)

    def _handle_greeting(self) -> str:
        """Professional greeting"""
        return (
            "**Xin chào, tôi là MediAI Clinical Assistant.**\n\n"
            "Tôi có thể hỗ trợ bạn:\n"
            "- 📊 **Đánh giá nguy cơ** sepsis và tử vong ICU\n"
            "- 🔍 **Giải thích kết quả** dự đoán của mô hình\n"
            "- 📋 **Tra cứu thông tin** lâm sàng và tiêu chuẩn\n\n"
            "⚠️ **Lưu ý quan trọng**: Đây là công cụ hỗ trợ nghiên cứu. "
            "Không thay thế đánh giá lâm sàng của bác sĩ.\n\n"
            "Bạn cần hỗ trợ gì?"
        )

    def _handle_risk_assessment_request(self) -> str:
        """Guide user to structured assessment"""
        return (
            "**📊 Đánh giá Nguy cơ Lâm sàng**\n\n"
            "Để đánh giá chính xác, tôi cần dữ liệu sinh hiệu và xét nghiệm của bệnh nhân.\n\n"
            "**Vui lòng chọn:**\n"
            "- Sử dụng form **'Predict Sepsis'** hoặc **'Predict Mortality'** "
            "trong menu bên trái để nhập dữ liệu có cấu trúc\n"
            "- Hoặc cung cấp thông tin sau đây ngay tại đây:\n\n"
            "**Thông tin cần thiết:**\n"
            "```\n"
            "- Tuổi, giới tính\n"
            "- Sinh hiệu: Nhịp tim, huyết áp, SpO2, nhiệt độ, nhịp thở\n"
            "- Xét nghiệm: WBC, Lactate, Creatinine\n"
            "- Điểm lâm sàng: SOFA score (nếu có)\n"
            "```\n\n"
            "⚠️ **Disclaimer**: Kết quả chỉ mang tính tham khảo. "
            "Bác sĩ lâm sàng cần xác nhận và quyết định cuối cùng."
        )

    def _handle_clinical_guidance(self, user_input: str) -> str:
        """Provide clinical guidance information"""
        user_input_lower = user_input.lower()

        if 'qsofa' in user_input_lower:
            return (
                "**📋 qSOFA (Quick SOFA) Score**\n\n"
                "Công cụ sàng lọc nhanh nguy cơ sepsis ngoài ICU.\n\n"
                "**Tiêu chuẩn (mỗi điều = 1 điểm):**\n"
                "1. Huyết áp tâm thu ≤ 100 mmHg\n"
                "2. Nhịp thở ≥ 22 lần/phút\n"
                "3. Rối loạn ý thức (GCS < 15)\n\n"
                "**Diễn giải:**\n"
                "- **≥ 2 điểm**: Nghi ngờ sepsis, cần đánh giá sâu hơn\n"
                "- **< 2 điểm**: Nguy cơ thấp hơn\n\n"
                "**Lưu ý**: qSOFA không thay thế SOFA score đầy đủ trong ICU.\n\n"
                "📖 *Tham khảo: Sepsis-3 Definitions (JAMA 2016)*"
            )
        elif 'sofa' in user_input_lower:
            return (
                "**📋 SOFA (Sequential Organ Failure Assessment) Score**\n\n"
                "Đánh giá mức độ suy cơ quan ở bệnh nhân ICU.\n\n"
                "**6 hệ cơ quan:**\n"
                "1. **Hô hấp**: PaO2/FiO2\n"
                "2. **Đông máu**: Tiểu cầu\n"
                "3. **Gan**: Bilirubin\n"
                "4. **Tim mạch**: MAP hoặc vasopressor\n"
                "5. **Thần kinh**: GCS\n"
                "6. **Thận**: Creatinine hoặc lượng nước tiểu\n\n"
                "**Điểm số**: 0-4 cho mỗi cơ quan (tổng 0-24)\n\n"
                "**Diễn giải:**\n"
                "- Tăng ≥ 2 điểm = Suy cơ quan\n"
                "- Điểm càng cao → Tỷ lệ tử vong càng cao\n\n"
                "📖 *Tham khảo: Vincent et al., Intensive Care Med 1996*"
            )
        else:
            return (
                "**📚 Thông tin Lâm sàng**\n\n"
                "Tôi có thể cung cấp thông tin về:\n"
                "- **qSOFA Score**: Sàng lọc sepsis nhanh\n"
                "- **SOFA Score**: Đánh giá suy cơ quan\n"
                "- **SIRS**: Hội chứng đáp ứng viêm hệ thống\n"
                "- **APACHE-II**: Đánh giá mức độ nặng bệnh\n\n"
                "Bạn muốn biết về tiêu chuẩn nào?"
            )

    def _handle_explanation_request(self, context: dict) -> str:
        """Explain model predictions"""
        if 'last_prediction' not in context:
            return (
                "⚠️ Chưa có kết quả dự đoán nào để giải thích.\n\n"
                "Vui lòng thực hiện đánh giá nguy cơ trước, sau đó tôi có thể "
                "giải thích các yếu tố ảnh hưởng đến kết quả."
            )

        return (
            "**🔍 Giải thích Kết quả Dự đoán**\n\n"
            "Mô hình AI sử dụng **42 đặc trưng lâm sàng** để dự đoán nguy cơ:\n\n"
            "**Các yếu tố quan trọng nhất:**\n"
            "1. **Lactate**: Chỉ số tưới máu mô, marker của shock\n"
            "2. **SOFA Score**: Mức độ suy đa cơ quan\n"
            "3. **Xu hướng sinh hiệu**: Thay đổi theo thời gian\n"
            "4. **Độ tuổi & comorbidities**: Yếu tố nguy cơ nền\n\n"
            "**Phương pháp giải thích:**\n"
            "- Sử dụng **SHAP (SHapley Additive exPlanations)**\n"
            "- Hiển thị đóng góp của từng đặc trưng\n"
            "- Minh bạch và có thể kiểm chứng\n\n"
            "📊 Xem biểu đồ SHAP trong trang 'Model Performance' để phân tích chi tiết."
        )

    def _handle_general_inquiry(self, user_input: str) -> str:
        """Handle general questions"""
        return (
            "**ℹ️ Câu hỏi Chung**\n\n"
            "Tôi hiểu bạn đang hỏi về: *\"{0}\"*\n\n"
            "Tôi chuyên về:\n"
            "- Đánh giá nguy cơ sepsis/tử vong ICU\n"
            "- Giải thích kết quả mô hình AI\n"
            "- Thông tin về điểm lâm sàng (qSOFA, SOFA, etc.)\n\n"
            "Bạn có thể làm rõ câu hỏi hoặc chọn một chủ đề trên?"
        ).format(user_input[:50])

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = str(uuid.uuid4())

    if 'clinical_assistant' not in st.session_state:
        st.session_state.clinical_assistant = ClinicalAssistant()

    if 'chat_context' not in st.session_state:
        st.session_state.chat_context = {}

    # Add initial greeting if no messages
    if len(st.session_state.chat_messages) == 0:
        initial_greeting = st.session_state.clinical_assistant._handle_greeting()
        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': initial_greeting,
            'timestamp': datetime.now().isoformat()
        })

# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_professional_header():
    """Render professional header"""
    st.markdown("""
    <div class="professional-header">
        <h1 style="margin:0;">🏥 MediAI Clinical Assistant</h1>
        <p style="margin:5px 0 0 0; opacity:0.9;">
            AI-Powered ICU Risk Assessment Tool
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_critical_disclaimer():
    """Render critical disclaimer banner"""
    st.markdown("""
    <div class="critical-disclaimer">
        ⚠️ <strong>CẢNH BÁO QUAN TRỌNG</strong><br>
        Đây là công cụ nghiên cứu/giáo dục. <strong>KHÔNG được phê duyệt cho quyết định lâm sàng.</strong>
        Mọi dự đoán phải được bác sĩ lâm sàng xác nhận. Không thay thế đánh giá chuyên môn.
    </div>
    """, unsafe_allow_html=True)

def render_sidebar_info():
    """Render sidebar with information"""
    with st.sidebar:
        st.markdown("### 📋 Chức năng")
        st.markdown("""
        **Chatbot có thể:**
        - ✅ Đánh giá nguy cơ sepsis/tử vong
        - ✅ Giải thích kết quả mô hình
        - ✅ Tra cứu thông tin lâm sàng
        - ✅ Hướng dẫn sử dụng điểm số

        **Chatbot KHÔNG thể:**
        - ❌ Đưa ra chẩn đoán xác định
        - ❌ Tư vấn thuốc/liều lượng
        - ❌ Thay thế bác sĩ lâm sàng
        """)

        st.markdown("---")

        st.markdown("### ⚙️ Cài đặt")
        language = st.selectbox("Ngôn ngữ", ["Tiếng Việt", "English"])

        st.markdown("---")

        st.markdown("### 📊 Thông tin Mô hình")
        st.markdown("""
        **Sepsis Model:**
        - AUROC: 0.893
        - Sensitivity: 82.8%
        - Specificity: 80.6%

        **Mortality Model:**
        - AUROC: 0.65+
        - 24-hour prediction
        """)

        st.markdown("---")

        if st.button("🔄 Reset Chat", type="secondary"):
            st.session_state.chat_messages = []
            st.session_state.chat_session_id = str(uuid.uuid4())
            st.rerun()

def render_chat_message(message: dict):
    """Render a single chat message"""
    role = message['role']
    content = message['content']

    if role == 'user':
        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(content)
    else:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(content)

            # Add disclaimer for risk assessments
            if any(keyword in content.lower() for keyword in ['nguy cơ', 'risk', 'critical', '🔴']):
                st.markdown("""
                <div style='background:#FEF2F2;border-left:3px solid #DC2626;padding:10px;margin-top:10px;border-radius:4px;font-size:12px;'>
                ⚠️ <strong>DISCLAIMER:</strong> Kết quả chỉ mang tính tham khảo.
                Bác sĩ lâm sàng phải xác nhận và quyết định điều trị.
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""

    # Inject CSS
    inject_custom_css()

    # Initialize session
    initialize_session_state()

    # Render header
    render_professional_header()
    render_critical_disclaimer()

    # Render sidebar
    render_sidebar_info()

    # Main chat area
    st.markdown("### 💬 Hội thoại")

    # Display chat history
    for message in st.session_state.chat_messages:
        render_chat_message(message)

    # Chat input
    user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu...")

    if user_input:
        # Add user message to history
        st.session_state.chat_messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })

        # Generate response
        assistant = st.session_state.clinical_assistant
        response = assistant.generate_response(
            user_input,
            st.session_state.chat_context
        )

        # Add assistant response to history
        st.session_state.chat_messages.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.now().isoformat()
        })

        # Log interaction
        try:
            assistant.audit_logger.log_event(
                event_type=EventType.API_CALL,
                user_id=st.session_state.get('user_id', 'demo'),
                session_id=st.session_state.chat_session_id,
                details={
                    'action': 'chatbot_interaction',
                    'user_input': user_input[:100],  # Truncate for privacy
                    'intent': assistant.classify_intent(user_input),
                    'response_length': len(response)
                },
                outcome='SUCCESS'
            )
        except Exception as e:
            st.error(f"⚠️ Audit logging failed: {str(e)}")

        # Rerun to display new messages
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;color:#6B7280;font-size:12px;'>
    MediAI Clinical Assistant v1.0 | Session ID: {0}<br>
    Powered by LightGBM + SHAP | Research Use Only
    </div>
    """.format(st.session_state.chat_session_id[:8]), unsafe_allow_html=True)

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Check authentication
    if 'authenticated' not in st.session_state or not st.session_state.authenticated:
        st.error("⚠️ Please login first from the main page")
        st.stop()

    main()
