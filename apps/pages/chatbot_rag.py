"""
AI Chatbot Page with RAG Integration
Professional Medical AI Assistant with retrieval-augmented generation
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.core.vector_store import VectorStore
from api.services.document_processor import MedicalDocumentProcessor
from api.services.embedding_service import MedicalEmbeddingService
from api.services.rag_pipeline import RAGPipeline
from api.services.safety_guardrails import SafetyGuardrails

# Import prompt enhancer
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.prompt_enhancer import PromptEnhancer


@st.cache_resource
def initialize_rag_system():
    """Initialize RAG system (cached for performance)"""
    try:
        # Initialize components
        vector_store = VectorStore()
        embedding_service = MedicalEmbeddingService(provider="sentence-transformers")
        safety = SafetyGuardrails()

        # Try to initialize RAG pipeline (may not have LLM key)
        try:
            llm_provider = os.getenv("LLM_PRIMARY_PROVIDER", "groq")
            # Check for API keys in order: Groq, DeepSeek, OpenAI, Anthropic
            llm_api_key = (
                os.getenv("GROQ_API_KEY")
                or os.getenv("DEEPSEEK_API_KEY")
                or os.getenv("OPENAI_API_KEY")
                or os.getenv("ANTHROPIC_API_KEY")
            )

            if llm_api_key:
                rag_pipeline = RAGPipeline(
                    vector_store=vector_store,
                    embedding_service=embedding_service,
                    llm_provider=llm_provider,
                )
            else:
                # Create a retrieval-only version
                rag_pipeline = RetrievalOnlyPipeline(
                    vector_store=vector_store,
                    embedding_service=embedding_service,
                )
        except Exception as llm_error:
            # Fallback to retrieval-only
            rag_pipeline = RetrievalOnlyPipeline(
                vector_store=vector_store,
                embedding_service=embedding_service,
            )

        return rag_pipeline, safety, None

    except Exception as e:
        return None, None, str(e)


class RetrievalOnlyPipeline:
    """Retrieval-only pipeline when LLM is not available"""

    def __init__(self, vector_store, embedding_service):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.document_processor = MedicalDocumentProcessor()

    def retrieve(self, query, top_k=5, category=None, use_hybrid=True, use_query_expansion=True):
        """Retrieve relevant documents"""
        # Generate query embedding
        if use_query_expansion:
            query_embeddings = self.embedding_service.embed_with_expansion(query)
            query_embedding = query_embeddings[0]
        else:
            query_embedding = self.embedding_service.embed(query)

        # Retrieve documents
        if use_hybrid:
            documents = self.vector_store.hybrid_search(
                query_embedding=query_embedding,
                query_text=query,
                top_k=top_k,
                category=category,
                semantic_weight=0.7,
            )
        else:
            documents = self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                category=category,
                min_similarity=0.5,
            )

        return documents

    def query(self, question, top_k=5, category=None, include_citations=True):
        """Query with retrieval only (no generation)"""
        docs = self.retrieve(question, top_k, category, use_hybrid=True)

        if not docs:
            return {
                "answer": "❌ **No LLM API Key Configured**\n\nI found no relevant documents in my knowledge base.\n\n**To enable AI-powered answers:**\n\n1. **Get Groq API key:** https://console.groq.com/ (Recommended - Free tier: 30 req/min)\n2. Add to `.env.chatbot`: `GROQ_API_KEY=your_key_here`\n3. Restart app\n\n**Alternative providers:**\n- DeepSeek: https://platform.deepseek.com/\n- OpenAI: https://platform.openai.com/\n\n**Note:** You can still see retrieved medical documents below.",
                "citations": [],
                "confidence": 0.0,
                "num_sources": 0,
            }

        # Build answer from retrieved documents
        answer = "📚 **Retrieved Medical Knowledge** (Retrieval-Only Mode)\n\n"
        answer += "⚠️ *No LLM API key configured. Showing raw retrieved documents.*\n\n"
        answer += "---\n\n"

        for idx, doc in enumerate(docs[:3], 1):
            answer += f"### [{idx}] {doc['source']}\n\n"
            answer += f"**Category:** {doc['category'].title()}\n\n"
            answer += f"**Relevance Score:** {doc.get('hybrid_score', doc.get('similarity', 0)):.2%}\n\n"

            # Show preview
            content = doc['content']
            if len(content) > 500:
                content = content[:500] + "..."
            answer += f"{content}\n\n"
            answer += "---\n\n"

        answer += "\n\n**💡 To enable AI-powered answers:**\n"
        answer += "1. Get **Groq API key**: https://console.groq.com/ (Free: 30 req/min)\n"
        answer += "2. Add to `.env.chatbot`: `GROQ_API_KEY=your_key_here`\n"
        answer += "3. Restart app\n"

        citations = [
            {
                "id": idx,
                "source": doc["source"],
                "category": doc["category"],
                "similarity": doc.get("hybrid_score", doc.get("similarity", 0)),
            }
            for idx, doc in enumerate(docs, 1)
        ]

        return {
            "answer": answer,
            "citations": citations,
            "confidence": sum(c["similarity"] for c in citations) / len(citations) if citations else 0,
            "num_sources": len(docs),
        }

    def get_stats(self):
        """Get system stats"""
        total_docs = self.vector_store.get_document_count()
        categories = ["drug", "disease", "guideline", "protocol", "general"]
        category_counts = {}
        for cat in categories:
            category_counts[cat] = self.vector_store.get_document_count(category=cat)

        return {
            "total_documents": total_docs,
            "by_category": category_counts,
            "embedding_dimension": self.embedding_service.get_embedding_dimension(),
            "llm_provider": "None (Retrieval-Only)",
            "llm_model": "N/A - Add API key to enable",
        }


def show_chatbot():
    """Show AI Chatbot page with RAG"""

    st.markdown(
        '<div class="main-header">🤖 AI Medical Assistant (RAG-Powered)</div>',
        unsafe_allow_html=True,
    )

    # Initialize RAG system
    rag_pipeline, safety, error = initialize_rag_system()

    if error:
        st.error(
            f"""
        **RAG System Initialization Error**

        Failed to initialize the RAG system: {error}

        **Troubleshooting:**
        1. Ensure PostgreSQL is running
        2. Run initialization script: `python scripts/initialize_rag_system.py`
        3. Check DATABASE_URL in .env file
        4. Verify pgvector extension is installed

        **Falling back to basic chatbot mode.**
        """
        )
        # Fall back to basic mode (import original chatbot)
        from .chatbot import show_chatbot as show_basic_chatbot

        show_basic_chatbot()
        return

    # Initialize session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "rag_enabled" not in st.session_state:
        st.session_state.rag_enabled = True

    # Page header
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("### 💬 Chat with Medical AI Assistant")
        st.markdown(
            "Powered by **RAG** (Retrieval-Augmented Generation) with medical knowledge base."
        )

    with col2:
        # RAG toggle
        rag_enabled = st.checkbox(
            "🔍 RAG Mode", value=st.session_state.rag_enabled, key="rag_toggle"
        )
        st.session_state.rag_enabled = rag_enabled

    with col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    st.markdown("---")

    # Sidebar with RAG stats and templates
    with st.sidebar:
        st.markdown("### 📊 RAG System Status")

        if rag_pipeline:
            try:
                stats = rag_pipeline.get_stats()
                st.success("✅ Online")
                st.metric("Knowledge Base", f"{stats['total_documents']} docs")
                st.metric("Embedding Dim", stats["embedding_dimension"])
                st.metric("LLM Provider", stats["llm_provider"].upper())

                # Category breakdown
                with st.expander("📚 Knowledge Categories"):
                    for category, count in stats["by_category"].items():
                        if count > 0:
                            st.write(f"- **{category.title()}**: {count}")

            except Exception as e:
                st.warning(f"Stats unavailable: {e}")
        else:
            st.error("❌ Offline")

        st.markdown("---")
        st.markdown("### 📋 Quick Templates")

        templates = {
            "🔬 Sepsis Assessment": "What are the current guidelines for diagnosing and treating sepsis in ICU patients?",
            "💔 Mortality Risk": "What factors increase mortality risk in ICU patients? How should we assess and communicate prognosis?",
            "📊 SOFA Score": "Explain the SOFA score components and how to interpret them for organ dysfunction assessment.",
            "💊 Vasopressor Guide": "What are the indications, dosing, and monitoring for norepinephrine in septic shock?",
            "🧪 Lab Interpretation": "What are critical lab values that indicate urgent intervention in ICU patients?",
            "⚠️ Emergency Signs": "What vital signs or symptoms indicate a medical emergency requiring immediate intervention?",
        }

        for template_name, template_text in templates.items():
            if st.button(template_name, use_container_width=True, key=template_name):
                st.session_state.chat_messages.append(
                    {"role": "user", "content": template_text}
                )
                # Generate response using RAG
                response = generate_rag_response(
                    template_text, rag_pipeline, safety, rag_enabled
                )
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": response["answer"]}
                )
                st.rerun()

        st.markdown("---")
        st.markdown("### ℹ️ About RAG System")
        st.info(
            """
            **Features:**
            - Evidence-based responses
            - Source citations
            - Medical knowledge base
            - Safety guardrails
            - Emergency detection

            **Knowledge Sources:**
            - Clinical guidelines
            - Medical protocols
            - Drug information
            - Evidence-based medicine
            """
        )

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat messages
        for idx, message in enumerate(st.session_state.chat_messages):
            if message["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message["content"])

                    # Show citations if available
                    if "citations" in message and message["citations"]:
                        with st.expander("📚 Sources"):
                            for citation in message["citations"]:
                                st.write(
                                    f"**[{citation['id']}]** {citation['source']} "
                                    f"(Category: {citation['category']}, "
                                    f"Relevance: {citation['similarity']:.2%})"
                                )

                    # Show confidence if available
                    if "confidence" in message:
                        confidence = message["confidence"]
                        if confidence > 0:
                            color = (
                                "green"
                                if confidence > 0.7
                                else "orange" if confidence > 0.5 else "red"
                            )
                            st.markdown(
                                f"**Confidence:** <span style='color: {color};'>{confidence:.0%}</span>",
                                unsafe_allow_html=True,
                            )

        # Welcome message if no messages
        if len(st.session_state.chat_messages) == 0:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(
                    """
                    👋 **Welcome to MediAI RAG-Powered Assistant!**

                    I use **Retrieval-Augmented Generation (RAG)** to provide evidence-based medical guidance:

                    **How it works:**
                    1. 🔍 **Retrieval**: I search our medical knowledge base for relevant information
                    2. 🧠 **Generation**: I use an AI model to synthesize a clear, accurate answer
                    3. 📚 **Citations**: I provide sources so you can verify information

                    **I can help with:**
                    - Clinical interpretations and guidelines
                    - Risk assessments (sepsis, mortality)
                    - Medication information
                    - Lab value interpretation
                    - Treatment protocols

                    **Safety Features:**
                    - 🚨 Emergency detection
                    - ⚠️ Safety guardrails
                    - 📋 Medical disclaimers
                    - ✅ Source citations

                    ⚠️ **Important:** This is a demonstration tool for educational purposes. Always consult qualified healthcare professionals for clinical decisions.

                    Try a question or use the quick templates in the sidebar!
                    """
                )

    # Chat input
    st.markdown("---")

    # Prompt enhancement toggle in sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Prompt Settings")
        auto_enhance = st.toggle(
            "🚀 Auto-enhance prompts",
            value=st.session_state.get("auto_enhance_prompts", True),
            help="Automatically enhance short medical queries into detailed, structured prompts",
            key="auto_enhance_prompts"
        )

    # Custom chat input with enhancement indicator
    col_input, col_enhance = st.columns([5, 1])

    with col_input:
        user_input = st.chat_input("💬 Ask a medical question...")

    with col_enhance:
        # Show enhancement status indicator
        if st.session_state.get("auto_enhance_prompts", True):
            st.markdown(
                "<div style='margin-top: 8px; text-align: center;'>🚀</div>",
                unsafe_allow_html=True,
                help="Auto-enhancement enabled"
            )

    if user_input:
        # Store original query
        original_query = user_input

        # Auto-enhance if enabled
        if st.session_state.get("auto_enhance_prompts", True):
            enhanced_query, was_enhanced = PromptEnhancer.enhance_prompt(user_input)

            if was_enhanced:
                # Show enhancement notification
                with st.container():
                    st.info(f"🚀 **Prompt được tăng cường tự động**\n\n**Câu hỏi gốc:** {original_query}")
                    user_input = enhanced_query
            else:
                user_input = original_query

        # Continue with original flow
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})

        # Generate response using RAG
        response = generate_rag_response(
            user_input, rag_pipeline, safety, st.session_state.rag_enabled
        )

        # Add assistant message with metadata
        assistant_message = {
            "role": "assistant",
            "content": response["answer"],
            "citations": response.get("citations", []),
            "confidence": response.get("confidence", 0),
        }
        st.session_state.chat_messages.append(assistant_message)

        # Save to history
        _save_chat_history(user_input, response["answer"])

        st.rerun()

    # Export chat
    if len(st.session_state.chat_messages) > 0:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button("📥 Export Chat History", use_container_width=True):
                export_chat()


def generate_rag_response(
    user_input: str, rag_pipeline, safety: SafetyGuardrails, use_rag: bool = True
) -> dict:
    """
    Generate AI response using RAG pipeline with safety checks

    Args:
        user_input: User query
        rag_pipeline: RAG pipeline instance
        safety: Safety guardrails instance
        use_rag: Whether to use RAG (vs. basic mode)

    Returns:
        Response dictionary with answer, citations, confidence
    """
    # Safety check
    query_safety = safety.process_query(user_input)

    if not query_safety["is_safe"]:
        # Return safety response
        return {
            "answer": query_safety["special_response"],
            "citations": [],
            "confidence": 1.0,
        }

    if query_safety["is_emergency"]:
        # Return emergency response
        return {
            "answer": query_safety["special_response"],
            "citations": [],
            "confidence": 1.0,
        }

    # Generate response
    if use_rag and rag_pipeline:
        try:
            # Use RAG pipeline
            result = rag_pipeline.query(
                question=user_input, top_k=5, include_citations=True
            )

            # Process response through safety guardrails
            result["answer"] = safety.process_response(
                result["answer"], query_safety, is_demo=True
            )

            return result

        except Exception as e:
            # Fallback error response
            return {
                "answer": f"I encountered an error processing your query: {str(e)}\n\nPlease try rephrasing your question or contact support if the issue persists.",
                "citations": [],
                "confidence": 0.0,
            }
    else:
        # Basic mode (fallback)
        response = "RAG mode is disabled. This is a basic response mode.\n\nPlease enable RAG mode for evidence-based answers with source citations."
        response = safety.add_disclaimer(response, is_demo=True)

        return {"answer": response, "citations": [], "confidence": 0.0}


def _save_chat_history(question: str, answer: str):
    """Save chat interaction to history"""
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": st.session_state.get("user_id", "anonymous"),
        "question": question,
        "answer": answer,
    }

    st.session_state.chat_history.append(history_entry)

    # Save to file
    try:
        history_file = (
            Path(__file__).parent.parent / ".streamlit" / "chat_history.json"
        )
        history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(history_file, "w") as f:
            json.dump(st.session_state.chat_history[-100:], f, indent=2)
    except Exception:
        pass


def export_chat():
    """Export chat history"""
    chat_text = "# MediAI Chat History (RAG-Powered)\n\n"
    chat_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    chat_text += f"User: {st.session_state.get('user_id', 'anonymous')}\n\n"
    chat_text += "---\n\n"

    for idx, msg in enumerate(st.session_state.chat_messages, 1):
        role = "👤 User" if msg["role"] == "user" else "🤖 Assistant"
        chat_text += f"### {role} (Message {idx})\n\n"
        chat_text += f"{msg['content']}\n\n"

        # Add citations if available
        if msg.get("citations"):
            chat_text += "**Sources:**\n"
            for citation in msg["citations"]:
                chat_text += f"- [{citation['id']}] {citation['source']}\n"
            chat_text += "\n"

        chat_text += "---\n\n"

    st.download_button(
        label="📥 Download Chat (Markdown)",
        data=chat_text,
        file_name=f"mediai_rag_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown",
    )
