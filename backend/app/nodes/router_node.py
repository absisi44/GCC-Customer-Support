# ======================================================
# Day 2 Router Node
# ======================================================
from typing import Literal
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from app.states.support_state import SupportState
# pyrefly: ignore [missing-import]
from app.llms.llm_provider import get_llm


class RouteDecision(BaseModel):
    target: Literal["shipping", "billing", "policy", "technical", "human_handoff"] = Field(
        description="المسار المناسب لمعالجة طلب العميل"
    )
    reason: str = Field(
        description="سبب اختيار هذا المسار باختصار"
    )


async def router_node(state: SupportState) -> dict:
    """
    Classifies the user's intent and routes to the appropriate specialist agent.
    Combines Day 2 routing (shipping, billing, technical, human_handoff)
    with Day 3 knowledge base (policy/FAQ).
    """
    system_prompt = (
        "أنت وكيل التوجيه الذكي (Router Agent) لمتجر إلكتروني يخدم عملاء منطقة الخليج.\n"
        "مهمتك الوحيدة هي تصنيف رسالة العميل إلى أحد المسارات التالية بدقة:\n"
        "- shipping: الاستفسار عن حالة طلب محدد، تتبع شحنة، تأخر الشحن، أو أرقام التتبع.\n"
        "- billing: مشاكل الدفع، خصم المبلغ مرتين، فواتير الشراء، طلب استرجاع المبالغ.\n"
        "- policy: الأسئلة العامة عن سياسات المتجر، شروط الإرجاع والاستبدال، رسوم الشحن العامة، والأسئلة الشائعة.\n"
        "- technical: مشاكل الحساب، تسجيل الدخول، وأعطال الموقع أو التطبيق.\n"
        "- human_handoff: الشكاوى الحادة أو الحالات المعقدة أو طلب التحدث مع موظف بشري مباشرة.\n\n"
        "قواعد هامة:\n"
        "1. لا تحاول حل المشكلة بنفسك.\n"
        "2. فقط قم بتصنيف الطلب وتحديد المسار المناسب مع ذكر السبب."
    )

    llm = get_llm(temperature=0)
    router_llm = llm.with_structured_output(RouteDecision)

    decision: RouteDecision = await router_llm.ainvoke([
        {"role": "system", "content": system_prompt},
        *state["messages"]
    ])

    print(f"🧭 [Router Decision] -> Target: '{decision.target}' | Reason: {decision.reason}")

    complaint = state.get("complaint", {}) or {}
    return {
        "active_agent": decision.target,
        "complaint": {
            **complaint,
            "category": decision.target
        }
    }


def route_from_router(state: SupportState) -> str:
    """Determine next node based on active_agent set by router_node."""
    return state.get("active_agent", "human_handoff")
