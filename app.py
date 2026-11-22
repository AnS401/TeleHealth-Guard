import os
import streamlit as st
from core import llm
from core.router import handle

st.set_page_config(page_title="Telehealth Guard Agent (demo)", page_icon="🩺", layout="wide")
st.title("🩺 Telehealth Guard Agent")
st.warning("Demo with MOCK data. Not medical advice. Fictional brands, no real patients, no PHI collected.")

with st.sidebar:
    st.header("Settings")
    gk = st.text_input("GROQ_API_KEY", type="password", value=os.getenv("GROQ_API_KEY", ""))
    ok = st.text_input("OPENROUTER_API_KEY", type="password", value=os.getenv("OPENROUTER_API_KEY", ""))
    if gk:
        os.environ["GROQ_API_KEY"] = gk
    if ok:
        os.environ["OPENROUTER_API_KEY"] = ok
    use_llm = st.toggle("Use LLM (Groq, then OpenRouter)", value=True, disabled=not llm.available())
    st.caption("LLM on: intent classification + friendly rewrite. Rules still decide every safety refusal."
               if llm.available() else "No API key set: running rules-only mode.")
    st.divider()
    st.subheader("Try these")
    examples = ["Show me skincare brands", "Tell me about Northstar Weight", "Where is my order ORD-1001?",
                "Book a visit with Bloom Hair", "What dose should I take?", "Can I take it with ibuprofen?",
                "I have chest pain after my first dose", "Write me a poem"]
    for e in examples:
        if st.button(e, use_container_width=True):
            st.session_state["pending"] = e

if "history" not in st.session_state:
    st.session_state.history = []

BADGE = {"clinical_advice": "🛑 refused (clinical)", "emergency": "🚨 emergency redirect",
         "off_topic": "⚪ off-topic"}

for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["text"])
        if m.get("reply"):
            r = m["reply"]
            st.caption(BADGE.get(r.intent.value, f"✅ {r.intent.value}"))
            with st.expander("Agent trace"):
                st.json({"tools_called": r.tools_called, **r.trace})

prompt = st.chat_input("Ask about brands, orders or visits...") or st.session_state.pop("pending", None)
if prompt:
    st.session_state.history.append({"role": "user", "text": prompt})
    reply = handle(prompt, use_llm=use_llm)
    st.session_state.history.append({"role": "assistant", "text": reply.text, "reply": reply})
    st.rerun()
