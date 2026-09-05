# ======================================================
# Full Multi-Agent Customer Support Graph (Day 1 + Day 2 + Day 3)
# ======================================================

import os
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

# pyrefly: ignore [missing-import]
from app.states.support_state import SupportState
# pyrefly: ignore [missing-import]
from app.nodes import (
    rag_node,
    router_node,
    route_from_router,
    shipping_executor_node,
    shipping_tool_node,
    route_after_shipping,
    billing_executor_node,
    billing_tool_node,
    route_after_billing,
    technical_node,
    human_handoff_node,
)
# pyrefly: ignore [missing-import]
from app.embedindb.embeding import GetEmbeddings
# pyrefly: ignore [missing-import]
from app.embedindb.ingest import ingest_knowledge_base


_checkpointer: Optional[Any] = None
_postgres_pool: Optional[Any] = None


def get_checkpointer() -> Any:
    """
    Returns an in-memory state checkpointer for non-blocking, reliable state persistence.
    MemorySaver natively supports async ainvoke() across all nodes and sessions without external DB dependency.
    """
    global _checkpointer
    if _checkpointer is None:
        _checkpointer = MemorySaver()
        print("ℹ️ Using in-memory MemorySaver checkpointer for state persistence.")
    return _checkpointer


def build_support_graph(checkpointer: Optional[Any] = None):
    """
    Builds and compiles the complete multi-agent graph:
    1. router: Classifies user intent and sets active_agent & complaint category.
    2. shipping_executor + tool: Handles order status, tracking, and carrier details.
    3. billing_executor + billing_tool: Handles invoices, payments, and double charge queries.
    4. rag_node: Answers company policies, return rules, and FAQs via ChromaDB vectorstore.
    5. technical: Handles system, login, and application issues.
    6. human_handoff: Gracefully handles complex complaints and human agent requests.
    """
    builder = StateGraph(SupportState)

    # 1. Add All Specialist Nodes
    builder.add_node("router", router_node)
    builder.add_node("shipping_executor", shipping_executor_node)
    builder.add_node("tool", shipping_tool_node)
    builder.add_node("billing_executor", billing_executor_node)
    builder.add_node("billing_tool", billing_tool_node)
    builder.add_node("rag_node", rag_node)
    builder.add_node("technical", technical_node)
    builder.add_node("human_handoff", human_handoff_node)

    # 2. Flow from START to Router
    builder.add_edge(START, "router")

    # 3. Conditional routing based on router decision
    builder.add_conditional_edges(
        "router",
        route_from_router,
        {
            "shipping": "shipping_executor",
            "billing": "billing_executor",
            "policy": "rag_node",
            "technical": "technical",
            "human_handoff": "human_handoff",
        }
    )

    # 4. Shipping Agent Tool Loop (Day 2)
    builder.add_conditional_edges(
        "shipping_executor",
        route_after_shipping,
        {
            "tool": "tool",
            "end": END,
        }
    )
    builder.add_edge("tool", "shipping_executor")

    # 5. Billing Agent Tool Loop (Day 2 Exercise)
    builder.add_conditional_edges(
        "billing_executor",
        route_after_billing,
        {
            "tool": "billing_tool",
            "end": END,
        }
    )
    builder.add_edge("billing_tool", "billing_executor")

    # 6. Direct End Edges for terminal nodes
    builder.add_edge("rag_node", END)
    builder.add_edge("technical", END)
    builder.add_edge("human_handoff", END)

    # 7. Checkpointer Configuration
    if checkpointer is None:
        checkpointer = get_checkpointer()

    return builder.compile(checkpointer=checkpointer)


# Compiled singleton graph
support_graph = build_support_graph()


def ensure_knowledge_base_ready(collection_name: str = "scit_support_kb_day3"):
    """Ensure vectorstore collection exists and has documents."""
    embed_manager = GetEmbeddings()
    try:
        vectorstore = embed_manager.get_vectorstore(collection_name=collection_name)
        count = vectorstore._collection.count()
        if count == 0:
            print("Vectorstore is empty. Ingesting knowledge base...")
            ingest_knowledge_base(collection_name=collection_name)
    except Exception:
        print("Initializing and ingesting knowledge base...")
        ingest_knowledge_base(collection_name=collection_name)


async def run_support_pipeline(
    query: str,
    customer_id: str = "CUST-1001",
    account_tier: str = "standard",
    thread_id: str = "customer-session-1001",
    open_ticket_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the full Multi-Agent pipeline asynchronously with state persistence.
    """
    ensure_knowledge_base_ready()

    config = {"configurable": {"thread_id": thread_id}}
    initial_state: SupportState = {
        "messages": [HumanMessage(content=query)],
        "customer": {
            "customer_id": customer_id,
            "account_tier": account_tier,
            "open_ticket_id": open_ticket_id,
        },
        "complaint": {
            "category": None,
            "sentiment": None,
            "resolution_status": "open",
        },
        "active_agent": "",
    }

    result = await support_graph.ainvoke(initial_state, config=config)
    last_message = result["messages"][-1]
    answer_text = last_message.content if hasattr(last_message, "content") else str(last_message)
    if isinstance(answer_text, str):
        import re
        answer_text = re.sub(r"<think>.*?</think>", "", answer_text, flags=re.DOTALL).strip()

    return {
        "query": query,
        "answer": answer_text,
        "active_agent": result.get("active_agent", ""),
        "customer": result.get("customer"),
        "complaint": result.get("complaint"),
        "messages_count": len(result.get("messages", [])),
        "state": result,
    }


# Backwards compatibility aliases
rag_graph = support_graph
build_rag_graph = build_support_graph
run_rag_pipeline = run_support_pipeline
