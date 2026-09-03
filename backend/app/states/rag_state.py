# ==================================================
# State definition for the RAG Customer Support Agent
# ==================================================

from typing import List, Optional
from typing_extensions import TypedDict
from langchain_core.documents import Document


class RAGState(TypedDict):
    """State schema for RAG pipeline."""
    query: str
    documents: List[Document]
    answer: str
    sources: List[str]
