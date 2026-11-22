"""MCP server exposing the same tools. Run: python mcp_server.py  (stdio transport).
Limit to know: an MCP server cannot control what the host model (ChatGPT/Claude) says. It can only
(1) keep its tools narrow, (2) put scope rules in tool descriptions, and (3) return refusals from check_scope.
"""
from mcp.server.fastmcp import FastMCP
from core import guardrails as g, tools
from core.schemas import Intent

mcp = FastMCP("telehealth-guard-demo")


@mcp.tool()
def check_scope(message: str) -> dict:
    """Call FIRST with the patient's raw message. If allowed is false, relay `reply` verbatim and call no other tool.
    This service never gives dosing, safety, diagnosis or suitability advice."""
    final, why = g.decide(message, g.rules_classify(message), None)
    if final.intent == Intent.emergency:
        return {"allowed": False, "intent": "emergency", "reply": g.EMERGENCY_MSG}
    if final.intent == Intent.clinical_advice:
        return {"allowed": False, "intent": "clinical_advice", "reply": g.CLINICAL_MSG}
    return {"allowed": True, "intent": final.intent.value}


@mcp.tool()
def search_brands(category: str | None = None, query: str | None = None) -> list[dict]:
    """List mock telehealth brands, optionally by category. Non-clinical information only."""
    return tools.search_brands(category, query)


@mcp.tool()
def get_brand(name: str) -> dict | None:
    """Get one brand's public listing (price, shipping, whether a clinician visit is required)."""
    return tools.get_brand(name)


@mcp.tool()
def order_status(order_id: str) -> dict | None:
    """Look up a mock order by ID (e.g. ORD-1001)."""
    return tools.order_status(order_id)


@mcp.tool()
def book_visit(brand: str) -> dict:
    """Record a visit request with a brand. Collects no health information."""
    return tools.book_visit(brand)


if __name__ == "__main__":
    mcp.run()
