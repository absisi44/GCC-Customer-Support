# ======================================================
# Day 2 Billing Specialist Agent & Tool Nodes
# ======================================================
from langchain_core.messages import ToolMessage

# pyrefly: ignore [missing-import]
from app.states.support_state import SupportState
# pyrefly: ignore [missing-import]
from app.tools.invoice_tool import lookup_invoice
# pyrefly: ignore [missing-import]
from app.llms.llm_provider import get_llm


async def billing_executor_node(state: SupportState) -> dict:
    """
    Billing support agent node that can call lookup_invoice tool to check invoices and payments.
    """
    system_prompt = (
        "أنت موظف خدمة العملاء المختص بالفواتير والمدفوعات (Billing Support Agent) لمتجر إلكتروني خليجي.\n"
        "مهمتك:\n"
        "1. مساعدة العميل في الاستفسار عن فواتيره ومشاكل الدفع والخصم المزدوج واسترجاع الأموال بدقة ولطف باللغة العربية.\n"
        "2. استخدم أداة lookup_invoice للبحث عن بيانات الفاتورة عندما يذكر العميل رقم الفاتورة (مثال: INV-5501).\n"
        "3. اشرح تفاصيل المبالغ والعملة وحالة الدفع وعدد مرات الخصم بلطف ووضوح.\n"
        "4. إذا لم يتم العثور على الفاتورة، وضح ذلك للعميل واطلب التأكد من الرقم."
    )

    llm = get_llm(temperature=0)
    billing_executor_llm = llm.bind_tools([lookup_invoice])

    response = await billing_executor_llm.ainvoke([
        {"role": "system", "content": system_prompt},
        *state["messages"]
    ])

    return {"messages": [response]}


async def billing_tool_node(state: SupportState) -> dict:
    """
    Executes tool calls requested by billing_executor_node.
    """
    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in getattr(last_message, "tool_calls", []):
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        print(f"⚙️ [Tool Execution] Calling '{tool_name}' with args: {tool_args}")

        if tool_name == "lookup_invoice":
            result = lookup_invoice.invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_id
                )
            )

    return {"messages": tool_messages}


def route_after_billing(state: SupportState) -> str:
    """Decide whether billing agent requested a tool or finished response."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tool"
    return "end"
