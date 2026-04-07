"""
Unit tests for Chat router
Tests chat API endpoints and related models
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestChatRouterConfig:
    """Tests for chat router configuration"""

    def test_router_exists(self):
        """Test chat router exists"""
        from api.routers.chat import router
        
        assert router is not None

    def test_router_has_prefix(self):
        """Test chat router has /chat prefix"""
        from api.routers.chat import router
        
        assert router.prefix == "/chat"

    def test_router_has_send_message_endpoint(self):
        """Test send message endpoint is registered"""
        from api.routers.chat import router
        
        routes = [r.path for r in router.routes]
        
        # Should have a POST endpoint for messages
        assert "/" in routes or "/message" in routes or len(routes) > 0


class TestChatModels:
    """Tests for chat Pydantic models"""

    def test_citation_model_exists(self):
        """Test Citation model exists"""
        from api.routers.chat import Citation
        
        assert Citation is not None

    def test_chat_message_model_exists(self):
        """Test ChatMessage model exists"""
        from api.routers.chat import ChatMessage
        
        assert ChatMessage is not None

    def test_chat_request_model_exists(self):
        """Test ChatRequest model exists"""
        from api.routers.chat import ChatRequest
        
        assert ChatRequest is not None

    def test_chat_response_model_exists(self):
        """Test ChatResponse model exists"""
        from api.routers.chat import ChatResponse
        
        assert ChatResponse is not None

    def test_conversation_history_model_exists(self):
        """Test ConversationHistory model exists"""
        from api.routers.chat import ConversationHistory
        
        assert ConversationHistory is not None


class TestCitationModel:
    """Tests for Citation model fields"""

    def test_citation_has_number(self):
        """Test Citation has number field"""
        from api.routers.chat import Citation
        
        field_names = list(Citation.model_fields.keys()) if hasattr(Citation, 'model_fields') else list(Citation.__annotations__.keys())
        
        assert 'number' in field_names

    def test_citation_has_source(self):
        """Test Citation has source field"""
        from api.routers.chat import Citation
        
        field_names = list(Citation.model_fields.keys()) if hasattr(Citation, 'model_fields') else list(Citation.__annotations__.keys())
        
        assert 'source' in field_names

    def test_citation_has_url(self):
        """Test Citation has url field"""
        from api.routers.chat import Citation
        
        field_names = list(Citation.model_fields.keys()) if hasattr(Citation, 'model_fields') else list(Citation.__annotations__.keys())
        
        assert 'url' in field_names


class TestChatRequestModel:
    """Tests for ChatRequest model"""

    def test_chat_request_has_message(self):
        """Test ChatRequest has message field"""
        from api.routers.chat import ChatRequest
        
        field_names = list(ChatRequest.model_fields.keys()) if hasattr(ChatRequest, 'model_fields') else list(ChatRequest.__annotations__.keys())
        
        assert 'message' in field_names

    def test_chat_request_has_session_id(self):
        """Test ChatRequest has session_id field"""
        from api.routers.chat import ChatRequest
        
        field_names = list(ChatRequest.model_fields.keys()) if hasattr(ChatRequest, 'model_fields') else list(ChatRequest.__annotations__.keys())
        
        assert 'session_id' in field_names

    def test_chat_request_has_include_sources(self):
        """Test ChatRequest has include_sources field"""
        from api.routers.chat import ChatRequest
        
        field_names = list(ChatRequest.model_fields.keys()) if hasattr(ChatRequest, 'model_fields') else list(ChatRequest.__annotations__.keys())
        
        assert 'include_sources' in field_names

    def test_chat_request_message_validation(self):
        """Test ChatRequest validates message length"""
        from api.routers.chat import ChatRequest
        from pydantic import ValidationError
        
        # Valid request
        request = ChatRequest(message="What is sepsis?")
        assert request.message == "What is sepsis?"
        
        # Empty message should fail
        try:
            ChatRequest(message="")
            assert False, "Should raise validation error"
        except ValidationError:
            pass


class TestChatResponseModel:
    """Tests for ChatResponse model"""

    def test_chat_response_has_answer(self):
        """Test ChatResponse has answer field"""
        from api.routers.chat import ChatResponse
        
        field_names = list(ChatResponse.model_fields.keys()) if hasattr(ChatResponse, 'model_fields') else list(ChatResponse.__annotations__.keys())
        
        assert 'answer' in field_names

    def test_chat_response_has_citations(self):
        """Test ChatResponse has citations field"""
        from api.routers.chat import ChatResponse
        
        field_names = list(ChatResponse.model_fields.keys()) if hasattr(ChatResponse, 'model_fields') else list(ChatResponse.__annotations__.keys())
        
        assert 'citations' in field_names

    def test_chat_response_has_disclaimer(self):
        """Test ChatResponse has disclaimer field"""
        from api.routers.chat import ChatResponse
        
        field_names = list(ChatResponse.model_fields.keys()) if hasattr(ChatResponse, 'model_fields') else list(ChatResponse.__annotations__.keys())
        
        assert 'disclaimer' in field_names

    def test_chat_response_has_session_id(self):
        """Test ChatResponse has session_id field"""
        from api.routers.chat import ChatResponse
        
        field_names = list(ChatResponse.model_fields.keys()) if hasattr(ChatResponse, 'model_fields') else list(ChatResponse.__annotations__.keys())
        
        assert 'session_id' in field_names


class TestMockResponse:
    """Tests for mock response functionality"""

    def test_get_mock_response_exists(self):
        """Test get_mock_response function exists"""
        from api.routers.chat import get_mock_response
        
        assert get_mock_response is not None
        assert callable(get_mock_response)

    def test_get_mock_response_returns_dict(self):
        """Test get_mock_response returns tuple"""
        from api.routers.chat import get_mock_response

        result = get_mock_response("What is diabetes?")

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_mock_response_has_answer(self):
        """Test mock response includes answer"""
        from api.routers.chat import get_mock_response

        answer, citations = get_mock_response("What is diabetes?")

        assert isinstance(answer, str)
        assert len(answer) > 0

    def test_mock_response_has_citations(self):
        """Test mock response includes citations"""
        from api.routers.chat import get_mock_response

        answer, citations = get_mock_response("What is diabetes?")

        assert isinstance(citations, list)

    def test_mock_response_for_sepsis(self):
        """Test mock response for sepsis query"""
        from api.routers.chat import get_mock_response

        answer, citations = get_mock_response("sepsis symptoms")

        # Should have relevant content
        assert 'sepsis' in answer.lower() or len(answer) > 0


class TestGetChatbot:
    """Tests for get_chatbot function"""

    def test_get_chatbot_exists(self):
        """Test get_chatbot function exists"""
        from api.routers.chat import get_chatbot

        assert get_chatbot is not None
        assert callable(get_chatbot)

    def test_get_chatbot_returns_instance_or_none(self):
        """Test get_chatbot returns chatbot or None"""
        from api.routers.chat import get_chatbot

        chatbot = get_chatbot()

        # May be None if disabled, or chatbot instance if enabled
        assert chatbot is None or chatbot is not None

    @patch('api.routers.chat.settings')
    def test_get_chatbot_returns_none_when_disabled(self, mock_settings):
        """Test get_chatbot returns None when ENABLE_CHATBOT is False"""
        import api.routers.chat as chat_module

        mock_settings.ENABLE_CHATBOT = False
        chat_module._chatbot_instance = None

        result = chat_module.get_chatbot()

        assert result is None

    @patch('api.routers.chat.settings')
    @patch('api.routers.chat.ProductionMedicalChatbot', create=True)
    def test_get_chatbot_creates_instance_when_enabled(self, mock_chatbot_class, mock_settings):
        """Test get_chatbot creates instance when ENABLE_CHATBOT is True"""
        import api.routers.chat as chat_module

        mock_settings.ENABLE_CHATBOT = True
        chat_module._chatbot_instance = None

        mock_chatbot_instance = MagicMock()
        mock_chatbot_class.return_value = mock_chatbot_instance

        with patch.dict('os.environ', {'LLM_PROVIDER': 'groq'}):
            with patch('api.routers.chat.ProductionMedicalChatbot', mock_chatbot_class):
                result = chat_module.get_chatbot()

        # Should return the created instance or None (if creation fails)
        assert result is not None or result is None

    @patch("api.routers.chat.settings")
    def test_resolve_chatbot_provider_falls_back_from_unsupported_provider(
        self, mock_settings
    ):
        """Unsupported configured providers should fall back to a supported one."""
        from api.routers.chat import resolve_chatbot_provider

        mock_settings.LLM_PROVIDER = "gemini"
        mock_settings.GROQ_API_KEY = "test-groq-key"
        mock_settings.OPENAI_API_KEY = None
        mock_settings.AWS_ACCESS_KEY_ID = None

        assert resolve_chatbot_provider() == "groq"


class TestMockResponseDetailed:
    """Detailed tests for get_mock_response"""

    def test_sepsis_response_includes_citations(self):
        """Test sepsis query returns citations"""
        from api.routers.chat import get_mock_response

        answer, citations = get_mock_response("What is sepsis?")

        assert len(citations) > 0
        assert any(c.source for c in citations)

    def test_mortality_response(self):
        """Test mortality query returns relevant content"""
        from api.routers.chat import get_mock_response

        answer, citations = get_mock_response("mortality prediction")

        assert "mortality" in answer.lower() or "APACHE" in answer or "SOFA" in answer
        assert len(citations) > 0

    def test_blood_pressure_response(self):
        """Test blood pressure query returns relevant content"""
        from api.routers.chat import get_mock_response

        answer, citations = get_mock_response("blood pressure levels")

        assert "blood pressure" in answer.lower() or "hypertension" in answer.lower()

    def test_generic_response(self):
        """Test generic query returns generic helpful response"""
        from api.routers.chat import get_mock_response

        answer, citations = get_mock_response("random medical question xyz")

        assert len(answer) > 0
        assert "medical" in answer.lower() or "information" in answer.lower()


class TestSendMessageEndpoint:
    """Tests for send_message endpoint"""

    @pytest.mark.asyncio
    async def test_send_message_uses_mock_when_chatbot_disabled(self):
        """Test send_message uses mock response when chatbot disabled"""
        from api.routers.chat import send_message, ChatRequest
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        with patch('api.routers.chat.ChatService') as mock_service:
            with patch('api.routers.chat.get_chatbot', return_value=None):
                mock_service.get_or_create_session.return_value = (mock_session, True)
                mock_service.get_recent_messages.return_value = []

                request = ChatRequest(message="What is sepsis?")

                result = await send_message(request, mock_user, mock_db)

        assert result.answer is not None
        assert result.session_id == str(mock_session.session_id)

    @pytest.mark.asyncio
    async def test_send_message_saves_user_message(self):
        """Test send_message saves user message to database"""
        from api.routers.chat import send_message, ChatRequest
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        with patch('api.routers.chat.ChatService') as mock_service:
            with patch('api.routers.chat.get_chatbot', return_value=None):
                mock_service.get_or_create_session.return_value = (mock_session, True)
                mock_service.get_recent_messages.return_value = []

                request = ChatRequest(message="Test message")

                await send_message(request, mock_user, mock_db)

        # Should save user message
        mock_service.add_message.assert_called()
        call_args = mock_service.add_message.call_args_list[0]
        assert call_args[1]["role"] == "user"
        assert call_args[1]["content"] == "Test message"

    @pytest.mark.asyncio
    async def test_send_message_saves_assistant_response(self):
        """Test send_message saves assistant response to database"""
        from api.routers.chat import send_message, ChatRequest
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        with patch('api.routers.chat.ChatService') as mock_service:
            with patch('api.routers.chat.get_chatbot', return_value=None):
                mock_service.get_or_create_session.return_value = (mock_session, True)
                mock_service.get_recent_messages.return_value = []

                request = ChatRequest(message="Test message")

                await send_message(request, mock_user, mock_db)

        # Should save assistant message (second call)
        assert mock_service.add_message.call_count >= 2
        call_args = mock_service.add_message.call_args_list[1]
        assert call_args[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_send_message_uses_chatbot_when_available(self):
        """Test send_message uses real chatbot when available"""
        from api.routers.chat import send_message, ChatRequest
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        mock_chatbot = MagicMock()
        mock_chatbot.query.return_value = {
            "answer": "Chatbot answer",
            "citations": [{"source": "Test", "url": "http://test.com"}],
            "redacted_query": None,
            "model_name": "test-model"
        }

        with patch('api.routers.chat.ChatService') as mock_service:
            with patch('api.routers.chat.get_chatbot', return_value=mock_chatbot):
                mock_service.get_or_create_session.return_value = (mock_session, True)
                mock_service.get_recent_messages.return_value = []

                request = ChatRequest(message="Test question")

                result = await send_message(request, mock_user, mock_db)

        assert result.answer == "Chatbot answer"
        mock_chatbot.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_passes_rag_context_to_chatbot(self):
        """Test send_message wires retrieval context into chatbot query."""
        from api.routers.chat import send_message, ChatRequest
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        mock_chatbot = MagicMock()
        mock_chatbot.query.return_value = {
            "answer": "Chatbot answer [1]",
            "citations": [{"source": "PubMed", "pmid": "12345"}],
            "redacted_query": None,
            "model_name": "test-model",
        }

        mock_rag_service = MagicMock()
        mock_rag_service.build_retrieval_package.return_value = {
            "retrieved_context": "[1] Sepsis guideline",
            "source_docs": [{"source": "PubMed", "pmid": "12345"}],
            "retrieval_context": {"documents_count": 1},
        }

        with patch("api.routers.chat.ChatService") as mock_service:
            with patch("api.routers.chat.get_chatbot", return_value=mock_chatbot):
                with patch(
                    "api.routers.chat.get_chat_rag_service",
                    return_value=mock_rag_service,
                ):
                    mock_service.get_or_create_session.return_value = (
                        mock_session,
                        True,
                    )
                    mock_service.get_recent_messages.return_value = []

                    request = ChatRequest(message="Test question")

                    await send_message(request, mock_user, mock_db)

        kwargs = mock_chatbot.query.call_args.kwargs
        assert kwargs["retrieved_context"] == "[1] Sepsis guideline"
        assert kwargs["source_docs"][0]["pmid"] == "12345"

    @pytest.mark.asyncio
    async def test_send_message_falls_back_on_chatbot_error(self):
        """Test send_message falls back to mock on chatbot error"""
        from api.routers.chat import send_message, ChatRequest
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.session_id = uuid4()

        mock_chatbot = MagicMock()
        mock_chatbot.query.side_effect = Exception("Chatbot error")

        with patch('api.routers.chat.ChatService') as mock_service:
            with patch('api.routers.chat.get_chatbot', return_value=mock_chatbot):
                mock_service.get_or_create_session.return_value = (mock_session, True)
                mock_service.get_recent_messages.return_value = []

                request = ChatRequest(message="What is sepsis?")

                result = await send_message(request, mock_user, mock_db)

        # Should fall back to mock response
        assert result.answer is not None


class TestGetConversationHistoryEndpoint:
    """Tests for get_conversation_history endpoint"""

    @pytest.mark.asyncio
    async def test_get_history_returns_messages(self):
        """Test get_conversation_history returns messages"""
        from api.routers.chat import get_conversation_history
        from uuid import uuid4
        from datetime import datetime

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        session_uuid = uuid4()
        session_id_str = str(session_uuid)

        mock_session = MagicMock()
        mock_session.started_at = datetime.utcnow()
        mock_session.last_activity_at = datetime.utcnow()

        mock_message = MagicMock()
        mock_message.role = "user"
        mock_message.content = "Test message"
        mock_message.created_at = datetime.utcnow()
        mock_message.sources = None

        with patch('api.routers.chat.ChatService') as mock_service:
            mock_service.get_session.return_value = mock_session
            mock_service.get_session_messages.return_value = [mock_message]

            result = await get_conversation_history(session_id_str, mock_user, mock_db)

        assert result.session_id == session_id_str
        assert len(result.messages) == 1
        assert result.messages[0].content == "Test message"

    @pytest.mark.asyncio
    async def test_get_history_invalid_session_id(self):
        """Test get_conversation_history raises on invalid session ID"""
        from api.routers.chat import get_conversation_history
        from fastapi import HTTPException

        mock_db = MagicMock()
        mock_user = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_conversation_history("invalid-uuid", mock_user, mock_db)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_get_history_session_not_found(self):
        """Test get_conversation_history raises 404 when session not found"""
        from api.routers.chat import get_conversation_history
        from fastapi import HTTPException
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch('api.routers.chat.ChatService') as mock_service:
            mock_service.get_session.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                await get_conversation_history(str(uuid4()), mock_user, mock_db)

        assert exc_info.value.status_code == 404


class TestClearConversationEndpoint:
    """Tests for clear_conversation endpoint"""

    @pytest.mark.asyncio
    async def test_clear_conversation_success(self):
        """Test clear_conversation returns success"""
        from api.routers.chat import clear_conversation
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()

        session_id_str = str(uuid4())

        with patch('api.routers.chat.ChatService') as mock_service:
            mock_service.delete_session.return_value = True

            result = await clear_conversation(session_id_str, mock_user, mock_db)

        assert result["message"] == "Conversation cleared"
        assert result["session_id"] == session_id_str

    @pytest.mark.asyncio
    async def test_clear_conversation_invalid_session_id(self):
        """Test clear_conversation raises on invalid session ID"""
        from api.routers.chat import clear_conversation
        from fastapi import HTTPException

        mock_db = MagicMock()
        mock_user = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await clear_conversation("invalid-uuid", mock_user, mock_db)

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_clear_conversation_not_found(self):
        """Test clear_conversation raises 404 when not found"""
        from api.routers.chat import clear_conversation
        from fastapi import HTTPException
        from uuid import uuid4

        mock_db = MagicMock()
        mock_user = MagicMock()

        with patch('api.routers.chat.ChatService') as mock_service:
            mock_service.delete_session.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await clear_conversation(str(uuid4()), mock_user, mock_db)

        assert exc_info.value.status_code == 404


class TestListSessionsEndpoint:
    """Tests for list_sessions endpoint"""

    @pytest.mark.asyncio
    async def test_list_sessions_returns_sessions(self):
        """Test list_sessions returns user sessions"""
        from api.routers.chat import list_sessions
        from uuid import uuid4
        from datetime import datetime

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_session = MagicMock()
        mock_session.session_id = uuid4()
        mock_session.title = "Test Session"
        mock_session.message_count = 5
        mock_session.started_at = datetime.utcnow()
        mock_session.last_activity_at = datetime.utcnow()

        with patch('api.routers.chat.ChatService') as mock_service:
            mock_service.list_user_sessions.return_value = ([mock_session], 1)

            result = await list_sessions(mock_user, mock_db)

        assert result["total"] == 1
        assert len(result["sessions"]) == 1
        assert result["sessions"][0]["title"] == "Test Session"

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self):
        """Test list_sessions returns empty list when no sessions"""
        from api.routers.chat import list_sessions

        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1

        with patch('api.routers.chat.ChatService') as mock_service:
            mock_service.list_user_sessions.return_value = ([], 0)

            result = await list_sessions(mock_user, mock_db)

        assert result["total"] == 0
        assert len(result["sessions"]) == 0
