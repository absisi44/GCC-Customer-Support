# ======================================================
# GCC Customer Support AI Agent — FastAPI Application
# Combines Day 1 (State), Day 2 (Multi-Agent Tools), Day 3 (RAG)
# ======================================================

import os
import sys
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

load_dotenv()

# pyrefly: ignore [missing-import]
from app.graphs.graph import run_support_pipeline, ensure_knowledge_base_ready
# pyrefly: ignore [missing-import]
from app.embedindb.ingest import ingest_knowledge_base

app = FastAPI(
    title="GCC Customer Support AI Multi-Agent API",
    description="Multi-Agent Customer Support System featuring Router, Shipping Specialist with order tracking, Billing Specialist with invoice lookup, and RAG Knowledge Base for company policies & FAQs.",
    version="1.0.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., description="Customer message in Arabic or English", example="طلبي 5501 تأخر في التوصيل، وين وصل؟")
    customer_id: str = Field(default="CUST-1001", description="Unique Customer ID", example="CUST-1001")
    account_tier: str = Field(default="standard", description="Customer Tier (standard, VIP)", example="standard")
    thread_id: str = Field(default="customer-session-1001", description="Session thread ID for state persistence", example="customer-session-1001")
    open_ticket_id: Optional[str] = Field(default=None, description="Active ticket ID if applicable", example="TICKET-5501")


class ChatResponse(BaseModel):
    query: str
    answer: str
    active_agent: str
    customer: Optional[Dict[str, Any]] = None
    complaint: Optional[Dict[str, Any]] = None
    messages_count: int


@app.on_event("startup")
async def startup_event():
    """Ensure vectorstore is seeded on application startup."""
    try:
        ensure_knowledge_base_ready()
    except Exception as e:
        print(f"⚠️ Knowledge base startup warning: {e}")


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "GCC Customer Support AI Multi-Agent System",
        "supported_agents": [
            "router (Day 2)",
            "shipping_executor with lookup_order tool (Day 2)",
            "billing_executor with lookup_invoice tool (Day 2 Exercise)",
            "rag_node with ChromaDB Knowledge Base (Day 3)",
            "technical & human_handoff handlers"
        ]
    }


@app.post("/chat", response_model=ChatResponse, tags=["Agent Chat"])
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint to interact with the multi-agent customer support system.
    """
    try:
        result = await run_support_pipeline(
            query=request.message,
            customer_id=request.customer_id,
            account_tier=request.account_tier,
            thread_id=request.thread_id,
            open_ticket_id=request.open_ticket_id,
        )
        return ChatResponse(
            query=result["query"],
            answer=result["answer"],
            active_agent=result["active_agent"],
            customer=result.get("customer"),
            complaint=result.get("complaint"),
            messages_count=result.get("messages_count", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", tags=["Knowledge Base"])
def reindex_knowledge_base():
    """Trigger re-ingestion of markdown policies and JSON FAQs into ChromaDB."""
    try:
        collection_name = "scit_support_kb_day3"
        docs_count = ingest_knowledge_base(collection_name=collection_name)
        return {
            "success": True,
            "message": f"Successfully ingested {docs_count} document chunks into {collection_name}."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
