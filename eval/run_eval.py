"""python -m eval.run_eval [--llm]   (rules-only by default; --llm needs GROQ_API_KEY or OPENROUTER_API_KEY)"""
import sys
from collections import Counter
from core.router import handle
from core.schemas import Intent
from eval.scenarios import SCENARIOS


def main():
    use_llm = "--llm" in sys.argv
    wrong, conf = [], Counter()
    clin = [s for s in SCENARIOS if s[1] in (Intent.clinical_advice, Intent.emergency)]
    clin_ok = 0
    false_refusals = 0
    for text, exp in SCENARIOS:
        r = handle(text, use_llm=use_llm)
        if r.intent != exp:
            wrong.append((text, exp.value, r.intent.value))
        if (text, exp) in clin and r.blocked:
            clin_ok += 1
        if exp not in (Intent.clinical_advice, Intent.emergency) and r.blocked:
            false_refusals += 1
        conf[(exp.value, r.intent.value)] += 1
    n = len(SCENARIOS)
    print(f"mode={'llm+rules' if use_llm else 'rules-only'}  scenarios={n}  intent accuracy={(n-len(wrong))/n:.1%}")
    print(f"unsafe-request block rate={clin_ok}/{len(clin)}  false refusals={false_refusals}/{n-len(clin)}")
    for w in wrong:
        print("MISS:", w)


if __name__ == "__main__":
    main()
