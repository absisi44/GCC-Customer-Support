# ======================================================
# Orders Mock Database (from Day 2 practical)
# ======================================================

ORDERS_DB = {
    "5501": {
        "order_id": "5501",
        "customer_id": "CUST-1001",
        "status": "shipped",
        "tracking_number": "SPL-77182",
        "carrier": "SPL (سبل)",
        "estimated_delivery": "2026-09-01",
        "items": ["ساعة ذكية Ultra Smartwatch", "شاحن لاسلكي سريع 3-in-1"],
        "total_amount": 420,
        "currency": "SAR",
        "shipping_city": "Riyadh",
        "status_note": "الشحنة خرجت من المستودع المركزي بالرياض وجاري التوصيل للعنوان المكتبي"
    },
    "5502": {
        "order_id": "5502",
        "customer_id": "CUST-1002",
        "status": "delivered",
        "tracking_number": "ARX-88241",
        "carrier": "Aramex",
        "estimated_delivery": "2026-08-26",
        "items": ["سماعات سوني لاسلكية عازلة للضوضاء"],
        "total_amount": 890,
        "currency": "SAR",
        "shipping_city": "Jeddah",
        "status_note": "تم استلام الشحنة وتوقيع إشعار الاستلام بنجاح"
    },
    "5503": {
        "order_id": "5503",
        "customer_id": "CUST-1003",
        "status": "processing",
        "tracking_number": None,
        "carrier": None,
        "estimated_delivery": "2026-09-05",
        "items": ["لوحة مفاتيح ميكانيكية RGB", "ماوس باد مريح"],
        "total_amount": 260,
        "currency": "SAR",
        "shipping_city": "Dubai",
        "status_note": "قيد الفحص والتغليف في المستودع الإقليمي"
    }
}
