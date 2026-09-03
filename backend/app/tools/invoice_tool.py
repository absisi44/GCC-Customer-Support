# ======================================================
# Invoice Lookup Tool (from Day 2 notebook exercise)
# ======================================================

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from .invoices_db import INVOICES_DB


class InvoiceLookupInput(BaseModel):
    invoice_id: str = Field(description="رقم الفاتورة، مثال: INV-5501")


@tool(args_schema=InvoiceLookupInput)
def lookup_invoice(invoice_id: str) -> dict:
    """البحث عن تفاصيل الفاتورة والمبلغ المدفوع وحالة العملية."""
    clean_id = str(invoice_id).strip()
    invoice = INVOICES_DB.get(clean_id)

    if invoice is None:
        return {
            "success": False,
            "error": f"الفاتورة رقم {clean_id} غير موجودة في النظام."
        }

    return {
        "success": True,
        "invoice": invoice
    }
