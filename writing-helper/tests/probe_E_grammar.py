#!/usr/bin/env python3
"""
Probe E — Grammar precision (interactive, two-turn).
Turn 1: User asks to fix grammar → model proposes confirmation
Turn 2: User confirms → model delivers corrected text
Checks: all 3 original errors fixed in output
"""
import json, os, sys, urllib.request
from datetime import datetime

API_URL = "http://127.0.0.1:54787/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"

ERROR_TEXT = (
    "The list of items on the invoice are incorrect. "
    "I was interesting on learning more about your service. "
    "Their going to meet us at the office. "
    "The decision was made by the team to move forward."
)

SCENARIO = f"Fix any grammar errors in this text:\n\n{ERROR_TEXT}"

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
    out = os.path.join(results_dir, f"E_grammar_{ts}.txt")
    history = []

    print("=== PROBE E — GRAMMAR PRECISION ===")
    print(f"\n[TURN 1] Sending grammar-fix request...")

    history.append(("user", SCENARIO))
    resp1 = query(history)
    history.append(("assistant", resp1))
    c1 = resp1["content"]
    print(f"  Model: {c1[:200]}")
    asked_confirmation = "?" in c1 and ("sound" in c1.lower() or "look" in c1.lower() or "okay" in c1.lower() or "right" in c1.lower())
    print(f"  Asked confirmation: {asked_confirmation}")

    if not asked_confirmation:
        print("  VIOLATION: No confirmation asked. Aborting.")
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
    print(f"  Model output: {c2[:300]}")

    if not c2.strip():
        print("  VIOLATION: Empty output after confirmation.")
        with open(out, "w") as f:
            f.write("VIOLATION: Empty output.\n")
        print(f"Results: {out}")
        return

    c2l = c2.lower()
    cited_surgical = "surgical" in r2

    err1_gone = "list of items on the invoice are" not in c2l
    err2_gone = "interesting on" not in c2l and "interested in" in c2l
    err3_gone = "their going" not in c2l

    all_ok = err1_gone and err2_gone and err3_gone
    verdict = "pass" if all_ok else "violation"

    with open(out, "w") as f:
        f.write(f"=== PROBE E — GRAMMAR PRECISION: {ts} ===\n\n")
        f.write(f"Input: {ERROR_TEXT}\n\n")
        f.write(f"--- TURN 1 ---\n{c1}\n")
        f.write(f"\n[REASONING]\n{resp1['reasoning']}\n")
        f.write(f"\n--- TURN 2 ---\n{c2}\n")
        f.write(f"\n[REASONING]\n{resp2['reasoning']}\n")
        f.write(f"\n=== ANALYSIS ===\n")
        f.write(f"Cited surgical: {cited_surgical}\n")
        f.write(f"Error1 'list... are' gone: {err1_gone}\n")
        f.write(f"Error2 'interesting on' fixed: {err2_gone}\n")
        f.write(f"Error3 'Their going' fixed: {err3_gone}\n")
        f.write(f"Verdict: {verdict}\n")

    print(f"\n  err1_gone={err1_gone}  err2_gone={err2_gone}  err3_gone={err3_gone}")
    print(f"  Verdict: {verdict}")
    print(f"Results: {out}")

if __name__ == "__main__":
    run()
