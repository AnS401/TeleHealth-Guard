# Telehealth Guard Agent (MOCK DATA)

Agent that browses fictional telehealth brands, checks orders and records visit requests, and refuses
clinical questions. Streamlit UI, LLMs only via Groq (primary) and OpenRouter (fallback).

## Run
    pip install -r requirements.txt
    cp .env.example .env        # add GROQ_API_KEY and/or OPENROUTER_API_KEY (optional: works rules-only without)
    streamlit run app.py
    python mcp_server.py        # MCP server (stdio); e.g. add to Claude Desktop's config
    pytest -q                   # offline tests
    python -m eval.run_eval [--llm]

## Design
1. Rules (regex) detect emergencies and clinical questions and ALWAYS win.
2. LLM classifier returns JSON validated by Pydantic; it can escalate to refusal but can never downgrade one.
3. Allowed intents call mock tools; an optional LLM rewrite is rejected by an output guard if it contains clinical content.

## Honest limits
- Eval scenarios were written by the same person who wrote the rules, so rules-only accuracy is optimistic.
  Write fresh scenarios before quoting any number.
- Regex rules miss paraphrases; the LLM layer helps but is unproven here. Not HIPAA compliant. Mock data only.
- Live Groq/OpenRouter calls were not exercised when this was built; test with your keys.
