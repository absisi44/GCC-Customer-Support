# ======================================================
# Day 2 Shipping Specialist Agent & Tool Nodes
# ======================================================
from langchain_core.messages import ToolMessage

# pyrefly: ignore [missing-import]
from app.states.support_state import SupportState
# pyrefly: ignore [missing-import]
from app.tools.order_tool import lookup_order
# pyrefly: ignore [missing-import]
from app.llms.llm_provider import get_llm


async def shipping_executor_node(state: SupportState) -> dict:
    """
    Shipping support agent node that can call lookup_order tool to track orders.
    """
    system_prompt = (
        "أنت موظف خدمة العملاء المختص بالشحن والتوصيل (Shipping Support Agent) لمتجر إلكتروني خليجي.\n"
        "مهمتك:\n"
        "1. مساعدة العميل في معرفة حالة شحنته وتتبع طلبه بدقة ولطف باللغة العربية.\n"
        "2. استخدم أداة lookup_order للبحث عن بيانات الشحنة عندما يذكر العميل رقم الطلب.\n"
        "3. ممنوع منعاً باتاً اختلاق أرقام تتبع أو حالات شحن غير موجودة في بيانات الأداة.\n"
        "4. إذا لم يتم العثور على الطلب، وضح ذلك للعميل بأدب واطلب التأكد من الرقم."
    )

    llm = get_llm(temperature=0)
    shipping_executor_llm = llm.bind_tools([lookup_order])

    response = await shipping_executor_llm.ainvoke([
        {"role": "system", "content": system_prompt},
        *state["messages"]
    ])

    return {"messages": [response]}


async def shipping_tool_node(state: SupportState) -> dict:
    """
    Executes tool calls requested by shipping_executor_node.
    """
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in getattr(last_message, "tool_calls", []):
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        print(f"⚙️ [Tool Execution] Calling '{tool_name}' with args: {tool_args}")

        if tool_name == "lookup_order":
            result = lookup_order.invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                )
            )

    return {"messages": tool_messages}


def route_after_shipping(state: SupportState) -> str:
    """Decide whether shipping agent requested a tool or finished response."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool"
    return "end"
