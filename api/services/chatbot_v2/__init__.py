"""Chatbot V2 package."""

__all__ = [
    "ChatbotV2Retrieval",
    "ProductionMedicalChatbotV2",
    "create_chatbot_v2",
    "create_retrieval_v2",
]


def __getattr__(name):
    if name == "ChatbotV2Retrieval":
        from .retrieval import ChatbotV2Retrieval

        return ChatbotV2Retrieval
    if name == "ProductionMedicalChatbotV2":
        from .chatbot import ProductionMedicalChatbotV2

        return ProductionMedicalChatbotV2
    if name == "create_chatbot_v2":
        from .factory import create_chatbot_v2

        return create_chatbot_v2
    if name == "create_retrieval_v2":
        from .factory import create_retrieval_v2

        return create_retrieval_v2
    raise AttributeError(name)
