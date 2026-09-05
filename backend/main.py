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
from fastapi.staticfiles import StaticFiles
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


import asyncio


@app.on_event("startup")
async def startup_event():
    """Ensure vectorstore is seeded on application startup in background."""
    async def _safe_seed_kb():
        try:
            await asyncio.to_thread(ensure_knowledge_base_ready)
        except Exception as e:
            print(f"⚠️ Knowledge base initialization notice: {e}")

    asyncio.create_task(_safe_seed_kb())


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint for Railway and container monitoring."""
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e) or type(e).__name__)


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


# ======================================================
# Mount Frontend Static Files (Option A: Single-service)
# Mounted after API routes so /chat, /ingest, /health, /docs take precedence
# ======================================================
frontend_candidates = [
    os.path.join(current_dir, "..", "frontend"),
    os.path.join(os.getcwd(), "frontend"),
    os.path.join(os.getcwd(), "..", "frontend"),
    "/app/frontend",
]
frontend_dir = next((d for d in frontend_candidates if os.path.isdir(d)), None)

if frontend_dir:
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    print(f"✅ Mounted frontend static files from: {frontend_dir}")
else:
    print("⚠️ Frontend directory not found; serving API mode only.")

    @app.get("/", tags=["Health"])
    def root_fallback():
        return health_check()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
