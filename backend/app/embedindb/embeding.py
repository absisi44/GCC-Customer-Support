# ==================================================
# This file is to get OpenAI embeddings and Chroma vectorstore 
# ==================================================

import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()


class GetEmbeddings:
    """Class to manage OpenAI embeddings and Chroma vectorstore."""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
    ):
        load_dotenv()
        self.model_name = model_name
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self._embeddings: Optional[OpenAIEmbeddings] = None

    def get_embeddings(self) -> OpenAIEmbeddings:
        """Initialize and return the OpenAIEmbeddings model."""
        try:
            if self._embeddings is None:
                api_key = self.api_key or os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError(
                        "OPENAI_API_KEY is not set. Please add it to your .env file or Railway variables."
                    )
                self.api_key = api_key.strip().splitlines()[0].strip()
                self._embeddings = OpenAIEmbeddings(
                    model=self.model_name,
                    api_key=self.api_key,
                )
            return self._embeddings
        except Exception as e:
            raise ValueError(f"Error initializing OpenAI embeddings ({self.model_name}): {e}")

    def create_vectorstore(
        self,
        documents: List[Document],
        collection_name: str = "scit_support_kb_day3",
        persist_directory: Optional[str] = None,
    ) -> Chroma:
        """Create a Chroma vectorstore from documents with persistence."""
        try:
            db_dir = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
            os.makedirs(db_dir, exist_ok=True)

            embeddings = self.get_embeddings()
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=db_dir,
            )
            return vectorstore
        except Exception as e:
            raise ValueError(f"Error creating Chroma vectorstore: {e}")

    def get_vectorstore(
        self,
        collection_name: str = "scit_support_kb_day3",
        persist_directory: Optional[str] = None,
    ) -> Chroma:
        """Load an existing Chroma vectorstore collection."""
        try:
            db_dir = persist_directory or os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
            embeddings = self.get_embeddings()
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=db_dir,
            )
            return vectorstore
        except Exception as e:
            raise ValueError(f"Error loading Chroma vectorstore: {e}")
