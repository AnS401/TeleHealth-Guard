from . import guardrails as g, llm, tools
from .schemas import AgentReply, Intent


def _render_brands(rows):
    if not rows:
        return "No matching brands found."
    return "\n".join(f"- {b['name']} ({b['category']}): {b['blurb']} From ${b['from_price_usd']}/mo." for b in rows)


def _render_brand(b):
    return (f"{b['name']} ({b['category']}): {b['blurb']} Products: {', '.join(b['products'])}. "
            f"From ${b['from_price_usd']}/mo. Ships to: {b['ships_to']}. "
            f"A clinician visit is {'required' if b['visit_required'] else 'not required'}.")


def _polish(facts: str, message: str) -> str:
    msgs = [{"role": "system", "content": "Rewrite the FACTS as a short, friendly reply (max 70 words). Use ONLY the "
             "facts. Add no medical information, claims, or advice."},
            {"role": "user", "content": f"User asked: {message}\nFACTS:\n{facts}"}]
    try:
        text, _ = llm.chat(msgs, max_tokens=200)
        return g.output_guard(text.strip(), facts)
    except llm.LLMUnavailable:
        return facts


def handle(message: str, use_llm: bool = True) -> AgentReply:
    rules = g.rules_classify(message)
    llm_on = use_llm and llm.available()
    llm_res = g.llm_classify(message) if llm_on else None
    final, why = g.decide(message, rules, llm_res)
    trace = {"rules": rules.model_dump(mode="json"), "llm": llm_res.model_dump(mode="json") if llm_res else None,
             "decision": why, "final_intent": final.intent.value}
    calls, blocked, text = [], False, ""

    if final.intent == Intent.emergency:
        text, blocked = g.EMERGENCY_MSG, True
    elif final.intent == Intent.clinical_advice:
        text, blocked = g.CLINICAL_MSG, True
    elif final.intent == Intent.browse_brands:
        rows = tools.search_brands(final.category)
        calls.append({"tool": "search_brands", "args": {"category": final.category}, "results": len(rows)})
        text = _render_brands(rows)
    elif final.intent == Intent.brand_details:
        b = tools.get_brand(final.brand) if final.brand else None
        calls.append({"tool": "get_brand", "args": {"name": final.brand}, "found": bool(b)})
        text = _render_brand(b) if b else "Which brand do you mean? Ask me to list the brands."
    elif final.intent == Intent.order_status:
        o = tools.order_status(final.order_id) if final.order_id else None
        calls.append({"tool": "order_status", "args": {"order_id": final.order_id}, "found": bool(o)})
        text = (f"Order {o['order_id']} from {o['brand']}: {o['status']} ({o['eta']})." if o else
                "Please share your order ID (format ORD-1234). Try ORD-1001, ORD-1002 or ORD-1003 in this demo.")
    elif final.intent == Intent.book_visit:
        if final.brand:
            r = tools.book_visit(final.brand)
            calls.append({"tool": "book_visit", "args": {"brand": final.brand}, "status": r["status"]})
            text = f"Visit request recorded for {r['brand']} (mock). {r['next_step']}"
        else:
            text = "Which brand would you like to book with? Ask me to list the brands."
    else:
        text = g.OFF_TOPIC_MSG

    if llm_on and not blocked and final.intent not in (Intent.off_topic,) and calls:
        text = _polish(text, message)
    return AgentReply(intent=final.intent, text=text, blocked=blocked, tools_called=calls, trace=trace)
