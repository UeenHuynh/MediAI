"""
MediAI Floating Clinical Assistant Widget
==========================================

A professional floating chatbot that appears on all pages as a question mark
icon in the bottom right corner. Provides context-aware help and guidance.

Features:
- Floating button with professional medical icon
- Collapsible chat panel
- Context-aware responses based on current page
- Professional medical styling
- HIPAA-compliant audit logging
"""

import streamlit as st
import uuid
from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.audit_logger import AuditLogger, EventType
except ImportError:
    AuditLogger = None
    EventType = None

# ============================================================================
# CONFIGURATION
# ============================================================================

# Context information for each page
PAGE_CONTEXTS = {
    'Home': {
        'title': 'Trang chủ MediAI',
        'description': 'Hệ thống dự đoán nguy cơ ICU',
        'help_topics': [
            'Hệ thống MediAI là gì?',
            'Các chức năng chính',
            'Cách bắt đầu sử dụng',
            'Quy trình đánh giá nguy cơ'
        ],
        'quick_actions': [
            'Đánh giá nguy cơ sepsis',
            'Đánh giá nguy cơ tử vong',
            'Xem dashboard'
        ]
    },
    'Predict Sepsis': {
        'title': 'Dự đoán Nguy cơ Sepsis',
        'description': 'Form nhập liệu đánh giá nguy cơ nhiễm trùng huyết',
        'help_topics': [
            'Các trường dữ liệu cần nhập',
            'Phạm vi giá trị hợp lệ',
            'SOFA score là gì?',
            'Cách diễn giải kết quả',
            'Độ tin cậy của mô hình'
        ],
        'quick_actions': [
            'Giải thích các trường bắt buộc',
            'Ví dụ dữ liệu mẫu',
            'Xem tiêu chuẩn lâm sàng'
        ]
    },
    'Predict Mortality': {
        'title': 'Dự đoán Nguy cơ Tử vong',
        'description': 'Form đánh giá tỷ lệ tử vong ICU 24h',
        'help_topics': [
            'Các yếu tố nguy cơ tử vong',
            'APACHE-II score',
            'Phân tầng nguy cơ',
            'Khi nào cần leo thang điều trị'
        ],
        'quick_actions': [
            'Giải thích các trường',
            'Xem hướng dẫn ICU',
            'Tiêu chuẩn APACHE-II'
        ]
    },
    'Dashboard': {
        'title': 'Dashboard Giám sát',
        'description': 'Theo dõi xu hướng và chỉ số lâm sàng',
        'help_topics': [
            'Các biểu đồ hiển thị gì?',
            'Cách đọc xu hướng sinh hiệu',
            'Cảnh báo bất thường',
            'Xuất dữ liệu phân tích'
        ],
        'quick_actions': [
            'Giải thích các biểu đồ',
            'Cách lọc dữ liệu',
            'Xuất báo cáo'
        ]
    },
    'Model Performance': {
        'title': 'Hiệu suất Mô hình',
        'description': 'Metrics và đánh giá chất lượng AI',
        'help_topics': [
            'AUROC là gì?',
            'Sensitivity vs Specificity',
            'Calibration curve',
            'SHAP explanations',
            'Confusion matrix'
        ],
        'quick_actions': [
            'Giải thích các metrics',
            'So sánh các mô hình',
            'Xem SHAP values'
        ]
    },
    'Settings': {
        'title': 'Cài đặt Hệ thống',
        'description': 'Cấu hình và tùy chỉnh',
        'help_topics': [
            'Thay đổi mật khẩu',
            'Cài đặt thông báo',
            'Quản lý phiên đăng nhập',
            'Xuất audit logs'
        ],
        'quick_actions': [
            'Cấu hình bảo mật',
            'Quản lý người dùng',
            'Xem lịch sử hoạt động'
        ]
    }
}

# ============================================================================
# CONTEXT-AWARE ASSISTANT
# ============================================================================

class ContextAwareAssistant:
    """Chatbot that understands the current page context"""

    def __init__(self):
        if AuditLogger:
            self.audit_logger = AuditLogger()
        else:
            self.audit_logger = None

    def get_current_page_name(self) -> str:
        """Detect current page from Streamlit navigation"""
        try:
            # Get current script path
            import inspect
            frame = inspect.currentframe()
            if frame and frame.f_back:
                script_path = frame.f_back.f_code.co_filename
                # Extract page name from path
                if 'predict_sepsis' in script_path:
                    return 'Predict Sepsis'
                elif 'predict_mortality' in script_path:
                    return 'Predict Mortality'
                elif 'dashboard' in script_path:
                    return 'Dashboard'
                elif 'model_performance' in script_path:
                    return 'Model Performance'
                elif 'settings' in script_path:
                    return 'Settings'
        except:
            pass

        # Fallback: check session state or URL params
        if 'current_page' in st.session_state:
            return st.session_state.current_page

        return 'Home'

    def get_page_context(self, page_name: str) -> dict:
        """Get context information for current page"""
        return PAGE_CONTEXTS.get(page_name, PAGE_CONTEXTS['Home'])

    def generate_contextual_greeting(self, page_name: str) -> str:
        """Generate greeting based on current page"""
        context = self.get_page_context(page_name)

        greeting = (
            f"**🏥 Xin chào! Tôi là MediAI Assistant.**\n\n"
            f"Bạn đang ở: **{context['title']}**\n"
            f"*{context['description']}*\n\n"
        )

        if context['help_topics']:
            greeting += "**❓ Tôi có thể giúp bạn:**\n"
            for topic in context['help_topics'][:4]:  # Show max 4
                greeting += f"- {topic}\n"
            greeting += "\n"

        greeting += (
            "**💡 Mẹo:** Bạn có thể hỏi bất cứ điều gì về trang này, "
            "các trường dữ liệu, hoặc cách sử dụng hệ thống.\n\n"
            "Bạn cần giúp gì?"
        )

        return greeting

    def generate_contextual_response(
        self,
        user_input: str,
        page_name: str,
        chat_history: list
    ) -> str:
        """Generate response based on current page context"""

        context = self.get_page_context(page_name)
        user_input_lower = user_input.lower()

        # Check for page-specific help
        if page_name == 'Predict Sepsis':
            return self._handle_sepsis_page_help(user_input_lower)
        elif page_name == 'Predict Mortality':
            return self._handle_mortality_page_help(user_input_lower)
        elif page_name == 'Dashboard':
            return self._handle_dashboard_help(user_input_lower)
        elif page_name == 'Model Performance':
            return self._handle_model_performance_help(user_input_lower)

        # Generic help
        return self._handle_generic_help(user_input, context)

    def _handle_sepsis_page_help(self, user_input: str) -> str:
        """Help for Sepsis prediction page"""

        if any(kw in user_input for kw in ['trường', 'field', 'nhập', 'input', 'cần gì']):
            return (
                "**📝 Hướng dẫn Nhập liệu - Dự đoán Sepsis**\n\n"
                "**Thông tin bắt buộc:**\n"
                "1. **Thông tin cơ bản:**\n"
                "   - Tuổi (Age): 18-100 tuổi\n"
                "   - Giới tính (Gender): Nam/Nữ\n\n"
                "2. **Sinh hiệu (Vital Signs):**\n"
                "   - ❤️ Nhịp tim (HR): 40-180 bpm\n"
                "   - 🌡️ Nhiệt độ (Temp): 35-41°C\n"
                "   - 💨 Nhịp thở (RR): 8-40 breaths/min\n"
                "   - 🩺 Huyết áp (BP): SBP 70-200, DBP 40-120 mmHg\n"
                "   - 📊 SpO2: 85-100%\n\n"
                "3. **Xét nghiệm quan trọng:**\n"
                "   - 🔬 WBC (Bạch cầu): 2-30 x10^9/L\n"
                "   - ⚡ Lactate: 0.5-10 mmol/L *(RED FLAG nếu >4)*\n"
                "   - 🫘 Creatinine: 0.5-5 mg/dL\n\n"
                "4. **Điểm lâm sàng:**\n"
                "   - 📋 SOFA Score: 0-24\n"
                "   - 🎯 qSOFA: 0-3\n\n"
                "**💡 Lưu ý:**\n"
                "- Các giá trị ngoài phạm vi sẽ có cảnh báo\n"
                "- Lactate >4 = RED FLAG nghiêm trọng\n"
                "- Mô hình dự đoán nguy cơ trong 6 giờ tới\n\n"
                "⚠️ *Kết quả chỉ tham khảo, không thay thế đánh giá lâm sàng*"
            )

        elif any(kw in user_input for kw in ['sofa', 'điểm', 'score']):
            return (
                "**📋 SOFA Score - Sequential Organ Failure Assessment**\n\n"
                "Đánh giá mức độ suy cơ quan ở bệnh nhân ICU.\n\n"
                "**6 hệ cơ quan (mỗi hệ 0-4 điểm):**\n"
                "1. **Hô hấp**: PaO2/FiO2\n"
                "   - 0: ≥400 | 1: <400 | 2: <300 | 3: <200 | 4: <100\n"
                "2. **Đông máu**: Platelets (x10³/μL)\n"
                "   - 0: ≥150 | 1: <150 | 2: <100 | 3: <50 | 4: <20\n"
                "3. **Gan**: Bilirubin (mg/dL)\n"
                "   - 0: <1.2 | 1: 1.2-1.9 | 2: 2-5.9 | 3: 6-11.9 | 4: ≥12\n"
                "4. **Tim mạch**: MAP hoặc vasopressor\n"
                "5. **Thần kinh**: Glasgow Coma Scale\n"
                "6. **Thận**: Creatinine hoặc urine output\n\n"
                "**Diễn giải:**\n"
                "- Tăng ≥2 điểm → Định nghĩa Sepsis\n"
                "- 0-6: Mức độ nhẹ\n"
                "- 7-12: Trung bình\n"
                "- 13-24: Nặng\n\n"
                "📖 *Tham khảo: Sepsis-3 Consensus Definitions (JAMA 2016)*"
            )

        elif any(kw in user_input for kw in ['ví dụ', 'example', 'mẫu', 'sample']):
            return (
                "**📊 Ví dụ Dữ liệu - Bệnh nhân Nguy cơ CAO**\n\n"
                "```\n"
                "Thông tin cơ bản:\n"
                "- Tuổi: 68\n"
                "- Giới tính: Nam\n\n"
                "Sinh hiệu:\n"
                "- Nhịp tim: 125 bpm ⚠️ (tachycardia)\n"
                "- Nhiệt độ: 38.8°C ⚠️ (fever)\n"
                "- Nhịp thở: 28 breaths/min ⚠️\n"
                "- SBP/DBP: 88/52 mmHg 🔴 (hypotension)\n"
                "- SpO2: 91% ⚠️\n\n"
                "Xét nghiệm:\n"
                "- WBC: 18.5 x10^9/L ⚠️ (leukocytosis)\n"
                "- Lactate: 5.2 mmol/L 🔴 CRITICAL\n"
                "- Creatinine: 2.1 mg/dL ⚠️ (AKI)\n\n"
                "Điểm lâm sàng:\n"
                "- SOFA Score: 8\n"
                "- qSOFA: 3\n"
                "```\n\n"
                "**Dự đoán:** Nguy cơ sepsis **HIGH (72%)**\n\n"
                "**RED FLAGS phát hiện:**\n"
                "- 🔴 Hạ huyết áp (SBP <90)\n"
                "- 🔴 Lactate cao (>4 mmol/L)\n"
                "- ⚠️ Suy thận cấp\n\n"
                "**Khuyến nghị:**\n"
                "- Sepsis Bundle ngay lập tức\n"
                "- Nuôi cấy máu + Kháng sinh trong 1h\n"
                "- Truyền dịch hồi sức 30 mL/kg"
            )

        elif any(kw in user_input for kw in ['kết quả', 'result', 'diễn giải', 'interpret']):
            return (
                "**📊 Cách Diễn giải Kết quả Dự đoán Sepsis**\n\n"
                "Sau khi nhập dữ liệu, mô hình sẽ trả về:\n\n"
                "**1. Mức độ Nguy cơ (Risk Level):**\n"
                "- 🟢 **LOW (<30%)**: Nguy cơ thấp, giám sát thường quy\n"
                "- 🟡 **MEDIUM (30-60%)**: Theo dõi sát, chuẩn bị can thiệp\n"
                "- 🟠 **HIGH (60-80%)**: Nguy cơ cao, xem xét Sepsis Bundle\n"
                "- 🔴 **CRITICAL (>80%)**: URGENT - Can thiệp ngay lập tức\n\n"
                "**2. Độ tin cậy (Confidence):**\n"
                "- Dựa trên ensemble của nhiều models\n"
                "- Độ tin cậy thấp (<70%) → Cần thêm dữ liệu lâm sàng\n\n"
                "**3. RED FLAGS:**\n"
                "- Các dấu hiệu nguy hiểm được highlight đỏ\n"
                "- VD: Lactate >4, MAP <65, SpO2 <90\n\n"
                "**4. SHAP Explanation:**\n"
                "- Biểu đồ các yếu tố ảnh hưởng kết quả\n"
                "- Màu đỏ = Tăng nguy cơ\n"
                "- Màu xanh = Giảm nguy cơ\n\n"
                "**5. Khuyến nghị Lâm sàng:**\n"
                "- Hướng dẫn can thiệp dựa trên guidelines\n"
                "- Surviving Sepsis Campaign 2021\n\n"
                "⚠️ **LƯU Ý:** Mọi kết quả cần bác sĩ xác nhận!"
            )

        # Default sepsis help
        return (
            "**ℹ️ Trợ giúp - Trang Dự đoán Sepsis**\n\n"
            "Bạn có thể hỏi:\n"
            "- 'Cần nhập những trường gì?'\n"
            "- 'SOFA score là gì?'\n"
            "- 'Cho tôi ví dụ dữ liệu mẫu'\n"
            "- 'Cách diễn giải kết quả?'\n"
            "- 'Phạm vi giá trị hợp lệ?'\n\n"
            "Hoặc nhập câu hỏi cụ thể của bạn!"
        )

    def _handle_mortality_page_help(self, user_input: str) -> str:
        """Help for Mortality prediction page"""

        if any(kw in user_input for kw in ['apache', 'điểm', 'score']):
            return (
                "**📋 APACHE-II Score**\n\n"
                "**Acute Physiology and Chronic Health Evaluation**\n"
                "Đánh giá mức độ nặng bệnh ICU và dự đoán tử vong.\n\n"
                "**3 thành phần chính:**\n"
                "1. **Acute Physiology Score (0-60 điểm)**\n"
                "   - 12 biến sinh lý: Nhiệt độ, MAP, HR, RR\n"
                "   - PaO2, pH, Na, K, Creatinine, Hct, WBC, GCS\n"
                "2. **Age Points (0-6 điểm)**\n"
                "   - <44: 0 | 45-54: 2 | 55-64: 3 | 65-74: 5 | ≥75: 6\n"
                "3. **Chronic Health Points (0-5 điểm)**\n"
                "   - Bệnh mạn tính nặng: Gan, Tim, Thận, COPD\n\n"
                "**Tổng điểm: 0-71**\n"
                "- 0-4: Tử vong <4%\n"
                "- 5-9: Tử vong 4-8%\n"
                "- 10-14: Tử vong 8-15%\n"
                "- 15-19: Tử vong 15-25%\n"
                "- 20-24: Tử vong 25-40%\n"
                "- 25-29: Tử vong 40-55%\n"
                "- 30-34: Tử vong 55-75%\n"
                "- ≥35: Tử vong >75%\n\n"
                "📖 *Knaus et al., Crit Care Med 1985*"
            )

        elif any(kw in user_input for kw in ['yếu tố', 'factor', 'ảnh hưởng', 'influence']):
            return (
                "**🎯 Các Yếu tố Nguy cơ Tử vong ICU**\n\n"
                "**Yếu tố Sinh lý (Physiology):**\n"
                "- 🔴 Huyết áp thấp (MAP <65 mmHg)\n"
                "- 🔴 Suy hô hấp (PaO2/FiO2 <200)\n"
                "- 🔴 Suy thận cấp (Creatinine tăng)\n"
                "- ⚠️ Rối loạn ý thức (GCS giảm)\n"
                "- ⚠️ Rối loạn đông máu (PLT <50K)\n\n"
                "**Yếu tố Nhân khẩu (Demographics):**\n"
                "- 📊 Tuổi cao (>65)\n"
                "- 📊 Giới tính (nam có thể cao hơn)\n\n"
                "**Bệnh nền (Comorbidities):**\n"
                "- ❤️ Suy tim mạn\n"
                "- 🫁 COPD nặng\n"
                "- 🫘 Suy thận mạn\n"
                "- 🩸 Ung thư giai đoạn cuối\n"
                "- 🔬 Suy giảm miễn dịch\n\n"
                "**Can thiệp Điều trị:**\n"
                "- 💉 Sử dụng vasopressor\n"
                "- 🫁 Thở máy xâm nhập\n"
                "- 🩸 Lọc máu liên tục\n\n"
                "**Mức độ Nghiêm trọng:**\n"
                "- 📋 SOFA score cao (>10)\n"
                "- 📋 APACHE-II cao (>25)\n"
                "- ⏱️ Thời gian nằm ICU kéo dài\n\n"
                "⚠️ *Mô hình MediAI tích hợp tất cả các yếu tố này*"
            )

        # Default mortality help
        return (
            "**ℹ️ Trợ giúp - Dự đoán Tử vong ICU**\n\n"
            "Trang này dự đoán tỷ lệ tử vong trong 24h dựa trên:\n"
            "- Sinh hiệu worst values trong 24h\n"
            "- Điểm APACHE-II và SOFA\n"
            "- Bệnh nền và can thiệp điều trị\n\n"
            "Bạn có thể hỏi:\n"
            "- 'APACHE-II score là gì?'\n"
            "- 'Các yếu tố nguy cơ tử vong?'\n"
            "- 'Cách tính điểm APACHE-II?'\n"
            "- 'Khi nào cần leo thang điều trị?'"
        )

    def _handle_dashboard_help(self, user_input: str) -> str:
        """Help for Dashboard page"""
        return (
            "**📊 Trợ giúp - Dashboard Giám sát**\n\n"
            "Dashboard hiển thị:\n"
            "- 📈 Xu hướng sinh hiệu theo thời gian\n"
            "- 🎯 Các chỉ số quan trọng (KPIs)\n"
            "- ⚠️ Cảnh báo bất thường\n"
            "- 📊 Phân bố nguy cơ bệnh nhân\n\n"
            "**Cách sử dụng:**\n"
            "- Chọn khoảng thời gian cần xem\n"
            "- Lọc theo bệnh nhân hoặc khoa\n"
            "- Xuất báo cáo PDF/Excel\n\n"
            "Cần giúp gì cụ thể về Dashboard?"
        )

    def _handle_model_performance_help(self, user_input: str) -> str:
        """Help for Model Performance page"""

        if any(kw in user_input for kw in ['auroc', 'auc', 'roc']):
            return (
                "**📊 AUROC - Area Under ROC Curve**\n\n"
                "**Định nghĩa:**\n"
                "Diện tích dưới đường cong ROC, đo khả năng phân biệt\n"
                "giữa positive và negative cases.\n\n"
                "**Thang điểm:**\n"
                "- 1.0 = Perfect prediction\n"
                "- 0.9-1.0: Excellent (xuất sắc)\n"
                "- 0.8-0.9: Very good (rất tốt) ← **MediAI Sepsis: 0.893**\n"
                "- 0.7-0.8: Good (tốt)\n"
                "- 0.6-0.7: Fair (khá) ← **MediAI Mortality: 0.65**\n"
                "- 0.5-0.6: Poor (kém)\n"
                "- 0.5 = Random guess (đoán ngẫu nhiên)\n\n"
                "**Ý nghĩa Lâm sàng:**\n"
                "- AUROC cao → Mô hình phân loại tốt\n"
                "- Nhưng cần xem thêm sensitivity/specificity\n"
                "- Và calibration (độ chính xác xác suất)\n\n"
                "📖 *ROC = Receiver Operating Characteristic*"
            )

        elif any(kw in user_input for kw in ['sensitivity', 'specificity', 'độ nhạy', 'độ đặc hiệu']):
            return (
                "**🎯 Sensitivity vs Specificity**\n\n"
                "**Sensitivity (Độ nhạy):**\n"
                "- Tỷ lệ phát hiện đúng trong số bệnh nhân THỰC SỰ có bệnh\n"
                "- = True Positives / (True Positives + False Negatives)\n"
                "- **MediAI Sepsis: 82.8%** → Bỏ sót 17.2% ca sepsis\n\n"
                "**Specificity (Độ đặc hiệu):**\n"
                "- Tỷ lệ loại trừ đúng trong số người KHÔNG có bệnh\n"
                "- = True Negatives / (True Negatives + False Positives)\n"
                "- **MediAI Sepsis: 80.6%** → 19.4% false alarms\n\n"
                "**Trade-off:**\n"
                "- Tăng sensitivity → Giảm specificity (nhiều false +)\n"
                "- Tăng specificity → Giảm sensitivity (nhiều false -)\n\n"
                "**Trong Y tế:**\n"
                "- Sepsis: Ưu tiên **sensitivity cao** (không bỏ sót)\n"
                "- Screening: Cân bằng cả hai\n"
                "- Confirm test: Ưu tiên **specificity cao**\n\n"
                "⚠️ *MediAI được thiết kế để không bỏ sót ca nghiêm trọng*"
            )

        elif any(kw in user_input for kw in ['shap', 'giải thích', 'explain']):
            return (
                "**🔍 SHAP - SHapley Additive exPlanations**\n\n"
                "**Mục đích:**\n"
                "Giải thích AI 'đưa ra quyết định' như thế nào.\n\n"
                "**Cách đọc SHAP Plot:**\n"
                "- Trục X: SHAP value (ảnh hưởng đến dự đoán)\n"
                "  - Dương (+) → Tăng nguy cơ\n"
                "  - Âm (-) → Giảm nguy cơ\n"
                "- Màu sắc: Giá trị thực của feature\n"
                "  - Đỏ = Cao\n"
                "  - Xanh = Thấp\n"
                "- Vị trí trên/dưới: Tầm quan trọng\n\n"
                "**Ví dụ:**\n"
                "```\n"
                "Lactate [màu đỏ, SHAP +0.8]\n"
                "→ Lactate CAO, ảnh hưởng TĂNG nguy cơ mạnh\n\n"
                "Age [màu xanh, SHAP -0.3]\n"
                "→ Tuổi THẤP, ảnh hưởng GIẢM nguy cơ\n"
                "```\n\n"
                "**Lợi ích:**\n"
                "- ✅ Minh bạch (explainable AI)\n"
                "- ✅ Tin cậy được bác sĩ\n"
                "- ✅ Phát hiện lỗi của mô hình\n\n"
                "📖 *SHAP dựa trên lý thuyết trò chơi (Game Theory)*"
            )

        # Default model performance help
        return (
            "**📊 Trợ giúp - Hiệu suất Mô hình**\n\n"
            "Trang này hiển thị:\n"
            "- ROC Curve và AUROC\n"
            "- Confusion Matrix\n"
            "- Calibration Plot\n"
            "- SHAP Explanations\n"
            "- Feature Importance\n\n"
            "Bạn có thể hỏi:\n"
            "- 'AUROC là gì?'\n"
            "- 'Sensitivity vs Specificity?'\n"
            "- 'Cách đọc SHAP plot?'\n"
            "- 'Mô hình có tốt không?'"
        )

    def _handle_generic_help(self, user_input: str, context: dict) -> str:
        """Generic help for unknown queries"""
        return (
            f"**ℹ️ Trợ giúp - {context['title']}**\n\n"
            f"*{context['description']}*\n\n"
            "**Các câu hỏi thường gặp:**\n"
        ) + "\n".join(f"- {topic}" for topic in context['help_topics'][:5]) + (
            "\n\nHoặc bạn có thể hỏi cụ thể hơn về:\n"
            "- Các chức năng trên trang này\n"
            "- Cách nhập dữ liệu\n"
            "- Cách diễn giải kết quả\n"
            "- Tiêu chuẩn lâm sàng"
        )

# ============================================================================
# FLOATING WIDGET UI
# ============================================================================

def render_floating_assistant(page_name: Optional[str] = None):
    """
    Render floating assistant widget

    Usage:
        Add to any page:
        ```python
        from components.floating_assistant import render_floating_assistant
        render_floating_assistant()
        ```
    """

    # Initialize session state
    if 'fa_open' not in st.session_state:
        st.session_state.fa_open = False
    if 'fa_messages' not in st.session_state:
        st.session_state.fa_messages = []
    if 'fa_assistant' not in st.session_state:
        st.session_state.fa_assistant = ContextAwareAssistant()
    if 'fa_session_id' not in st.session_state:
        st.session_state.fa_session_id = str(uuid.uuid4())

    # Detect current page
    if not page_name:
        page_name = st.session_state.fa_assistant.get_current_page_name()

    # Add initial greeting if first time
    if len(st.session_state.fa_messages) == 0:
        greeting = st.session_state.fa_assistant.generate_contextual_greeting(page_name)
        st.session_state.fa_messages.append({
            'role': 'assistant',
            'content': greeting,
            'timestamp': datetime.now().isoformat()
        })

    # Custom CSS for floating button and panel
    st.markdown("""
    <style>
    /* Floating button - Bottom right corner */
    .floating-help-button {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        border-radius: 50%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        cursor: pointer;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        border: 3px solid white;
    }

    .floating-help-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(30,64,175,0.4);
    }

    .floating-help-button span {
        font-size: 28px;
        color: white;
        font-weight: bold;
    }

    /* Chat panel */
    .floating-chat-panel {
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 400px;
        max-height: 600px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        z-index: 9998;
        display: flex;
        flex-direction: column;
        border: 2px solid #E5E7EB;
    }

    .chat-panel-header {
        background: linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 14px 14px 0 0;
        font-weight: 600;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .chat-panel-header .close-btn {
        cursor: pointer;
        font-size: 20px;
        padding: 0 5px;
    }

    .chat-panel-body {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        max-height: 450px;
        background: #F9FAFB;
    }

    .chat-message {
        margin-bottom: 12px;
        padding: 10px 14px;
        border-radius: 8px;
        font-size: 13px;
        line-height: 1.5;
    }

    .chat-message.user {
        background: #DBEAFE;
        margin-left: 20px;
        border: 1px solid #BFDBFE;
    }

    .chat-message.assistant {
        background: white;
        margin-right: 20px;
        border: 1px solid #E5E7EB;
    }

    .chat-panel-footer {
        padding: 12px;
        border-top: 1px solid #E5E7EB;
        background: white;
        border-radius: 0 0 14px 14px;
    }

    /* Notification badge */
    .help-notification {
        position: absolute;
        top: -5px;
        right: -5px;
        width: 20px;
        height: 20px;
        background: #DC2626;
        border-radius: 50%;
        border: 2px solid white;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    </style>
    """, unsafe_allow_html=True)

    # Toggle button logic
    col1, col2, col3 = st.columns([6, 1, 1])

    with col3:
        if st.button("❓" if not st.session_state.fa_open else "✕",
                     key="floating_help_toggle",
                     help="Trợ giúp MediAI",
                     use_container_width=True):
            st.session_state.fa_open = not st.session_state.fa_open
            st.rerun()

    # Render chat panel if open
    if st.session_state.fa_open:
        with st.container():
            st.markdown("---")
            st.markdown(f"### 🏥 MediAI Assistant - {page_name}")

            # Chat messages container
            chat_container = st.container()
            with chat_container:
                for msg in st.session_state.fa_messages:
                    if msg['role'] == 'user':
                        with st.chat_message("user", avatar="👤"):
                            st.markdown(msg['content'])
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(msg['content'])

            # Chat input
            user_input = st.chat_input("Nhập câu hỏi...", key="fa_chat_input")

            if user_input:
                # Add user message
                st.session_state.fa_messages.append({
                    'role': 'user',
                    'content': user_input,
                    'timestamp': datetime.now().isoformat()
                })

                # Generate response
                assistant = st.session_state.fa_assistant
                response = assistant.generate_contextual_response(
                    user_input,
                    page_name,
                    st.session_state.fa_messages
                )

                # Add assistant response
                st.session_state.fa_messages.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })

                # Log interaction
                if assistant.audit_logger:
                    try:
                        assistant.audit_logger.log_event(
                            event_type=EventType.API_CALL if EventType else 'API_CALL',
                            user_id=st.session_state.get('user_id', 'demo'),
                            session_id=st.session_state.fa_session_id,
                            details={
                                'action': 'floating_assistant_interaction',
                                'page': page_name,
                                'user_input_length': len(user_input),
                                'response_length': len(response)
                            },
                            outcome='SUCCESS'
                        )
                    except Exception:
                        pass  # Silently fail audit logging

                st.rerun()

            # Clear chat button
            if st.button("🔄 Reset Chat", key="fa_reset"):
                st.session_state.fa_messages = []
                st.session_state.fa_session_id = str(uuid.uuid4())
                st.rerun()


# ============================================================================
# LIGHTWEIGHT VERSION (For embedding in all pages)
# ============================================================================

def add_floating_help_button():
    """
    Minimal version - just adds the floating button with JavaScript
    Use this if you want minimal performance impact
    """
    st.markdown("""
    <div class="floating-help-button" onclick="alert('Trợ giúp MediAI - Chức năng đang phát triển')">
        <span>?</span>
    </div>
    """, unsafe_allow_html=True)


# Export
__all__ = ['render_floating_assistant', 'add_floating_help_button', 'ContextAwareAssistant']
