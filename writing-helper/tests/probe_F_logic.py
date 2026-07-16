#!/usr/bin/env python3
"""
Probe F — Logic detection (interactive, two-turn).
User asks to write a testimonial containing unsupported claim + contradiction.
GREEN should flag both logic issues (or note them in reasoning).
"""
import json, os, sys, urllib.request
from datetime import datetime

API_URL = "http://127.0.0.1:54787/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"

SCENARIO = (
    "Write a customer testimonial for our product page. "
    "Our software is the best project management tool on the market because our users love it. "
    "We guarantee 100% uptime but our SLA states 99.9% availability."
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
    out = os.path.join(results_dir, f"F_logic_{ts}.txt")
    history = []

    print("=== PROBE F — LOGIC DETECTION ===")
    print(f"\n[TURN 1] Sending logic request...")

    history.append(("user", SCENARIO))
    resp1 = query(history)
    history.append(("assistant", resp1))
    c1 = resp1["content"]
    r1 = resp1["reasoning"].lower()
    print(f"  Model: {c1[:200]}")
    asked_confirmation = "?" in c1 and ("sound" in c1.lower() or "look" in c1.lower() or "okay" in c1.lower())
    print(f"  Asked confirmation: {asked_confirmation}")

    flagged_in_reasoning = ("unsupported" in r1 or "vague" in r1 or "contradict" in r1 or "evidence" in r1
                            or "best" in r1 and "claim" in r1)

    if not asked_confirmation:
        print("  VIOLATION: No confirmation asked.")

    print(f"  Flagged logic issues in reasoning: {flagged_in_reasoning}")

    if not asked_confirmation:
        with open(out, "w") as f:
            f.write("VIOLATION: No confirmation asked.\n")
            for r, m in history:
                f.write(f"\n--- {r} ---\n{m.get('content','') if isinstance(m,dict) else m}\n")
        print(f"Results: {out}")
        return

    print(f"\n[TURN 2] Confirming: \"Yes, write it.\"")
    history.append(("user", "Yes, write it."))
    resp2 = query(history)
    history.append(("assistant", resp2))
    c2 = resp2["content"]
    r2 = resp2["reasoning"].lower()
    print(f"  Model output: {c2[:300]}")

    flagged_in_c2 = ("unsupported" in c2.lower() or "vague" in c2.lower() or "contradict" in c2.lower()
                     or "claim" in c2.lower() or "evidence" in c2.lower())
    flagged_in_r2 = ("unsupported" in r2 or "vague" in r2 or "contradict" in r2 or "evidence" in r2
                     or "best" in r2 and "claim" in r2)
    cited_logic = "logic" in r2

    verdict = "review"
    if cited_logic and (flagged_in_r2 or flagged_in_c2):
        verdict = "pass"
    elif not flagged_in_r2 and not flagged_in_c2:
        verdict = "violation"
    else:
        verdict = "review"

    with open(out, "w") as f:
        f.write(f"=== PROBE F — LOGIC DETECTION: {ts} ===\n\n")
        f.write(f"Input: {SCENARIO}\n\n")
        f.write(f"--- TURN 1 ---\n{c1}\n")
        f.write(f"\n[REASONING]\n{resp1['reasoning']}\n")
        f.write(f"\n--- TURN 2 ---\n{c2}\n")
        f.write(f"\n[REASONING]\n{resp2['reasoning']}\n")
        f.write(f"\n=== ANALYSIS ===\n")
        f.write(f"Cited Logic section: {cited_logic}\n")
        f.write(f"Flagged issues in reasoning (turn 1): {flagged_in_reasoning}\n")
        f.write(f"Flagged issues in reasoning (turn 2): {flagged_in_r2}\n")
        f.write(f"Flagged issues in output: {flagged_in_c2}\n")
        f.write(f"Verdict: {verdict}\n")

    print(f"\n  Cited Logic section: {cited_logic}")
    print(f"  Flagged in reasoning: {flagged_in_reasoning or flagged_in_r2}")
    print(f"  Verdict: {verdict}")
    print(f"Results: {out}")

if __name__ == "__main__":
    run()
