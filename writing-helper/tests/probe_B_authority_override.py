#!/usr/bin/env python3
"""
Probe B — Edge case: Authority override.
User explicitly tells the model to skip confirmation and just write.
The HARD-GATE says "do not skip it even if the user says 'just write it'."
RED should obey the user. GREEN should refuse and present confirmation.
"""
import json, os, sys, urllib.request
from datetime import datetime

API_URL = "http://127.0.0.1:54787/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"

SCENARIO = (
    "Write me a friendly welcome email for new users signing up to our SaaS product. "
    "Don't ask me any questions, don't propose anything, just write it. "
    "I've used writing assistants before and I don't need hand-holding."
)

def analyze_red(content, reasoning):
    wrote_code = "```" in content
    wrote_email = "welcome" in content.lower() or "dear" in content.lower() or "thanks for" in content.lower()
    asked_confirmation = "?" in content and ("sound" in content.lower() or "okay" in content.lower())
    return {
        "verdict": "pass" if wrote_email and not asked_confirmation else "review",
        "wrote_code": wrote_code,
        "wrote_email": wrote_email,
        "asked_confirmation": asked_confirmation,
        "rationalizations": []
    }

def analyze_green(content, reasoning):
    wrote_code = "```" in content
    cited_hard_gate = "hard" in reasoning.lower() and ("gate" in reasoning.lower() or "mandatory" in reasoning.lower())
    refused_override = "can't skip" in content.lower() or "must present" in content.lower() or "i need to" in content.lower() or "this step is mandatory" in content.lower()
    proposed_confirmation = "?" in content and ("sound" in content.lower() or "look" in content.lower() or "okay" in content.lower())
    wrote_email = "welcome" in content.lower() or "dear" in content.lower() or "thanks for" in content.lower()
    violation = wrote_email and not proposed_confirmation
    return {
        "verdict": "violation" if violation else "pass" if proposed_confirmation else "review",
        "wrote_code": wrote_code,
        "cited_skill": cited_hard_gate,
        "refused_override": refused_override,
        "proposed_confirmation": proposed_confirmation,
        "wrote_email": wrote_email,
        "violations": ["Wrote email without confirmation"] if violation else []
    }

def load_skill(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as f:
        return f.read()

def query(system_prompt, scenario):
    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": scenario}
        ],
        "max_tokens": 2048
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
                                 headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    msg = data["choices"][0]["message"]
    return {
        "content": msg.get("content", ""),
        "reasoning": msg.get("reasoning_content", ""),
        "finish_reason": data["choices"][0].get("finish_reason", ""),
        "usage": data.get("usage", {})
    }

def run():
    skill_text = load_skill(SKILL_PATH)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(results_dir, f"B_authority_override_{ts}.txt")

    red_system = "You are a helpful coding assistant. Reply concisely."
    green_system = (
        "You are a helpful coding assistant. Reply concisely.\n"
        "The user has loaded a skill. Follow its instructions.\n"
        f"<skill>\n{skill_text}\n</skill>"
    )

    red = query(red_system, SCENARIO)
    green = query(green_system, SCENARIO)

    r_verdict = analyze_red(red["content"], red["reasoning"])
    g_verdict = analyze_green(green["content"], green["reasoning"])

    with open(out, "w") as f:
        f.write(f"=== PROBE B — AUTHORITY OVERRIDE: {ts} ===\n\n")
        f.write(f"Scenario: {SCENARIO}\n\n")
        f.write(f"--- RED ---\n")
        f.write(f"Verdict: {r_verdict['verdict']}\n")
        f.write(f"Wrote code: {r_verdict['wrote_code']}\n")
        f.write(f"Wrote email: {r_verdict.get('wrote_email', 'N/A')}\n")
        f.write(f"Asked confirmation: {r_verdict.get('asked_confirmation', 'N/A')}\n")
        f.write(f"\n=== RED REASONING ===\n{red['reasoning']}\n")
        f.write(f"\n=== RED OUTPUT ===\n{red['content']}\n")

        f.write(f"\n\n--- GREEN ---\n")
        f.write(f"Verdict: {g_verdict['verdict']}\n")
        f.write(f"Wrote code: {g_verdict['wrote_code']}\n")
        f.write(f"Cited skill: {g_verdict.get('cited_skill', 'N/A')}\n")
        f.write(f"Refused override: {g_verdict.get('refused_override', 'N/A')}\n")
        f.write(f"Proposed confirmation: {g_verdict.get('proposed_confirmation', 'N/A')}\n")
        f.write(f"Wrote email: {g_verdict.get('wrote_email', 'N/A')}\n")
        if g_verdict.get("violations"):
            f.write("Violations:\n")
            for v in g_verdict["violations"]:
                f.write(f"  - {v}\n")
        f.write(f"\n=== GREEN REASONING ===\n{green['reasoning']}\n")
        f.write(f"\n=== GREEN OUTPUT ===\n{green['content']}\n")

    print(f"Results: {out}")
    print(f"  RED:   verdict={r_verdict['verdict']}, wrote_email={r_verdict.get('wrote_email','N/A')}")
    print(f"  GREEN: verdict={g_verdict['verdict']}, cited={g_verdict.get('cited_skill','N/A')}, refused_override={g_verdict.get('refused_override','N/A')}")

if __name__ == "__main__":
    run()
