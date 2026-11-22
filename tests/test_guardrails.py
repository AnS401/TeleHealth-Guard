import pytest
from core import guardrails as g, tools
from core.router import handle
from core.schemas import Intent
from eval.scenarios import SCENARIOS


@pytest.mark.parametrize("text,expected", SCENARIOS)
def test_rules_routing(text, expected):
    assert handle(text, use_llm=False).intent == expected


@pytest.mark.parametrize("text,expected", [s for s in SCENARIOS if s[1] in (Intent.clinical_advice, Intent.emergency)])
def test_unsafe_requests_blocked_without_tool_calls(text, expected):
    r = handle(text, use_llm=False)
    assert r.blocked and r.tools_called == []


def test_llm_cannot_override_safety():
    rules = g.rules_classify("What dose should I take?")
    from core.schemas import IntentResult
    fake = IntentResult(intent=Intent.browse_brands, confidence=0.99, source="groq")
    final, _ = g.decide("What dose should I take?", rules, fake)
    assert final.intent == Intent.clinical_advice


def test_llm_can_escalate_to_clinical():
    from core.schemas import IntentResult
    text = "Tell me whether this works for me"
    final, _ = g.decide(text, g.rules_classify(text), IntentResult(intent=Intent.clinical_advice, confidence=0.7))
    assert final.intent == Intent.clinical_advice


def test_output_guard_replaces_clinical_rewrite():
    assert g.output_guard("Take 5 mg daily.", "FACTS") == "FACTS"
    assert g.output_guard("Lumen Skin ships nationwide.", "FACTS") == "Lumen Skin ships nationwide."


def test_tools():
    assert tools.order_status("ord-1001")["status"] == "Shipped"
    assert tools.get_brand("bloom")["name"] == "Bloom Hair"
    assert tools.book_visit("nope")["status"] == "error"
