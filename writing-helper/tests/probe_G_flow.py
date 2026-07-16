#!/usr/bin/env python3
"""
Probe G — Flow smoothing (interactive, two-turn).
User asks to smooth choppy text with unclear pronoun references.
GREEN should smooth transitions and clarify the ambiguous "it".
"""
import json, os, sys, urllib.request
from datetime import datetime

API_URL = "http://127.0.0.1:54787/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"

SCENARIO = (
    "Smooth this text for readability:\n\n"
    "The development team launched the new feature. Users reported bugs. "
    "The team fixed the bugs. We met with the vendor about their API integration. "
    "It was complicated, so we decided against it."
)

def load_skill(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as f:
        return f.read()

def query(messages):
    skill_text = load_skill(SKILL_PATH)
    system = (
        "You are a helpful assistant. Reply concisely.\n"
        "The user has loaded a skill. Follow its instructions.\n"
        f"<skill>\n{skill_text}\n</skill>"
    )
    full = [{"role": "system", "content": system}]
    for role, msg in messages:
        full.append({"role": role, "content": msg if isinstance(msg, str) else msg.get("content","")})
    payload = json.dumps({
        "model": MODEL,
        "messages": full,
        "max_tokens": 4096
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    msg = data["choices"][0]["message"]
    return {
        "content": msg.get("content", ""),
        "reasoning": msg.get("reasoning_content", ""),
    }

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(results_dir, f"G_flow_{ts}.txt")
    history = []

    print("=== PROBE G — FLOW SMOOTHING ===")
    print(f"\n[TURN 1] Sending flow-smooth request...")

    history.append(("user", SCENARIO))
    resp1 = query(history)
    history.append(("assistant", resp1))
    c1 = resp1["content"]
    print(f"  Model: {c1[:200]}")
    asked_confirmation = "?" in c1 and ("sound" in c1.lower() or "look" in c1.lower() or "okay" in c1.lower())
    print(f"  Asked confirmation: {asked_confirmation}")

    if not asked_confirmation:
        print("  VIOLATION: No confirmation asked.")
        with open(out, "w") as f:
            f.write("VIOLATION: No confirmation asked.\n")
            for r, m in history:
                f.write(f"\n--- {r} ---\n{m.get('content','') if isinstance(m,dict) else m}\n")
        print(f"Results: {out}")
        return

    print(f"\n[TURN 2] Confirming: \"Yes, go ahead.\"")
    history.append(("user", "Yes, go ahead."))
    resp2 = query(history)
    history.append(("assistant", resp2))
    c2 = resp2["content"]
    r2 = resp2["reasoning"].lower()
    c2l = c2.lower()
    print(f"  Model output: {c2[:400]}")

    # Check: are the 3 choppy sentences combined?
    has_launched = ("launch" in c2l) and ("bugs" in c2l)
    # Check: is the unclear "it" resolved?
    has_api = "api" in c2l
    vendor_clarified = "integration" in c2l or "api" in c2l

    # Check counts of standalone "it" (unclear reference)
    standalone_it = len([w for w in c2l.split() if w == "it"])
    # The model should clarify what "it" refers to, reducing standalone uses

    cited_flow = "flow" in r2 or "choppy" in r2 or "pronoun" in r2 or "transition" in r2
    resolved_pronoun = standalone_it <= 1  # at most one standalone "it"

    verdict = "violation"
    if cited_flow and has_launched and resolved_pronoun:
        verdict = "pass"
    elif cited_flow and has_launched:
        verdict = "review"

    with open(out, "w") as f:
        f.write(f"=== PROBE G — FLOW SMOOTHING: {ts} ===\n\n")
        f.write(f"Input: {SCENARIO}\n\n")
        f.write(f"--- TURN 1 ---\n{c1}\n")
        f.write(f"\n[REASONING]\n{resp1['reasoning']}\n")
        f.write(f"\n--- TURN 2 ---\n{c2}\n")
        f.write(f"\n[REASONING]\n{resp2['reasoning']}\n")
        f.write(f"\n=== ANALYSIS ===\n")
        f.write(f"Cited Flow section: {cited_flow}\n")
        f.write(f"Sentences combined: {has_launched}\n")
        f.write(f"Vendor/API clarified: {vendor_clarified}\n")
        f.write(f"Standalone 'it' count: {standalone_it}\n")
        f.write(f"Pronoun resolved: {resolved_pronoun}\n")
        f.write(f"Verdict: {verdict}\n")

    print(f"\n  Cited Flow section: {cited_flow}")
    print(f"  Sentences combined: {has_launched}")
    print(f"  Standalone 'it' count: {standalone_it}")
    print(f"  Pronoun resolved: {resolved_pronoun}")
    print(f"  Verdict: {verdict}")
    print(f"Results: {out}")

if __name__ == "__main__":
    run()
