# ==================================================
# Day 3 RAG Knowledge Node & Functions
# Identical naming and logic to Day3 notebook
# ==================================================

import os
from typing import List, Tuple, Any
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# pyrefly: ignore [missing-import]
from app.states.support_state import SupportState
# pyrefly: ignore [missing-import]
from app.embedindb.embeding import GetEmbeddings
# pyrefly: ignore [missing-import]
from app.llms.groqllm import GetGroqLLM


def get_llm():
    """Get Groq LLM if GROQ_API_KEY is configured, else fallback to OpenAI."""
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            return GetGroqLLM().get_groq_llm()
        except Exception:
            pass

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        return ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_key)

    raise ValueError("Neither GROQ_API_KEY nor OPENAI_API_KEY was found in environment variables.")


# --------------------------------------------------
# Exact functions from Day 3 Notebook:
# 1. retrieve(query, k=4)
# 2. build_context(docs)
# 3. answer_question(query, k=4)
# --------------------------------------------------

def retrieve(query: str, k: int = 4) -> List[Document]:
    """Retrieve top-k relevant documents from the vectorstore."""
    embed_manager = GetEmbeddings()
    vectorstore = embed_manager.get_vectorstore()
    return vectorstore.similarity_search(query, k=k)


def build_context(docs: List[Document]) -> str:
    """Format retrieved chunks with their source identifiers."""
    return "\n\n".join(
        f"[Source: {doc.metadata.get('source_id')}]\n{doc.page_content}"
        for doc in docs
    )


def answer_question(query: str, k: int = 4) -> Tuple[AIMessage, List[Document]]:
    """Grounded RAG generation strictly using retrieved company context."""
    docs = retrieve(query, k=k)
    context = build_context(docs)

    system_prompt = f"""You are a customer support assistant for a GCC e-commerce store.

Answer the customer's question using only the retrieved company knowledge below.

Rules:
- Do not invent policy details.
- If the answer is not supported by the context, say that the available knowledge does not provide the answer.
- Keep the answer clear and direct.
- Use the same language as the customer.
- Mention important limits, fees, time windows or conditions when they are present.

Retrieved company knowledge:
{context}
"""

    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query),
    ])

    # Clean <think> tags if model is a reasoning model (e.g. Qwen / DeepSeek)
    if hasattr(response, "content") and isinstance(response.content, str):
        import re
        cleaned_content = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
        response = AIMessage(content=cleaned_content)

    return response, docs


# --------------------------------------------------
# LangGraph Node matching Course Architecture
# --------------------------------------------------

def rag_node(state: SupportState) -> dict:
    """RAG Knowledge Node for customer policy & FAQ inquiries."""
    last_message = state["messages"][-1]
    query = last_message.content if hasattr(last_message, "content") else str(last_message)
    response, docs = answer_question(query, k=4)

    return {
        "messages": [response],
        "active_agent": "rag",
    }
