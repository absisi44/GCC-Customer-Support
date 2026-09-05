# ==================================================
# Knowledge Base Ingestion for RAG
# Loads company_policies.md & faqs.json into Chroma
# ==================================================

import json
import os
from pathlib import Path
from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# pyrefly: ignore [missing-import]
from app.embedindb.embeding import GetEmbeddings


def load_and_chunk_documents(data_dir: Optional[Path] = None) -> List[Document]:
    """Load and chunk company policies and FAQs into Document objects."""
    if data_dir is None:
        env_data_dir = os.getenv("DATA_DIR")
        cwd = Path.cwd()
        possible_dirs = [
            Path(env_data_dir) if env_data_dir else None,
            cwd / "data",
            cwd.parent / "data",
            Path(__file__).resolve().parents[3] / "data",
            Path(__file__).resolve().parents[2] / "data",
            Path("/app/data"),
        ]
        data_dir = next((d for d in possible_dirs if d and d.exists()), cwd / "data")

    policy_path = data_dir / "company_policies.md"
    faq_path = data_dir / "faqs.json"

    if not policy_path.exists():
        raise FileNotFoundError(f"Policy file not found at: {policy_path}")
    if not faq_path.exists():
        raise FileNotFoundError(f"FAQs file not found at: {faq_path}")

    # 1. Chunk Policy Markdown
    policy_text = policy_path.read_text(encoding="utf-8")
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    policy_docs = header_splitter.split_text(policy_text)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""],
    )
    policy_chunks = text_splitter.split_documents(policy_docs)

    for doc in policy_chunks:
        doc.metadata.update({
            "source_id": "COMPANY_POLICY",
            "source_type": "policy",
            "region": "GCC",
            "version": "1.0.0",
            "updated_at": "2026-08-01",
        })

    # 2. Chunk FAQs
    with open(faq_path, "r", encoding="utf-8") as f:
        faqs = json.load(f)

    faq_docs: List[Document] = []
    for faq in faqs:
        metadata_dict = faq.get("metadata", {})
        target_country = faq.get("country") or metadata_dict.get("target_country", "GCC")
        updated_at = faq.get("updated_at") or metadata_dict.get("updated_at", "2026-08-01")

        faq_docs.append(
            Document(
                page_content=(
                    f"Question: {faq['question']}\n"
                    f"Answer: {faq['answer']}\n"
                    f"Keywords: {', '.join(faq.get('keywords', []))}"
                ),
                metadata={
                    "source_id": faq["id"],
                    "source_type": "faq",
                    "category": faq.get("category", "general"),
                    "target_country": target_country,
                    "updated_at": updated_at,
                },
            )
        )

    all_docs = policy_chunks + faq_docs
    return all_docs


def ingest_knowledge_base(collection_name: str = "scit_support_kb_day3"):
    """Ingest documents into the Chroma vectorstore."""
    docs = load_and_chunk_documents()
    embed_manager = GetEmbeddings()
    vectorstore = embed_manager.create_vectorstore(
        documents=docs,
        collection_name=collection_name,
    )
    return vectorstore
