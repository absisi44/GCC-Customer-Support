# ======================================================
# General / Fallback Specialist Nodes
# ======================================================
from langchain_core.messages import AIMessage

# pyrefly: ignore [missing-import]
from app.states.support_state import SupportState


async def technical_node(state: SupportState) -> dict:
    """Handles technical issues and app/website inquiries."""
    return {
        "messages": [
            AIMessage(
                content="تم استلام بلاغك التقني وتحويله إلى الفريق الفني المختص لمعالجة المشكلة أو العطل في أسرع وقت. شكراً لصبرك."
            )
        ],
        "active_agent": "technical"
    }


async def human_handoff_node(state: SupportState) -> dict:
    """Transfers the ticket to a human representative for complex or escalations."""
    customer_id = state.get("customer", {}).get("customer_id", "العميل")
    return {
        "messages": [
            AIMessage(
                content="تم تحويل المحادثة إلى ممثل خدمة العملاء البشري وسيكون معك خلال لحظات لمساعدتك بشكل مباشر. تم حفظ جميع تفاصيل طلبك."
            )
        ],
        "active_agent": "human_handoff"
    }
