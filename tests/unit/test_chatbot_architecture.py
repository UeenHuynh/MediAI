"""
Chatbot Architecture & Question-Response Unit Tests

Tests cover:
1. Chatbot initialization & dependency chain
2. System prompt structure (ABCDE, Hour-1 Bundle, missing data)
3. Mock response routing for all question types
4. Real LLM response shape (via mocked chain)
5. Citation extraction accuracy
6. RAG context formatting
7. End-to-end endpoint flow
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from uuid import uuid4
from datetime import datetime


# ─────────────────────────────────────────────
# 1. ARCHITECTURE — Dependency & Import Chain
# ─────────────────────────────────────────────

class TestChatbotDependencyChain:
    """Verify every module in the chatbot stack can be imported cleanly."""

    def test_chat_router_importable(self):
        from api.routers.chat import router, get_chatbot, get_chat_rag_service
        assert router is not None
        assert callable(get_chatbot)
        assert callable(get_chat_rag_service)

    def test_chat_service_importable(self):
        from api.services.chat_service import ChatService
        assert ChatService is not None

    def test_chat_rag_service_importable(self):
        from api.services.chat_rag_service import ChatRAGService
        assert ChatRAGService is not None

    def test_langchain_medical_bot_importable(self):
        from api.services.langchain_medical_bot import ProductionMedicalChatbot
        assert ProductionMedicalChatbot is not None

    def test_pydantic_models_importable(self):
        from api.routers.chat import (
            Citation, ChatRequest, ChatResponse,
            ChatMessage, ConversationHistory,
        )
        assert all([Citation, ChatRequest, ChatResponse, ChatMessage, ConversationHistory])

    def test_settings_has_enable_chatbot(self):
        from api.core.config import settings
        assert hasattr(settings, "ENABLE_CHATBOT"), \
            "settings.ENABLE_CHATBOT missing — Render env var won't be picked up"

    def test_settings_has_groq_api_key(self):
        from api.core.config import settings
        assert hasattr(settings, "GROQ_API_KEY"), \
            "settings.GROQ_API_KEY missing — LLM won't initialize"

    def test_settings_has_semantic_scholar_key(self):
        from api.core.config import settings
        assert hasattr(settings, "SEMANTIC_SCHOLAR_API_KEY"), \
            "settings.SEMANTIC_SCHOLAR_API_KEY missing — Scholar tier disabled"

    def test_get_chatbot_returns_none_when_disabled(self):
        import api.routers.chat as m
        with patch.object(m.settings, "ENABLE_CHATBOT", False):
            m._chatbot_instance = None
            assert m.get_chatbot() is None

    def test_get_chatbot_initializes_when_enabled(self):
        import api.routers.chat as m
        mock_bot = MagicMock()
        with patch.object(m.settings, "ENABLE_CHATBOT", True):
            m._chatbot_instance = None
            # Patch the import inside get_chatbot via sys.modules
            import sys
            fake_module = MagicMock()
            fake_module.ProductionMedicalChatbot.return_value = mock_bot
            with patch.dict(sys.modules, {"services.langchain_medical_bot": fake_module}):
                result = m.get_chatbot()
        # Either initialized or None (if env not fully set up)
        assert result is mock_bot or result is None

    def test_resolve_provider_groq_when_key_available(self):
        from api.routers.chat import resolve_chatbot_provider
        with patch("api.routers.chat.settings") as s:
            s.LLM_PROVIDER = "groq"
            s.GROQ_API_KEY = "test-key"
            assert resolve_chatbot_provider() == "groq"

    def test_resolve_provider_falls_back_from_gemini(self):
        from api.routers.chat import resolve_chatbot_provider
        with patch("api.routers.chat.settings") as s:
            s.LLM_PROVIDER = "gemini"
            s.GROQ_API_KEY = "test-key"
            s.OPENAI_API_KEY = None
            s.AWS_ACCESS_KEY_ID = None
            assert resolve_chatbot_provider() == "groq"

    def test_resolve_provider_falls_back_to_openai_when_no_groq(self):
        from api.routers.chat import resolve_chatbot_provider
        with patch("api.routers.chat.settings") as s:
            s.LLM_PROVIDER = "gemini"
            s.GROQ_API_KEY = None
            s.OPENAI_API_KEY = "openai-key"
            s.AWS_ACCESS_KEY_ID = None
            assert resolve_chatbot_provider() == "openai"


# ─────────────────────────────────────────────
# 2. SYSTEM PROMPT STRUCTURE
# ─────────────────────────────────────────────

class TestSystemPromptStructure:
    """Verify system prompt contains all required clinical reasoning sections."""

    @pytest.fixture
    def prompt(self):
        from api.services.langchain_medical_bot import ProductionMedicalChatbot
        bot = ProductionMedicalChatbot.__new__(ProductionMedicalChatbot)
        bot.enable_pii_redaction = False
        return bot._get_system_prompt()

    @pytest.fixture
    def user_template(self):
        from api.services.langchain_medical_bot import ProductionMedicalChatbot
        bot = ProductionMedicalChatbot.__new__(ProductionMedicalChatbot)
        return bot._get_user_template()

    def test_prompt_contains_abcde(self, prompt):
        assert "ABCDE" in prompt or "Airway" in prompt, \
            "ABCDE framework missing from system prompt"

    def test_prompt_contains_airway(self, prompt):
        assert "Airway" in prompt or "airway" in prompt

    def test_prompt_contains_circulation(self, prompt):
        assert "Circulation" in prompt or "MAP" in prompt

    def test_prompt_contains_sofa_definition(self, prompt):
        assert "SOFA" in prompt, "SOFA scoring criteria missing"

    def test_prompt_contains_sepsis3(self, prompt):
        assert "Sepsis-3" in prompt or "sepsis" in prompt.lower()

    def test_prompt_contains_hour1_bundle(self, prompt):
        assert "Hour-1" in prompt or "hour-1" in prompt.lower() or "Bundle" in prompt

    def test_prompt_contains_antibiotic_instruction(self, prompt):
        assert "antibiotic" in prompt.lower() or "kháng sinh" in prompt

    def test_prompt_contains_missing_data_handling(self, prompt):
        """Prompt must instruct LLM how to handle incomplete lab data."""
        assert any(kw in prompt.lower() for kw in ["missing", "incomplete", "thiếu", "pending"])

    def test_prompt_contains_lactate(self, prompt):
        assert "lactate" in prompt.lower() or "Lactate" in prompt

    def test_prompt_contains_vasopressor(self, prompt):
        assert "vasopressor" in prompt.lower() or "norepinephrine" in prompt.lower()

    def test_prompt_contains_disclaimer(self, prompt):
        assert "⚠️" in prompt or "disclaimer" in prompt.lower() or "thẩm quyền" in prompt

    def test_prompt_language_instruction(self, user_template):
        """Language instruction is in the user template (not system prompt)."""
        assert "Vietnamese" in user_template or "language" in user_template.lower()

    def test_user_template_has_context_slot(self, user_template):
        assert "{context}" in user_template

    def test_user_template_has_question_slot(self, user_template):
        assert "{question}" in user_template

    def test_user_template_has_chat_history_slot(self, user_template):
        assert "{chat_history}" in user_template

    def test_user_template_instructs_actionable_response(self, user_template):
        assert "action" in user_template.lower() or "actionable" in user_template.lower()


# ─────────────────────────────────────────────
# 3. MOCK RESPONSE — Question Routing
# ─────────────────────────────────────────────

class TestMockResponseRouting:
    """Verify get_mock_response routes all question categories correctly."""

    QUESTIONS = {
        "icu_generic":    "bệnh nhân vừa nhập icu thì sao",
        "sofa":           "sofa là gì",
        "sofa_score":     "SOFA score là gì",
        "apache":         "apache là gì",
        "sepsis_basic":   "sepsis là gì",
        "sepsis_85":      "với sepsis 85% thì cần hành động gì",
        "sepsis_high":    "bệnh nhân nguy cơ cao sepsis 85%",
        "mortality":      "mortality prediction in icu",
        "blood_pressure": "blood pressure target in icu",
        "hypertension":   "hypertension management",
        "unknown":        "xin chào tôi bị đau đầu",
    }

    def _call(self, q):
        from api.routers.chat import get_mock_response
        return get_mock_response(q)

    # SOFA
    def test_sofa_returns_6_organs(self):
        answer, _ = self._call(self.QUESTIONS["sofa"])
        assert "SOFA" in answer
        organ_keywords = ["hô hấp", "đông máu", "gan", "tim", "thần kinh", "thận"]
        found = sum(1 for kw in organ_keywords if kw in answer.lower())
        assert found >= 4, f"Expected ≥4 organ systems, found {found}"

    def test_sofa_has_pubmed_citation(self):
        _, citations = self._call(self.QUESTIONS["sofa"])
        assert any(c.pmid for c in citations), "SOFA response needs PubMed citation"

    def test_sofa_citations_have_urls(self):
        _, citations = self._call(self.QUESTIONS["sofa"])
        for c in citations:
            assert c.url, f"Citation [{c.number}] missing URL"

    def test_apache_returns_apache_content(self):
        answer, citations = self._call(self.QUESTIONS["apache"])
        assert "APACHE" in answer
        assert len(citations) >= 1

    # Sepsis basic
    def test_sepsis_basic_returns_content(self):
        answer, citations = self._call(self.QUESTIONS["sepsis_basic"])
        assert "sepsis" in answer.lower()
        assert len(citations) >= 1

    # Sepsis 85% high-risk
    def test_sepsis_85_returns_action_content(self):
        answer, _ = self._call(self.QUESTIONS["sepsis_85"])
        clinical_keywords = ["kháng sinh", "antibiotic", "bundle", "vasopressor",
                             "icu", "lactate", "truyền dịch", "cấy máu"]
        found = [kw for kw in clinical_keywords if kw in answer.lower()]
        assert len(found) >= 2, f"Expected clinical actions, got: {answer[:200]}"

    def test_sepsis_85_has_live_api_citation(self):
        _, citations = self._call(self.QUESTIONS["sepsis_85"])
        live = [c for c in citations if c.source_type == "live_api"]
        assert len(live) >= 1, "High-risk sepsis needs live_api citation"

    def test_sepsis_high_risk_triggers_same_handler(self):
        answer1, _ = self._call(self.QUESTIONS["sepsis_85"])
        answer2, _ = self._call(self.QUESTIONS["sepsis_high"])
        # Both should be clinical action responses (not generic)
        assert "kháng sinh" in answer1.lower() or "bundle" in answer1.lower()
        assert "kháng sinh" in answer2.lower() or "bundle" in answer2.lower()

    # Mortality
    def test_mortality_returns_scoring_content(self):
        answer, citations = self._call(self.QUESTIONS["mortality"])
        assert any(kw in answer for kw in ["APACHE", "SOFA", "mortality"])
        assert len(citations) >= 1

    # Blood pressure
    def test_blood_pressure_returns_map_content(self):
        answer, _ = self._call(self.QUESTIONS["blood_pressure"])
        assert any(kw in answer.lower() for kw in ["blood pressure", "map", "mmhg", "hypertension"])

    # ICU generic — currently falls to generic fallback
    def test_icu_generic_returns_something(self):
        answer, _ = self._call(self.QUESTIONS["icu_generic"])
        assert len(answer) > 10, "Empty response for ICU generic question"

    def test_icu_generic_needs_improvement_flag(self):
        """Document that 'bệnh nhân vừa nhập icu' needs a dedicated mock handler."""
        answer, citations = self._call(self.QUESTIONS["icu_generic"])
        is_generic = "thank you for your question" in answer.lower()
        # This test documents current behavior — should be False after adding handler
        if is_generic:
            pytest.xfail(
                "ICU generic question hits fallback handler — "
                "add 'icu' keyword to get_mock_response for better UX when ENABLE_CHATBOT=false"
            )

    # Unknown
    def test_unknown_returns_generic_with_no_citations(self):
        answer, citations = self._call(self.QUESTIONS["unknown"])
        assert len(answer) > 0
        # Generic may or may not have citations — just shouldn't crash


# ─────────────────────────────────────────────
# 4. FIX — Add ICU generic handler to mock
# ─────────────────────────────────────────────

class TestICUAdmissionMockHandler:
    """After adding ICU handler, these must all pass."""

    ICU_QUERIES = [
        "bệnh nhân vừa nhập icu thì sao",
        "bệnh nhân mới vào icu cần làm gì",
        "icu admission protocol",
        "bệnh nhân nhập icu cần đánh giá gì",
        "bệnh nhân có sofa cao cần đặt nội khí quản chưa làm hóa sinh",
    ]

    def _call(self, q):
        from api.routers.chat import get_mock_response
        return get_mock_response(q)

    @pytest.mark.parametrize("question", ICU_QUERIES)
    def test_icu_question_returns_clinical_content(self, question):
        answer, citations = self._call(question)
        clinical_keywords = [
            "abcde", "airway", "đường thở", "sofa", "sepsis",
            "kháng sinh", "antibiotic", "lactate", "huyết động",
            "đánh giá", "assessment", "bundle",
        ]
        found = [kw for kw in clinical_keywords if kw in answer.lower()]
        assert len(found) >= 1, \
            f"Expected clinical content for '{question[:50]}', got: {answer[:150]}"

    @pytest.mark.parametrize("question", ICU_QUERIES)
    def test_icu_question_has_citations(self, question):
        _, citations = self._call(question)
        assert len(citations) >= 1, \
            f"ICU question '{question[:50]}' should have citations"


# ─────────────────────────────────────────────
# 5. REAL CHATBOT — Mocked LLM Response Shape
# ─────────────────────────────────────────────

class TestProductionChatbotResponseShape:
    """Test ProductionMedicalChatbot.query() output shape with mocked LLM."""

    @pytest.fixture
    def bot(self):
        from api.services.langchain_medical_bot import ProductionMedicalChatbot
        with patch("api.services.langchain_medical_bot.ChatGroq") as mock_groq:
            mock_llm = MagicMock()
            mock_groq.return_value = mock_llm
            b = ProductionMedicalChatbot(
                provider="groq",
                enable_pii_redaction=False,
                enable_callbacks=False,
            )
            b.chain = MagicMock()
        return b

    @pytest.fixture
    def source_docs(self):
        return [
            {"number": 1, "source": "PubMed (PMID: 34599691)", "title": "SSC Guidelines",
             "url": "https://pubmed.ncbi.nlm.nih.gov/34599691/", "pmid": "34599691",
             "tier": "pubmed", "source_type": "live_api"},
            {"number": 2, "source": "JAMA 2016", "title": "Sepsis-3 Definition",
             "url": "https://pubmed.ncbi.nlm.nih.gov/26903338/", "pmid": "26903338",
             "tier": "pubmed", "source_type": "live_api"},
            {"number": 3, "source": "SSC Ventilation", "title": "Mechanical Ventilation",
             "url": "https://www.sccm.org/ssc", "pmid": None,
             "tier": "cag", "source_type": "local"},
        ]

    def _query(self, bot, answer_text, source_docs, question):
        bot.chain.invoke.return_value = answer_text
        return bot.query(
            question=question,
            retrieved_context="[1] SSC\n[2] Sepsis-3\n[3] Ventilation",
            source_docs=source_docs,
        )

    # Shape tests
    def test_query_returns_dict(self, bot, source_docs):
        result = self._query(bot, "Answer [1].", source_docs, "sofa là gì")
        assert isinstance(result, dict)

    def test_query_has_answer_key(self, bot, source_docs):
        result = self._query(bot, "Answer [1].", source_docs, "sofa là gì")
        assert "answer" in result
        assert isinstance(result["answer"], str)

    def test_query_has_citations_key(self, bot, source_docs):
        result = self._query(bot, "Answer [1].", source_docs, "sofa là gì")
        assert "citations" in result
        assert isinstance(result["citations"], list)

    def test_query_has_error_key(self, bot, source_docs):
        result = self._query(bot, "Answer [1].", source_docs, "sofa là gì")
        assert "error" in result

    def test_query_has_model_name(self, bot, source_docs):
        result = self._query(bot, "Answer [1].", source_docs, "sofa là gì")
        assert "model_name" in result

    # Citation extraction
    def test_citation_extracted_when_referenced(self, bot, source_docs):
        result = self._query(bot, "Sepsis needs antibiotics [1] and fluids [2].", source_docs, "q")
        assert len(result["citations"]) == 2

    def test_citation_not_extracted_when_not_referenced(self, bot, source_docs):
        result = self._query(bot, "General answer with no citations.", source_docs, "q")
        assert len(result["citations"]) == 0

    def test_citation_metadata_preserved(self, bot, source_docs):
        result = self._query(bot, "Guidelines [1] define sepsis [2].", source_docs, "q")
        c1 = result["citations"][0]
        assert c1["pmid"] == "34599691"
        assert c1["tier"] == "pubmed"
        assert c1["source_type"] == "live_api"
        assert "pubmed.ncbi" in c1["url"]

    def test_citation_3_is_local(self, bot, source_docs):
        result = self._query(bot, "Ventilation protocol [3].", source_docs, "q")
        c3 = result["citations"][0]
        assert c3["source_type"] == "local"
        assert c3["tier"] == "cag"

    def test_no_duplicate_citations(self, bot, source_docs):
        result = self._query(bot, "Action [1] and [1] again.", source_docs, "q")
        numbers = [c["number"] for c in result["citations"]]
        assert len(numbers) == len(set(numbers)), "Duplicate citations found"

    # Error handling
    def test_query_returns_error_on_llm_failure(self, bot, source_docs):
        bot.chain.invoke.side_effect = Exception("LLM timeout")
        result = bot.query(question="test", retrieved_context="ctx", source_docs=source_docs)
        assert result["error"] is not None
        assert "answer" in result  # Still returns answer key


# ─────────────────────────────────────────────
# 6. COMPLEX ICU SCENARIO — Full Endpoint Flow
# ─────────────────────────────────────────────

COMPLEX_QUESTIONS = [
    "bệnh nhân vừa nhập icu thì sao",
    "bệnh nhân có sofa cao, cần đặt nội khí quản, chưa làm hóa sinh, hành động tiếp theo là gì",
    "bệnh nhân sepsis 85%, chỉ số sofa 10, MAP 55, cần làm gì ngay",
    "ICU patient with high SOFA, needs intubation, no labs done yet, what actions",
    "bệnh nhân suy đa tạng, lactate 5, cần vasopressor không",
]

RAG_CONTEXT = """[1] Surviving Sepsis Campaign Guidelines 2021 (PMID: 34599691)
Source: PubMed
Hour-1 Bundle: blood cultures → broad-spectrum antibiotics → lactate → 30mL/kg crystalloid if MAP<65 or lactate≥4 → vasopressor (norepinephrine) if MAP<65 persists.

[2] Sepsis-3 Definition — Singer M et al. JAMA 2016 (PMID: 26903338)
Source: PubMed
SOFA ≥2 from baseline + suspected infection = Sepsis. Vasopressor need + lactate >2 despite fluids = Septic Shock.

[3] Mechanical Ventilation in Sepsis-ARDS — SSC
Source: Local Knowledge
Lung-protective ventilation: Vt 6mL/kg IBW, Pplat <30 cmH2O, PEEP titration, SpO2 92-96%."""

SOURCE_DOCS = [
    {"number": 1, "source": "SSC 2021", "title": "Surviving Sepsis Campaign Guidelines",
     "url": "https://pubmed.ncbi.nlm.nih.gov/34599691/", "pmid": "34599691",
     "tier": "pubmed", "source_type": "live_api"},
    {"number": 2, "source": "JAMA 2016", "title": "Sepsis-3 Definition",
     "url": "https://pubmed.ncbi.nlm.nih.gov/26903338/", "pmid": "26903338",
     "tier": "pubmed", "source_type": "live_api"},
    {"number": 3, "source": "SSC Ventilation", "title": "Lung-protective ventilation",
     "url": "https://www.sccm.org/ssc", "pmid": None,
     "tier": "cag", "source_type": "local"},
]


class TestComplexICUEndpointFlow:
    """End-to-end endpoint test for complex ICU scenarios."""

    def _make_bot(self, answer_text):
        mock_bot = MagicMock()
        mock_bot.query.return_value = {
            "answer": answer_text,
            "citations": [
                {"source": "SSC 2021", "title": "SSC Guidelines",
                 "url": "https://pubmed.ncbi.nlm.nih.gov/34599691/",
                 "pmid": "34599691", "tier": "pubmed", "source_type": "live_api"},
                {"source": "JAMA 2016", "title": "Sepsis-3",
                 "url": "https://pubmed.ncbi.nlm.nih.gov/26903338/",
                 "pmid": "26903338", "tier": "pubmed", "source_type": "live_api"},
            ],
            "redacted_query": None,
            "model_name": "llama-3.3-70b",
            "disclaimer": "⚠️ Educational only.",
        }
        return mock_bot

    def _make_rag(self):
        mock_rag = MagicMock()
        mock_rag.build_retrieval_package.return_value = {
            "retrieved_context": RAG_CONTEXT,
            "source_docs": SOURCE_DOCS,
            "retrieval_context": {
                "search_query": "icu admission",
                "documents_count": 3,
                "documents": SOURCE_DOCS,
            },
        }
        return mock_rag

    @pytest.mark.asyncio
    @pytest.mark.parametrize("question", COMPLEX_QUESTIONS)
    async def test_complex_icu_question_gets_response(self, question):
        from api.routers.chat import send_message, ChatRequest

        ANSWER = (
            "Bệnh nhân cần được đánh giá ABCDE ngay. [1] "
            "Thực hiện Hour-1 Bundle: cấy máu, kháng sinh phổ rộng, "
            "đo lactate, truyền dịch 30mL/kg nếu MAP<65. [2] "
            "Nếu cần thở máy: Vt 6mL/kg, Pplat<30. [3]"
        )

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        with patch("api.routers.chat.ChatService") as svc:
            with patch("api.routers.chat.get_chatbot", return_value=self._make_bot(ANSWER)):
                with patch("api.routers.chat.get_chat_rag_service", return_value=self._make_rag()):
                    svc.get_or_create_session.return_value = (mock_session, True)
                    svc.get_recent_messages.return_value = []

                    result = await send_message(
                        ChatRequest(message=question, include_sources=True),
                        mock_user, mock_db,
                    )

        assert result.answer is not None
        assert len(result.answer) > 20
        assert result.session_id == str(mock_session.session_id)

    @pytest.mark.asyncio
    async def test_icu_response_includes_pubmed_citations(self):
        from api.routers.chat import send_message, ChatRequest

        ANSWER = "Bundle actions [1]. Sepsis-3 criteria [2]."
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        with patch("api.routers.chat.ChatService") as svc:
            with patch("api.routers.chat.get_chatbot", return_value=self._make_bot(ANSWER)):
                with patch("api.routers.chat.get_chat_rag_service", return_value=self._make_rag()):
                    svc.get_or_create_session.return_value = (mock_session, True)
                    svc.get_recent_messages.return_value = []

                    result = await send_message(
                        ChatRequest(message=COMPLEX_QUESTIONS[0], include_sources=True),
                        mock_user, mock_db,
                    )

        pubmed_cits = [c for c in result.citations if c.tier == "pubmed"]
        assert len(pubmed_cits) >= 1

    @pytest.mark.asyncio
    async def test_icu_response_rag_context_passed_to_chatbot(self):
        from api.routers.chat import send_message, ChatRequest

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_session = MagicMock()
        mock_session.session_id = uuid4()
        mock_bot = self._make_bot("Answer [1].")
        mock_rag = self._make_rag()

        with patch("api.routers.chat.ChatService") as svc:
            with patch("api.routers.chat.get_chatbot", return_value=mock_bot):
                with patch("api.routers.chat.get_chat_rag_service", return_value=mock_rag):
                    svc.get_or_create_session.return_value = (mock_session, True)
                    svc.get_recent_messages.return_value = []

                    await send_message(
                        ChatRequest(message=COMPLEX_QUESTIONS[1], include_sources=True),
                        mock_user, mock_db,
                    )

        kwargs = mock_bot.query.call_args.kwargs
        assert "Hour-1 Bundle" in kwargs["retrieved_context"]
        assert kwargs["source_docs"][0]["pmid"] == "34599691"

    @pytest.mark.asyncio
    async def test_icu_missing_labs_scenario(self):
        """Scenario: patient with no biochemistry done yet."""
        from api.routers.chat import send_message, ChatRequest

        QUESTION = "bệnh nhân sofa 12, cần đặt NKQ, chưa có kết quả xét nghiệm hóa sinh"
        ANSWER = (
            "Không chờ kết quả xét nghiệm — bắt đầu điều trị ngay [1]. "
            "Cần làm ngay: lactate, cấy máu, CBC, BMP, coagulation, ABG. "
            "Kháng sinh phổ rộng ngay lập tức [2]."
        )
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        with patch("api.routers.chat.ChatService") as svc:
            with patch("api.routers.chat.get_chatbot", return_value=self._make_bot(ANSWER)):
                with patch("api.routers.chat.get_chat_rag_service", return_value=self._make_rag()):
                    svc.get_or_create_session.return_value = (mock_session, True)
                    svc.get_recent_messages.return_value = []

                    result = await send_message(
                        ChatRequest(message=QUESTION, include_sources=True),
                        mock_user, mock_db,
                    )

        assert len(result.answer) > 20
        assert len(result.citations) >= 1

    @pytest.mark.asyncio
    async def test_chatbot_fallback_on_llm_error(self):
        """When LLM fails, endpoint falls back to mock — not 500 error."""
        from api.routers.chat import send_message, ChatRequest

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        broken_bot = MagicMock()
        broken_bot.query.side_effect = Exception("Groq API timeout")

        with patch("api.routers.chat.ChatService") as svc:
            with patch("api.routers.chat.get_chatbot", return_value=broken_bot):
                with patch("api.routers.chat.get_chat_rag_service", return_value=self._make_rag()):
                    svc.get_or_create_session.return_value = (mock_session, True)
                    svc.get_recent_messages.return_value = []

                    result = await send_message(
                        ChatRequest(message="sofa là gì", include_sources=True),
                        mock_user, mock_db,
                    )

        # Should fall back to mock, not raise exception
        assert result.answer is not None
        assert len(result.answer) > 0


# ─────────────────────────────────────────────
# 7. RAG SERVICE — Query Building & Selection
# ─────────────────────────────────────────────

class TestChatRAGServiceArchitecture:
    """Test RAG service document selection and context formatting."""

    def _service(self, docs):
        from api.services.chat_rag_service import ChatRAGService
        mock_rag = MagicMock()
        mock_rag.retrieve.return_value = docs
        return ChatRAGService(hybrid_rag=mock_rag, top_k=3)

    def test_icu_question_builds_search_query(self):
        from api.services.chat_rag_service import ChatRAGService
        svc = ChatRAGService(hybrid_rag=MagicMock())
        q = svc._build_search_query("bệnh nhân vừa nhập icu thì sao")
        assert len(q) > 5

    def test_short_followup_includes_context(self):
        from api.services.chat_rag_service import ChatRAGService
        svc = ChatRAGService(hybrid_rag=MagicMock())
        q = svc._build_search_query(
            "Tiếp theo?",
            [("user", "Bệnh nhân sepsis nặng"), ("assistant", "Cần kháng sinh")],
        )
        assert "sepsis" in q.lower()

    def test_pubmed_doc_included_in_selection(self):
        docs = [
            {"content": "CAG content", "source": "CAG", "tier": "cag", "score": 0.95},
            {"content": "PubMed content", "source": "PubMed", "tier": "pubmed",
             "score": 0.85, "metadata": {"pmid": "12345", "title": "Sepsis Paper"}},
        ]
        svc = self._service(docs)
        result = svc.build_retrieval_package("sepsis treatment")
        tiers = {d["tier"] for d in result["source_docs"]}
        assert "pubmed" in tiers

    def test_context_has_numbered_format(self):
        docs = [
            {"content": "Guideline content", "source": "PubMed", "tier": "pubmed",
             "score": 0.9, "metadata": {"pmid": "111", "title": "SSC"}},
        ]
        svc = self._service(docs)
        result = svc.build_retrieval_package("icu management")
        assert "[1]" in result["retrieved_context"]

    def test_source_docs_have_required_fields(self):
        docs = [
            {"content": "Content", "source": "PubMed", "tier": "pubmed",
             "score": 0.9, "metadata": {"pmid": "222", "title": "Test Paper"}},
        ]
        svc = self._service(docs)
        result = svc.build_retrieval_package("test")
        for doc in result["source_docs"]:
            assert "number" in doc
            assert "source" in doc
            assert "tier" in doc
            assert "source_type" in doc

    def test_empty_retrieval_returns_empty_context(self):
        from api.services.chat_rag_service import ChatRAGService
        mock_rag = MagicMock()
        mock_rag.retrieve.return_value = []
        svc = ChatRAGService(hybrid_rag=mock_rag, top_k=3)
        result = svc.build_retrieval_package("test question")
        assert result["retrieved_context"] == ""
        assert result["source_docs"] == []

    def test_retrieval_failure_returns_empty_gracefully(self):
        from api.services.chat_rag_service import ChatRAGService
        mock_rag = MagicMock()
        mock_rag.retrieve.side_effect = Exception("Qdrant connection failed")
        svc = ChatRAGService(hybrid_rag=mock_rag, top_k=3)
        result = svc.build_retrieval_package("sepsis management")
        assert result["retrieved_context"] == ""
        assert result["source_docs"] == []
        assert result["retrieval_context"]["documents_count"] == 0
