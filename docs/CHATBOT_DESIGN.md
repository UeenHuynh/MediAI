# 🏥 MediAI Professional Medical Chatbot Design

## Thiết kế Chatbot Y tế Nghiêm ngặt & Chuyên nghiệp

### 1. NGUYÊN TẮC CỐT LÕI

#### 1.1 Tính Chuyên nghiệp (Professionalism)
- **Ngôn ngữ y khoa chính xác**: Sử dụng thuật ngữ chuẩn ICD-10, SNOMED CT
- **Giọng điệu trang trọng**: Không dùng emoji, không thân mật quá mức
- **Trình bày có cấu trúc**: Thông tin được tổ chức rõ ràng theo mục
- **Trích dẫn nguồn**: Mọi khuyến nghị đều có tham chiếu khoa học

#### 1.2 Tính Nghiêm ngặt (Rigor)
- **Xác thực đầu vào**: Kiểm tra tất cả giá trị sinh hiệu trong phạm vi lâm sàng
- **Quản lý không chắc chắn**: Luôn báo cáo độ tin cậy và giới hạn của mô hình
- **Kiểm soát phạm vi**: Từ chối trả lời câu hỏi ngoài chuyên môn
- **Ghi nhật ký đầy đủ**: Audit log cho mọi tương tác

#### 1.3 An toàn Bệnh nhân (Patient Safety)
- **Disclaimer bắt buộc**: "Không thay thế đánh giá lâm sàng"
- **Cảnh báo nghiêm trọng**: Highlight các dấu hiệu nguy hiểm (RED FLAGS)
- **Hướng dẫn leo thang**: Khi nào cần gọi bác sĩ/đội cấp cứu
- **Không tư vấn điều trị**: Chỉ cung cấp thông tin, không ra quyết định

---

### 2. KIẾN TRÚC CHATBOT

```
┌─────────────────────────────────────────────────────────┐
│           STREAMLIT CHATBOT INTERFACE                   │
│  - Chat history display (st.chat_message)              │
│  - User input validation                                │
│  - Session state management                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│         CONVERSATION ORCHESTRATOR                       │
│  - Intent classification                                │
│  - Context tracking                                     │
│  - Multi-turn dialogue management                       │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ SAFETY LAYER │ │ MODEL SERVICE│ │ KNOWLEDGE    │
│ - Validation │ │ - Sepsis     │ │ BASE         │
│ - Guardrails │ │ - Mortality  │ │ - FAQs       │
│ - Audit logs │ │ - SHAP       │ │ - Protocols  │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

### 3. CHỨC NĂNG CHATBOT

#### 3.1 Intent Classification (Phân loại Ý định)

**Supported Intents:**
1. **RISK_ASSESSMENT** - "Đánh giá nguy cơ nhiễm trùng huyết cho bệnh nhân X"
2. **EXPLAIN_PREDICTION** - "Tại sao mô hình dự đoán nguy cơ cao?"
3. **CLINICAL_GUIDANCE** - "Tiêu chuẩn qSOFA là gì?"
4. **DATA_INQUIRY** - "Hiển thị xu hướng sinh hiệu 24h"
5. **SYSTEM_INFO** - "Mô hình được huấn luyện như thế nào?"

**Out-of-scope (Từ chối):**
- Câu hỏi chẩn đoán cụ thể ("Bệnh nhân này bị gì?")
- Tư vấn điều trị ("Tôi nên dùng thuốc gì?")
- Câu hỏi không y tế ("Thời tiết hôm nay?")

#### 3.2 Dialogue Flow (Luồng Hội thoại)

**Example: Sepsis Risk Assessment**

```
User: Tôi cần đánh giá nguy cơ sepsis cho bệnh nhân ICU

Bot:  ✓ Hiểu rồi. Để đánh giá nguy cơ nhiễm trùng huyết, tôi cần
      thông tin về sinh hiệu và xét nghiệm của bệnh nhân.

      Vui lòng cung cấp:
      [Hiển thị form có cấu trúc với 42 trường]

      ⚠️  LƯU Ý: Kết quả chỉ mang tính tham khảo, không thay thế
          đánh giá lâm sàng của bác sĩ.

User: [Nhập dữ liệu]

Bot:  ═══════════════════════════════════════
      📊 KẾT QUẢ ĐÁNH GIÁ NGUY CƠ SEPSIS
      ═══════════════════════════════════════

      Mức độ nguy cơ:  🔴 HIGH (72.5%)
      Độ tin cậy:      85.3%
      Thời gian dự báo: 6 giờ tới

      ⚠️  RED FLAGS PHÁT HIỆN:
      • Lactate > 4 mmol/L (giá trị: 5.2)
      • Tăng tần số thở (32 lần/phút)
      • Hạ huyết áp (MAP: 58 mmHg)

      📋 KHUYẾN NGHỊ:
      1. Xem xét Sepsis Bundle ngay lập tức
      2. Nuôi cấy máu trước khi kháng sinh
      3. Truyền dịch hồi sức (30 mL/kg trong 3h)
      4. Khởi động kháng sinh phổ rộng trong 1h

      📖 Tham khảo: Surviving Sepsis Campaign 2021

      🔍 CÁC YẾU TỐ ẢNH HƯỞNG:
      [SHAP explanation chart]

      ═══════════════════════════════════════
      ⚠️  DISCLAIMER: Đây là công cụ hỗ trợ quyết định.
          Bác sĩ lâm sàng cần xác nhận và ra quyết định
          cuối cùng về chẩn đoán và điều trị.
```

---

### 4. TÍNH NĂNG AN TOÀN

#### 4.1 Input Validation (Xác thực Đầu vào)

```python
CLINICAL_RANGES = {
    'heart_rate': (0, 300, 'bpm'),
    'temperature': (32.0, 42.0, '°C'),
    'respiratory_rate': (0, 60, 'breaths/min'),
    'sbp': (40, 250, 'mmHg'),
    'dbp': (20, 150, 'mmHg'),
    'spo2': (50, 100, '%'),
    'lactate': (0.5, 20.0, 'mmol/L'),  # Extended range with warnings
    'wbc': (0.1, 100.0, '10^9/L'),
    'creatinine': (0.1, 15.0, 'mg/dL')
}

def validate_vital_sign(name, value):
    min_val, max_val, unit = CLINICAL_RANGES[name]

    if value < min_val or value > max_val:
        return {
            'valid': False,
            'error': f"⚠️ {name} ngoài phạm vi lâm sàng ({min_val}-{max_val} {unit}). "
                     f"Giá trị: {value} {unit}. Vui lòng kiểm tra lại."
        }

    # Critical warnings
    if name == 'lactate' and value > 10:
        return {
            'valid': True,
            'warning': f"🔴 CRITICAL: Lactate rất cao ({value} mmol/L). "
                       f"Xem xét ngay lactic acidosis."
        }

    return {'valid': True}
```

#### 4.2 Guardrails (Hàng rào Bảo vệ)

**Prohibited Actions:**
- ❌ Không bao giờ đưa ra chẩn đoán xác định
- ❌ Không khuyên dùng thuốc cụ thể/liều lượng
- ❌ Không thay thế quyết định của bác sĩ
- ❌ Không lưu trữ PHI nếu chưa mã hóa

**Mandatory Actions:**
- ✅ Luôn hiển thị disclaimer trước kết quả
- ✅ Báo cáo độ tin cậy và uncertainty
- ✅ Highlight các RED FLAGS
- ✅ Log tất cả tương tác vào audit trail

#### 4.3 Audit Logging

```python
# Mọi hội thoại đều được ghi nhật ký
audit_logger.log_event(
    event_type='CHATBOT_INTERACTION',
    user_id=st.session_state.user_id,
    session_id=st.session_state.session_id,
    details={
        'intent': 'RISK_ASSESSMENT',
        'model_used': 'sepsis_lightgbm_v1',
        'prediction_risk': 0.725,
        'features_count': 42,
        'red_flags': ['high_lactate', 'hypotension'],
        'timestamp': datetime.utcnow().isoformat()
    },
    outcome='SUCCESS'
)
```

---

### 5. THIẾT KẾ UI/UX

#### 5.1 Chat Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  🏥 MediAI Clinical Assistant          [User: Dr. Nguyen]│
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ⚠️  PROFESSIONAL USE ONLY - NOT FOR CLINICAL DECISIONS  │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🤖 Assistant                                     │   │
│  │ Xin chào, tôi là trợ lý AI MediAI. Tôi có thể   │   │
│  │ hỗ trợ bạn:                                      │   │
│  │                                                   │   │
│  │ • Đánh giá nguy cơ sepsis và tử vong            │   │
│  │ • Giải thích kết quả dự đoán                     │   │
│  │ • Tra cứu thông tin lâm sàng                    │   │
│  │                                                   │   │
│  │ Bạn cần hỗ trợ gì?                              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 👨‍⚕️ You                                          │   │
│  │ Đánh giá nguy cơ sepsis cho BN #12345           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 🤖 Assistant                                     │   │
│  │ ═══════════════════════════════════════════════  │   │
│  │ 📊 SEPSIS RISK ASSESSMENT                       │   │
│  │ ═══════════════════════════════════════════════  │   │
│  │                                                   │   │
│  │ Risk Level: 🔴 HIGH (72.5%)                     │   │
│  │ [Progress bar visualization]                     │   │
│  │                                                   │   │
│  │ ⚠️  RED FLAGS:                                   │   │
│  │ • Lactate > 4 (value: 5.2 mmol/L)              │   │
│  │ • Hypotension (MAP: 58 mmHg)                    │   │
│  │                                                   │   │
│  │ [See full report] [SHAP explanation]            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
├─────────────────────────────────────────────────────────┤
│  💬 Type your message...                   [Send] [🎤] │
└─────────────────────────────────────────────────────────┘
```

#### 5.2 Professional Styling

**Color Scheme (Medical Professional):**
- Primary: `#1E40AF` (Deep Blue - Trust, Professionalism)
- Danger: `#DC2626` (Red - Alerts, Critical)
- Warning: `#F59E0B` (Amber - Caution)
- Success: `#059669` (Green - Normal)
- Background: `#F9FAFB` (Light Gray - Clinical Clean)
- Text: `#1F2937` (Dark Gray - High Contrast)

**Typography:**
- Headers: `Roboto Slab` (Professional, Authoritative)
- Body: `Inter` (Clean, Readable)
- Monospace: `JetBrains Mono` (For clinical values)

**Icons:**
- 🏥 Medical
- ⚠️ Warning
- 🔴 Critical
- 📊 Data/Metrics
- 📋 Guidelines
- 🔍 Analysis

---

### 6. TÍCH HỢP MÔ HÌNH

#### 6.1 Model Integration Flow

```python
class ChatbotOrchestrator:
    def __init__(self):
        self.model_service = ModelService()
        self.audit_logger = AuditLogger()

    def process_message(self, user_input: str, context: dict):
        # 1. Classify intent
        intent = self.classify_intent(user_input)

        # 2. Apply safety checks
        if not self.safety_check(intent, context):
            return self.refuse_response(intent)

        # 3. Route to appropriate handler
        if intent == 'RISK_ASSESSMENT':
            return self.handle_risk_assessment(user_input, context)
        elif intent == 'EXPLAIN_PREDICTION':
            return self.explain_model_output(context)
        # ... other intents

        # 4. Log interaction
        self.audit_logger.log_event('CHATBOT_INTERACTION', ...)
```

#### 6.2 Sepsis/Mortality Model Calls

```python
def handle_risk_assessment(self, user_input, context):
    # Extract clinical data from conversation
    clinical_data = self.extract_structured_data(user_input, context)

    # Validate all inputs
    validation = self.validate_clinical_data(clinical_data)
    if not validation.is_valid:
        return f"⚠️ Dữ liệu không hợp lệ: {validation.errors}"

    # Call model service
    sepsis_result = self.model_service.predict_sepsis(clinical_data)

    # Format professional response
    response = self.format_clinical_report(
        result=sepsis_result,
        include_disclaimer=True,
        include_shap=True,
        include_recommendations=True
    )

    return response
```

---

### 7. COMPLIANCE & REGULATIONS

#### 7.1 HIPAA Compliance
- ✅ Mã hóa tất cả PHI (AES-256)
- ✅ Audit logs cho mọi truy cập dữ liệu
- ✅ Minimum necessary principle (chỉ yêu cầu dữ liệu cần thiết)
- ✅ Session timeout (15 phút không hoạt động)

#### 7.2 GDPR Compliance
- ✅ Explicit consent trước khi xử lý dữ liệu
- ✅ Right to explanation (giải thích quyết định của AI)
- ✅ Data minimization (không lưu dữ liệu không cần thiết)
- ✅ Right to erasure (xóa dữ liệu theo yêu cầu)

#### 7.3 Medical Device Regulations
**⚠️ DISCLAIMER:** MediAI là công cụ nghiên cứu/giáo dục, **KHÔNG phải thiết bị y tế**
- Chưa được FDA/CE/TGA phê duyệt
- Không sử dụng cho quyết định lâm sàng thực tế
- Mọi dự đoán phải được bác sĩ xác nhận

---

### 8. TESTING & VALIDATION

#### 8.1 Safety Testing Scenarios

```python
# Test cases bắt buộc
test_cases = [
    # Từ chối câu hỏi ngoài phạm vi
    "What's the weather today?" → "⚠️ Xin lỗi, tôi chỉ hỗ trợ..."

    # Từ chối tư vấn điều trị
    "Should I give antibiotic X?" → "⚠️ Tôi không thể khuyên thuốc..."

    # Xử lý giá trị ngoại vi
    "Lactate: 50 mmol/L" → "⚠️ Giá trị ngoài phạm vi lâm sàng..."

    # Highlight RED FLAGS
    "MAP: 50, Lactate: 6" → "🔴 CRITICAL: ..."

    # Luôn hiển thị disclaimer
    ANY prediction → Must include "⚠️ DISCLAIMER: ..."
]
```

#### 8.2 Clinical Validation
- ✅ Retrospective validation với MIMIC-IV test set
- ✅ Expert review bởi 3+ intensivists
- ✅ Sensitivity analysis cho edge cases
- ✅ A/B testing với clinicians

---

### 9. IMPLEMENTATION PHASES

**Phase 1: Core Chatbot (Week 1-2)**
- [ ] Streamlit chat interface
- [ ] Session state management
- [ ] Basic intent classification
- [ ] Safety guardrails

**Phase 2: Model Integration (Week 3-4)**
- [ ] Connect to sepsis/mortality models
- [ ] SHAP explanation in chat
- [ ] Structured data extraction
- [ ] Clinical report formatting

**Phase 3: Professional Features (Week 5-6)**
- [ ] Audit logging
- [ ] Compliance checks
- [ ] Multi-language support (EN/VI)
- [ ] Advanced visualization

**Phase 4: Testing & Deployment (Week 7-8)**
- [ ] Safety testing
- [ ] Clinical validation
- [ ] Performance optimization
- [ ] Documentation

---

### 10. SUCCESS METRICS

**Technical Metrics:**
- Intent classification accuracy > 95%
- Response time < 2 seconds
- Zero false negatives for RED FLAGS
- 100% audit log coverage

**Clinical Metrics:**
- Clinician satisfaction > 4.5/5
- Time saved per assessment > 30%
- Error reduction vs manual entry > 80%
- Zero safety incidents

**Compliance Metrics:**
- 100% HIPAA audit compliance
- Zero data breaches
- All disclaimers displayed correctly
- Session management 100% compliant

---

## TÓM TẮT

MediAI Professional Chatbot là một **trợ lý AI y tế nghiêm ngặt** với:

✅ **Chuyên nghiệp**: Ngôn ngữ y khoa chính xác, giọng điệu trang trọng
✅ **An toàn**: Guardrails, validation, RED FLAGS, disclaimers bắt buộc
✅ **Tuân thủ**: HIPAA/GDPR compliant với audit logging đầy đủ
✅ **Minh bạch**: SHAP explanations, uncertainty reporting
✅ **Tích hợp**: Kết nối với sepsis/mortality models hiện có

**Không phải**: Chatbot thân thiện, tư vấn điều trị, thay thế bác sĩ
**Mục đích**: Hỗ trợ quyết định lâm sàng, giáo dục, nghiên cứu

---

**Version:** 1.0
**Date:** 2025-11-26
**Author:** MediAI Engineering Team
**Review:** Required by Clinical Advisory Board before deployment
