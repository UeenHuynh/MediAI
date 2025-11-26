# 🏥 Floating Assistant Integration Guide

## Hướng dẫn Tích hợp Chatbot Nổi

Tài liệu này hướng dẫn cách tích hợp **Floating Assistant** (chatbot góc phải màn hình) vào các trang Streamlit của MediAI.

---

## 📋 Tổng quan

**Floating Assistant** là một chatbot chuyên nghiệp, context-aware (hiểu ngữ cảnh trang hiện tại) xuất hiện dưới dạng:
- **Nút "❓"** ở góc phải trên màn hình
- Có thể toggle on/off
- Cung cấp trợ giúp dựa trên trang người dùng đang ở
- Tuân thủ HIPAA/GDPR với audit logging

---

## 🚀 Cách Tích hợp

### Bước 1: Import Component

Thêm import vào đầu file page:

```python
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.floating_assistant import render_floating_assistant
```

### Bước 2: Render Widget

Thêm vào **cuối function** của page (trước return hoặc cuối cùng):

```python
def show_your_page():
    """Your page function"""

    # ... your page content here ...

    # Render floating assistant (ALWAYS at the end)
    render_floating_assistant(page_name="Your Page Name")
```

---

## 📖 Ví dụ Cụ thể

### Ví dụ 1: Predict Sepsis Page

```python
"""
Sepsis Prediction Page
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.floating_assistant import render_floating_assistant

def show_sepsis_prediction():
    """Sepsis prediction page"""

    st.title("🔬 Sepsis Risk Prediction")

    # Your form and content here
    with st.form("sepsis_form"):
        # ... form fields ...
        submitted = st.form_submit_button("Predict")

        if submitted:
            # Handle prediction
            pass

    # Render floating assistant at the end
    render_floating_assistant(page_name="Predict Sepsis")
```

### Ví dụ 2: Dashboard Page

```python
"""
Dashboard Page
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.floating_assistant import render_floating_assistant

def show_dashboard():
    """Dashboard page"""

    st.title("📊 Clinical Dashboard")

    # Display charts and metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Patients", 150)
    # ... more content ...

    # Render floating assistant
    render_floating_assistant(page_name="Dashboard")
```

### Ví dụ 3: Settings Page

```python
"""
Settings Page
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from components.floating_assistant import render_floating_assistant

def show_settings():
    """Settings page"""

    st.title("⚙️ Settings")

    # Settings content
    st.checkbox("Enable notifications")
    st.button("Save Settings")

    # Render floating assistant
    render_floating_assistant(page_name="Settings")
```

---

## 🎨 Supported Page Names

Các tên trang được hỗ trợ với context-aware help:

| Page Name           | Description                         |
|---------------------|-------------------------------------|
| `"Home"`            | Trang chủ MediAI                   |
| `"Predict Sepsis"`  | Form dự đoán sepsis                |
| `"Predict Mortality"` | Form dự đoán tử vong              |
| `"Dashboard"`       | Dashboard giám sát                 |
| `"Model Performance"` | Metrics và đánh giá mô hình      |
| `"Settings"`        | Cài đặt hệ thống                   |

**Lưu ý:** Nếu dùng tên trang khác, assistant sẽ fallback về generic help.

---

## 💡 Tính năng Context-Aware

Assistant tự động thay đổi nội dung trợ giúp dựa trên trang hiện tại:

### Predict Sepsis Page
```
User: "Cần nhập những trường gì?"
Bot:  "📝 Hướng dẫn Nhập liệu - Dự đoán Sepsis
       1. Thông tin cơ bản: Tuổi, giới tính
       2. Sinh hiệu: HR, BP, Temp, RR, SpO2
       3. Xét nghiệm: WBC, Lactate, Creatinine
       ..."
```

### Dashboard Page
```
User: "Giải thích các biểu đồ"
Bot:  "📊 Dashboard hiển thị:
       - Xu hướng sinh hiệu theo thời gian
       - KPIs quan trọng
       - Cảnh báo bất thường
       ..."
```

### Model Performance Page
```
User: "AUROC là gì?"
Bot:  "📊 AUROC - Area Under ROC Curve
       Đo khả năng phân biệt positive/negative cases
       MediAI Sepsis: 0.893 (Very good)
       ..."
```

---

## 🔧 Customization

### Thay đổi Vị trí Button

Mặc định button ở góc phải dưới. Để thay đổi, sửa CSS trong `floating_assistant.py`:

```python
# Trong render_floating_assistant()
st.markdown("""
<style>
.floating-help-button {
    position: fixed;
    bottom: 30px;    /* Khoảng cách từ dưới */
    right: 30px;     /* Khoảng cách từ phải */
    /* Thay đổi giá trị này để di chuyển */
}
</style>
""", unsafe_allow_html=True)
```

### Thêm Page Context Mới

Để thêm context cho page mới, edit `PAGE_CONTEXTS` trong `floating_assistant.py`:

```python
PAGE_CONTEXTS = {
    # ... existing pages ...

    'Your New Page': {
        'title': 'Tiêu đề Trang Mới',
        'description': 'Mô tả ngắn gọn',
        'help_topics': [
            'Câu hỏi thường gặp 1',
            'Câu hỏi thường gặp 2',
            'Câu hỏi thường gặp 3'
        ],
        'quick_actions': [
            'Action 1',
            'Action 2'
        ]
    }
}
```

### Thêm Specialized Handler

Để thêm logic xử lý đặc biệt cho page mới:

```python
# Trong ContextAwareAssistant class

def generate_contextual_response(self, user_input, page_name, chat_history):
    # ... existing code ...

    if page_name == 'Your New Page':
        return self._handle_new_page_help(user_input)

    # ... rest of code ...

def _handle_new_page_help(self, user_input: str) -> str:
    """Help for new page"""

    if 'keyword' in user_input.lower():
        return "Trả lời cụ thể cho keyword..."

    return "Generic help cho page này..."
```

---

## 🧪 Testing

### Test Cơ bản

1. **Hiển thị Button:**
   - Mở trang đã tích hợp
   - Kiểm tra button "❓" xuất hiện góc phải

2. **Toggle Panel:**
   - Click button "❓"
   - Chat panel hiển thị
   - Click lại để đóng

3. **Context Awareness:**
   - Mở "Predict Sepsis"
   - Hỏi: "Cần nhập gì?"
   - Kiểm tra response có thông tin về sepsis fields

4. **Multi-Page:**
   - Navigate giữa các trang
   - Kiểm tra greeting thay đổi theo page
   - Chat history riêng biệt cho mỗi session

### Test Advanced

```python
# Test script (optional)
def test_floating_assistant():
    from components.floating_assistant import ContextAwareAssistant

    assistant = ContextAwareAssistant()

    # Test page detection
    page = assistant.get_current_page_name()
    assert page in ['Home', 'Predict Sepsis', 'Dashboard']

    # Test context retrieval
    context = assistant.get_page_context('Predict Sepsis')
    assert 'help_topics' in context
    assert len(context['help_topics']) > 0

    # Test response generation
    response = assistant.generate_contextual_response(
        "What fields are required?",
        "Predict Sepsis",
        []
    )
    assert 'trường' in response.lower() or 'field' in response.lower()

    print("✅ All tests passed")
```

---

## 📊 Performance Considerations

### Lazy Loading

Component chỉ render khi người dùng mở chat panel:

```python
if st.session_state.fa_open:
    # Only render chat UI when open
    render_chat_panel()
```

### Session State Management

Mỗi page có session state riêng:
- `fa_open`: Panel open/closed
- `fa_messages`: Chat history
- `fa_session_id`: Unique session ID

### Audit Logging

Mọi tương tác được log tự động:

```python
audit_logger.log_event(
    event_type='CHATBOT_INTERACTION',
    page='Predict Sepsis',
    user_input_length=50,
    outcome='SUCCESS'
)
```

---

## 🔒 Security & Compliance

### HIPAA Compliance
- ✅ Không lưu trữ PHI trong chat history
- ✅ All interactions audit logged
- ✅ Session timeout sau 15 phút
- ✅ Encrypted audit logs

### GDPR Compliance
- ✅ User có thể xóa chat history (Reset button)
- ✅ Transparent về cách data được sử dụng
- ✅ No data sharing với third parties

### Safety Guardrails
- ⚠️ Không bao giờ tư vấn điều trị
- ⚠️ Không bao giờ chẩn đoán
- ⚠️ Luôn hiển thị disclaimer
- ⚠️ Validate tất cả inputs

---

## 🐛 Troubleshooting

### Error: "Module 'components' not found"

**Giải pháp:**
```python
# Đảm bảo path được add đúng
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Error: "AuditLogger not found"

**Giải pháp:**
```python
# Trong floating_assistant.py, có fallback:
try:
    from utils.audit_logger import AuditLogger
except ImportError:
    AuditLogger = None  # Graceful degradation
```

### Button không hiển thị

**Kiểm tra:**
1. `render_floating_assistant()` được gọi cuối function?
2. Session state được initialize?
3. CSS được inject?

**Debug:**
```python
# Thêm vào cuối page function
st.write("FA Open:", st.session_state.get('fa_open', 'Not set'))
st.write("FA Messages:", len(st.session_state.get('fa_messages', [])))
```

### Chat history không persist

**Giải pháp:** Session state tự động persist trong Streamlit session. Nếu reset page, history sẽ mất. Để giữ lại:

```python
# Add to session state init
if 'fa_persistent_history' not in st.session_state:
    st.session_state.fa_persistent_history = []

# Save on each interaction
st.session_state.fa_persistent_history.append(message)
```

---

## 📚 Best Practices

### 1. Luôn đặt cuối function

```python
def show_page():
    # All page content here
    st.title("...")
    # forms, charts, etc.

    # LAST LINE - Render assistant
    render_floating_assistant(page_name="Page Name")
```

### 2. Dùng đúng page name

```python
# ✅ ĐÚNG
render_floating_assistant(page_name="Predict Sepsis")

# ❌ SAI
render_floating_assistant(page_name="sepsis prediction")  # lowercase
```

### 3. Test context awareness

Sau khi tích hợp, test các câu hỏi:
- "Cần nhập gì?"
- "Giải thích kết quả"
- "SOFA score là gì?"

### 4. Update page contexts khi thêm features

Nếu thêm field mới vào form, update `PAGE_CONTEXTS`:

```python
'Predict Sepsis': {
    'help_topics': [
        'Các trường dữ liệu cần nhập',
        'NEW: Giải thích trường X mới',  # Add this
        # ...
    ]
}
```

### 5. Maintain professional tone

All responses phải:
- Dùng thuật ngữ y khoa chính xác
- Không dùng emoji quá mức
- Luôn có disclaimer khi cần
- Trích dẫn nguồn khoa học

---

## 🎯 Roadmap

### Phase 2 (Future)
- [ ] Voice input/output
- [ ] Multi-language (EN/VI toggle)
- [ ] Integration với model predictions
- [ ] SHAP explanations trong chat
- [ ] PDF export của chat history

### Phase 3 (Advanced)
- [ ] LLM integration (GPT-4/Claude)
- [ ] RAG với medical guidelines
- [ ] Proactive suggestions
- [ ] Learning from interactions

---

## 📞 Support

**Issues:** Report bugs tại GitHub Issues
**Docs:** Đầy đủ tại `/docs/CHATBOT_DESIGN.md`
**Contact:** mediai-support@example.com

---

**Version:** 1.0
**Last Updated:** 2025-11-26
**Author:** MediAI Engineering Team
