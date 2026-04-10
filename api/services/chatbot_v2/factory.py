"""Factory helpers for chatbot v2."""

from .chatbot import ProductionMedicalChatbotV2
from .retrieval import ChatbotV2Retrieval


def create_chatbot_v2(**kwargs) -> ProductionMedicalChatbotV2:
    """Create the chatbot v2 wrapper."""
    return ProductionMedicalChatbotV2(**kwargs)


def create_retrieval_v2(**kwargs) -> ChatbotV2Retrieval:
    """Create the retrieval layer used by chatbot v2."""
    return ChatbotV2Retrieval(**kwargs)
