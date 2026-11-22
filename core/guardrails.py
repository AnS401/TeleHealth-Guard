"""Layered scope guard.
Layer 1: deterministic rules (emergency + clinical patterns) that ALWAYS win.
Layer 2: LLM intent classifier validated by Pydantic (Groq/OpenRouter), used only to add information.
Final decision is biased to safety: if either layer says clinical, we refuse.
"""
import json
import re
from typing import Optional
from pydantic import ValidationError
from . import llm
from .catalog import BRANDS, CATEGORY_KEYWORDS
from .schemas import Intent, IntentResult

EMERGENCY = re.compile(
    r"chest pain|can'?t breathe|cannot breathe|trouble breathing|overdos|suicid|kill myself|want to die|"
    r"too many (pills|tablets|doses)|took too (much|many)|heart (is )?racing|"
    r"\bstroke\b|seizure|anaphyla|throat (is )?(closing|swelling)|won'?t stop bleeding|unconscious|poison",
    re.I)

CLINICAL = re.compile(
    r"\b(dos(e|es|age)|how (much|many) (mg|units|pills|tablets)|should i (take|stop|start|use|inject|switch)|"
    r"can i (take|combine|mix|use|drink|stop)|interact\w*|side[- ]?effects?|contraindicat\w*|diagnos\w*|"
    r"do i have(?! to)|safe to|is (it|this|\w+( \w+)?) safe|symptoms?|pregnan\w*|breastfeed\w*|allergic|"
    r"prescribe me|what (medication|medicine|drug)|am i (a )?(good )?candidate|lab results?|"
    r"blood (pressure|sugar)|nursing|ingredients?|dizz\w+|nausea|vomit\w*|rash|hurt|"
    r"(make|making) me (gain|lose|sick|tired)|how long until|see results|\d+\s?mg|mg|will it (work|cure|help)|does it (work|cure)|treat my|cure)\b", re.I)

EMERGENCY_MSG = ("If this could be a medical emergency, stop here and call your local emergency number now "
                 "(911 in the US, 112 in India). I can't assess symptoms or advise on medical situations.")
CLINICAL_MSG = ("I can't give medical advice, dosing, safety or suitability guidance. Those decisions belong to a "
                "licensed clinician at the brand, after a proper visit. I can help you browse brands, check an "
                "order, or request a visit.")
OFF_TOPIC_MSG = "I can only help with browsing telehealth brands, order status, and visit requests."

ORDER_RE = re.compile(r"\bORD-\d{3,}\b", re.I)


def rule_flags(text: str) -> tuple[bool, bool]:
    return bool(EMERGENCY.search(text)), bool(CLINICAL.search(text))


def _find_brand(text: str) -> Optional[str]:
    t = text.lower()
    for b in BRANDS:
        if b["name"].lower() in t:
            return b["name"]
    return None


def _find_category(text: str) -> Optional[str]:
    t = text.lower()
    for k, v in CATEGORY_KEYWORDS.items():
        if k in t:
            return v
    return None


def rules_classify(text: str) -> IntentResult:
    emergency, clinical = rule_flags(text)
    brand, category = _find_brand(text), _find_category(text)
    m = ORDER_RE.search(text)
    if emergency:
        return IntentResult(intent=Intent.emergency, confidence=1, reason="emergency pattern")
    if clinical:
        return IntentResult(intent=Intent.clinical_advice, confidence=0.9, brand=brand, reason="clinical pattern")
    if m or re.search(r"\b(order|track|package|shipment|shipped|delivery)\b", text, re.I):
        return IntentResult(intent=Intent.order_status, order_id=m.group(0).upper() if m else None, reason="order words")
    if re.search(r"\b(book|appointment|schedule)\b", text, re.I):
        return IntentResult(intent=Intent.book_visit, brand=brand, category=category, reason="booking words")
    if brand:
        return IntentResult(intent=Intent.brand_details, brand=brand, reason="brand named")
    if re.search(r"\b(show|browse|list|brands?|stores?|options|find|looking for|what do you (offer|have))\b|offer\??$",
                 text, re.I) or category:
        return IntentResult(intent=Intent.browse_brands, category=category, reason="browse words")
    return IntentResult(intent=Intent.off_topic, reason="no match")


SYSTEM_PROMPT = f"""You classify messages sent to a telehealth marketplace assistant. Never answer the message.
Return ONLY JSON: {{"intent": one of [browse_brands, brand_details, order_status, book_visit, clinical_advice, emergency, off_topic],
"confidence": 0-1, "brand": string|null, "category": string|null, "order_id": string|null, "reason": short string}}.
clinical_advice = anything about dosing, safety, side effects, symptoms, diagnosis, interactions, pregnancy,
suitability or effectiveness of a treatment. emergency = possible urgent medical situation or self-harm.
Known brands: {[b['name'] for b in BRANDS]}."""


def llm_classify(text: str) -> Optional[IntentResult]:
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": text}]
    for _ in range(2):  # one retry on bad JSON / schema
        try:
            raw, provider = llm.chat(msgs, json_mode=True)
            data = json.loads(raw)
            data["source"] = provider
            return IntentResult.model_validate(data)
        except (json.JSONDecodeError, ValidationError, llm.LLMUnavailable, KeyError):
            continue
    return None


def decide(text: str, rules: IntentResult, llm_res: Optional[IntentResult]) -> tuple[IntentResult, str]:
    emergency, clinical = rule_flags(text)
    if emergency or (llm_res and llm_res.intent == Intent.emergency):
        return IntentResult(intent=Intent.emergency, confidence=1, source="guard"), "emergency (rules or LLM)"
    if clinical or (llm_res and llm_res.intent == Intent.clinical_advice):
        who = "rules" if clinical else "LLM"
        return IntentResult(intent=Intent.clinical_advice, confidence=1, source="guard"), f"clinical flagged by {who}"
    if llm_res and llm_res.confidence >= 0.6:
        merged = llm_res.model_copy(update={
            "brand": llm_res.brand or rules.brand, "category": llm_res.category or rules.category,
            "order_id": llm_res.order_id or rules.order_id})
        return merged, "LLM intent accepted"
    return rules, "rules fallback"


def output_guard(text: str, allowed_facts: str) -> str:
    """Reject LLM rewrites that contain clinical content; fall back to the templated facts."""
    if CLINICAL.search(text) or EMERGENCY.search(text):
        return allowed_facts
    return text
