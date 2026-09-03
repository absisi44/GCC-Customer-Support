# ==================================================
# Unified Course State (Day 1, Day 2 & Day 3)
# ==================================================

from typing import Annotated, Optional, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class CustomerContext(TypedDict):
    customer_id: str
    account_tier: str
    open_ticket_id: Optional[str]


class ComplaintContext(TypedDict):
    category: Optional[str]
    sentiment: Optional[str]
    resolution_status: str


class SupportState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    customer: CustomerContext
    complaint: ComplaintContext
    active_agent: Optional[str]
