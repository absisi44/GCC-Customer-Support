# ======================================================
# Order Lookup Tool (from Day 2 notebook)
# ======================================================

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from .orders_db import ORDERS_DB


class OrderLookupInput(BaseModel):
    order_id: str = Field(description="رقم الطلب الخاص بالعميل (Order ID)، مثال: 5501")


@tool(args_schema=OrderLookupInput)
def lookup_order(order_id: str) -> dict:
    """البحث عن تفاصيل حالة الطلب والشحنة ورقم التتبع بواسطة رقم الطلب."""
    clean_id = str(order_id).strip()
    order = ORDERS_DB.get(clean_id)

    if order is None:
        return {
            "success": False,
            "error": f"الطلب رقم {clean_id} غير موجود في النظام. يرجى التأكد من الرقم."
        }

    return {
        "success": True,
        "order": order
    }
