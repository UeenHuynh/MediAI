"""
Prompt Enhancement Engine
Automatically enhances short medical queries into detailed, structured prompts
"""

import re
from typing import Dict, List, Optional, Tuple


class PromptEnhancer:
    """Enhances user prompts with medical context and structure"""

    # Medical keywords and their enhancement templates
    ENHANCEMENT_PATTERNS = {
        # Sepsis & Infection
        r"(sepsis|nhiễm khuẩn huyết|septic)": {
            "category": "sepsis",
            "template": """Đánh giá bệnh nhân nghi ngờ nhiễm khuẩn huyết:

Vui lòng phân tích các khía cạnh sau:
1. Tính điểm qSOFA và giải thích kết quả
2. Đánh giá tiêu chí SIRS
3. Xác suất nhiễm khuẩn huyết và mức độ nghiêm trọng
4. Các bước xử trí ban đầu cần thiết
5. Xét nghiệm cấp cứu cần chỉ định
6. Phác đồ điều trị ban đầu theo hướng dẫn Surviving Sepsis Campaign

Truy vấn gốc: {original_query}""",
        },
        r"(kháng sinh|antibiotic)": {
            "category": "antibiotics",
            "template": """Tư vấn lựa chọn kháng sinh:

Vui lòng phân tích:
1. Kháng sinh kinh nghiệm phù hợp nhất cho tình huống này
2. Liều lượng và đường dùng
3. Thời gian điều trị khuyến cáo
4. Các yếu tố cần theo dõi trong quá trình điều trị
5. Thời điểm cân nhắc giảm bậc kháng sinh

Truy vấn gốc: {original_query}""",
        },
        r"(xét nghiệm|lab|test)": {
            "category": "labs",
            "template": """Phân tích kết quả xét nghiệm:

Vui lòng đánh giá:
1. Các giá trị bất thường và mức độ nghiêm trọng
2. Nguyên nhân có thể gây ra các bất thường
3. Ý nghĩa lâm sàng
4. Can thiệp cấp cứu nếu cần thiết
5. Xét nghiệm bổ sung khuyến cáo
6. Thời điểm kiểm tra lại

Truy vấn gốc: {original_query}""",
        },
        r"(gas máu|blood gas|abg|vbg)": {
            "category": "blood_gas",
            "template": """Phân tích khí máu động mạch:

Vui lòng đánh giá:
1. Rối loạn t산-base chính
2. Tính toán A-a gradient và giải thích
3. Tính P/F ratio
4. Đánh giá mức độ bù trừ
5. Nguyên nhân cơ bản
6. Điều chỉnh thở máy nếu cần thiết
7. Xử trí điều chỉnh rối loạn

Truy vấn gốc: {original_query}""",
        },
        r"(tử vong|mortality|tiên lượng|prognosis)": {
            "category": "mortality",
            "template": """Đánh giá nguy cơ tử vong và tiên lượng:

Vui lòng phân tích:
1. Tính điểm nguy cơ tử vong (SOFA, APACHE II)
2. Các yếu tố nguy cơ chính
3. Can thiệp có thể giảm nguy cơ tử vong
4. Thời gian nằm ICU dự kiến
5. Thông tin tiên lượng cho gia đình
6. Cân nhắc mục tiêu chăm sóc

Truy vấn gốc: {original_query}""",
        },
        r"(sốc|shock)": {
            "category": "shock",
            "template": """Phân loại và xử trí tình trạng sốc:

Vui lòng đánh giá:
1. Phân loại tình trạng sốc (phân bố/tim/giảm thể tích/tắc nghẽn)
2. Nguyên nhân cơ bản
3. Ưu tiên hồi sức ban đầu
4. Theo dõi huyết động cần thiết
5. Điều trị cụ thể theo loại sốc
6. Tiên lượng

Truy vấn gốc: {original_query}""",
        },
        r"(vasopressor|vận mạch|norepinephrine|dopamine)": {
            "category": "vasopressor",
            "template": """Lựa chọn và điều chỉnh thuốc vận mạch:

Vui lòng phân tích:
1. Đặc điểm huyết động (phân bố/tim/giảm thể tích)
2. Thuốc vận mạch/tăng co bóp phù hợp nhất
3. Liều khởi đầu khuyến cáo
4. Chiến lược chuẩn độ
5. Theo dõi cần thiết
6. Biến chứng có thể gặp
7. Thời điểm cai thuốc

Truy vấn gốc: {original_query}""",
        },
        r"(đặt nội khí quản|intubation|thở máy|ventilator)": {
            "category": "intubation",
            "template": """Chuẩn bị đặt nội khí quản và thở máy:

Vui lòng đánh giá:
1. Dự đoán đường thở khó
2. Thuốc gây mê phù hợp
3. Lựa chọn thuốc giãn cơ
4. Chiến lược tiền oxy hóa
5. Kế hoạch dự phòng nếu thất bại
6. An thần sau đặt nội khí quản
7. Thiết lập thở máy ban đầu

Truy vấn gốc: {original_query}""",
        },
        r"(sốt|fever|nhiệt độ|temperature)": {
            "category": "fever",
            "template": """Đánh giá sốt tại ICU:

Vui lòng phân tích:
1. Nguyên nhân nhiễm trùng có khả năng nhất
2. Nguyên nhân không nhiễm trùng (sốt do thuốc, VTE, v.v.)
3. Phác đồ kiểm tra chẩn đoán
4. Các thiết bị cần đánh giá/thay thế
5. Chỉ định kháng sinh kinh nghiệm
6. Biện pháp kiểm soát nhiễm trùng

Truy vấn gốc: {original_query}""",
        },
        r"(ngừng tim|cardiac arrest|cpr)": {
            "category": "cardiac_arrest",
            "template": """Xử trí ngừng tim:

Vui lòng hướng dẫn:
1. Thuật toán ACLS áp dụng
2. Nguyên nhân hồi phục được (H's và T's)
3. Thuốc/can thiệp chỉ định
4. Thời điểm cân nhắc ECMO/CPR cơ học
5. Tiên lượng
6. Chăm sóc sau hồi phục tuần hoàn tự nhiên (ROSC)
7. Thời điểm cân nhắc ngừng nỗ lực

Truy vấn gốc: {original_query}""",
        },
        r"(truyền máu|transfusion|xuất huyết|bleeding)": {
            "category": "transfusion",
            "template": """Xử trí xuất huyết lớn và truyền máu:

Vui lòng phân tích:
1. Cân nhắc kích hoạt phác đồ truyền máu lớn
2. Tỷ lệ chế phẩm máu khuyến cáo (RBC:FFP:Platelet)
3. Thuốc bổ trợ (TXA, calcium, v.v.)
4. Theo dõi đông máu
5. Mục tiêu hồi sức
6. Kiểm soát chảy máu quyết định cần thiết
7. Thời điểm cân nhắc chiến lược kiểm soát tổn thương

Truy vấn gốc: {original_query}""",
        },
        r"(điện giải|electrolyte|kali|natri|potassium|sodium)": {
            "category": "electrolytes",
            "template": """Phân tích và xử trí rối loạn điện giải:

Vui lòng đánh giá:
1. Mức độ nghiêm trọng của rối loạn
2. Nguyên nhân có thể
3. Nguy cơ lâm sàng (loạn nhịp tim, v.v.)
4. Phác đồ điều chỉnh
5. Tốc độ điều chỉnh an toàn
6. Theo dõi trong quá trình điều trị

Truy vấn gốc: {original_query}""",
        },
        r"(an thần|sedation|진통|analgesia)": {
            "category": "sedation",
            "template": """Tối ưu hóa an thần và giảm đau:

Vui lòng đề xuất:
1. Phác đồ an thần phù hợp
2. Chiến lược giảm đau
3. Cách thực hiện ngừng an thần hàng ngày
4. Thời điểm đánh giá rút nội khí quản
5. Phòng ngừa/điều trị mê sảng
6. Kế hoạch cai dần

Truy vấn gốc: {original_query}""",
        },
    }

    # Short query patterns that need enhancement
    SHORT_QUERY_PATTERNS = {
        r"^.{1,20}$": True,  # Very short queries (1-20 chars)
        r"^[^?.!]{1,50}$": True,  # Short queries without punctuation
    }

    @classmethod
    def should_enhance(cls, query: str) -> bool:
        """
        Determine if a query should be enhanced

        Args:
            query: User's input query

        Returns:
            True if query should be enhanced
        """
        # Don't enhance if already detailed (has multiple sentences or questions)
        if len(query.split(".")) > 2 or len(query.split("?")) > 2:
            return False

        # Don't enhance if already long and structured
        if len(query) > 200 and (":" in query or "1." in query or "-" in query):
            return False

        # Check if it matches short query patterns
        for pattern in cls.SHORT_QUERY_PATTERNS.keys():
            if re.search(pattern, query, re.IGNORECASE):
                return True

        # Check if it matches medical keywords
        for pattern in cls.ENHANCEMENT_PATTERNS.keys():
            if re.search(pattern, query, re.IGNORECASE):
                return True

        return False

    @classmethod
    def enhance_prompt(cls, query: str) -> Tuple[str, bool]:
        """
        Enhance a user query with medical context

        Args:
            query: User's input query

        Returns:
            Tuple of (enhanced_query, was_enhanced)
        """
        # Check if enhancement is needed
        if not cls.should_enhance(query):
            return query, False

        # Try to match against enhancement patterns
        for pattern, enhancement_data in cls.ENHANCEMENT_PATTERNS.items():
            if re.search(pattern, query, re.IGNORECASE):
                enhanced = enhancement_data["template"].format(original_query=query)
                return enhanced, True

        # If no specific pattern matched but query is short, add basic structure
        if len(query) < 100:
            basic_enhancement = f"""Vui lòng phân tích câu hỏi y khoa sau:

"{query}"

Hãy cung cấp:
1. Phân tích tình huống lâm sàng
2. Các yếu tố quan trọng cần xem xét
3. Khuyến nghị dựa trên bằng chứng
4. Hướng dẫn thực hành lâm sàng liên quan
"""
            return basic_enhancement, True

        return query, False

    @classmethod
    def get_enhancement_preview(cls, query: str) -> Optional[str]:
        """
        Get a preview of how the query would be enhanced

        Args:
            query: User's input query

        Returns:
            Enhanced query preview or None if no enhancement
        """
        enhanced, was_enhanced = cls.enhance_prompt(query)
        return enhanced if was_enhanced else None
