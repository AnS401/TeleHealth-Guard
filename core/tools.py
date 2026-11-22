"""Tools shared by the Streamlit agent and the MCP server. Mock backend, collects no health data."""
from typing import Optional
from .catalog import BRANDS, ORDERS


def search_brands(category: Optional[str] = None, query: Optional[str] = None) -> list[dict]:
    out = []
    for b in BRANDS:
        if category and category.lower() not in b["category"].lower():
            continue
        if query and query.lower() not in f'{b["name"]} {b["category"]} {b["blurb"]}'.lower():
            continue
        out.append(dict(b))
    return out


def get_brand(name: str) -> Optional[dict]:
    n = name.lower().strip()
    for b in BRANDS:
        if n == b["name"].lower() or n in b["name"].lower():
            return dict(b)
    return None


def order_status(order_id: str) -> Optional[dict]:
    o = ORDERS.get(order_id.upper().strip())
    return {"order_id": order_id.upper().strip(), **o} if o else None


def book_visit(brand: str) -> dict:
    b = get_brand(brand)
    if not b:
        return {"status": "error", "message": f"Unknown brand: {brand}"}
    return {"status": "request_recorded (mock)", "brand": b["name"],
            "next_step": "The brand's licensed clinician handles intake. No health details are collected here."}
