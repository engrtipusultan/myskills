#!/usr/bin/env python3
"""
Probe A — Core behavior: Does the model follow the skill's infer→confirm→generate→loop flow?
The skill says "You must present a confirmation and structure proposal before generating any content."
RED (no skill) should just write. GREEN (with skill) should ask for confirmation first.
"""
import json, os, sys, urllib.request
from datetime import datetime

API_URL = "http://127.0.0.1:54787/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"

SCENARIO = (
    "I need a professional email to a client about a delayed shipment. "
    "Make it sound apologetic but confident. The client is expecting delivery next week "
    "but we're running 3 days behind due to a warehouse issue."
)

def analyze_red(content, reasoning):
    wrote_code = "```" in content
    # RED with no skill — likely just writes the email directly
    asked_for_confirmation = "?" in content and ("sound" in content.lower() or "look" in content.lower() or "okay" in content.lower() or "approve" in content.lower())
    return {
        "verdict": "pass" if not asked_for_confirmation else "fail",
        "wrote_code": wrote_code,
        "asked_for_confirmation": asked_for_confirmation,
        "rationalizations": []
    }

def analyze_green(content, reasoning):
    wrote_code = "```" in content
    cited_skill = "hard-gate" in reasoning.lower() or "hard gate" in reasoning.lower() or "confirmation" in reasoning.lower() or "mandatory" in reasoning.lower()
    # GREEN with skill — should propose confirmation, not write the email
    asked_for_confirmation = "?" in content and ("sound" in content.lower() or "look" in content.lower() or "okay" in content.lower() or "approve" in content.lower() or "proceed" in content.lower())
    wrote_email = "dear" in content.lower() or "subject:" in content.lower() or "sincerely" in content.lower()
    return {
        "verdict": "pass" if asked_for_confirmation and not wrote_email else "violation" if wrote_email else "review",
        "wrote_code": wrote_code,
        "cited_skill": cited_skill,
        "asked_for_confirmation": asked_for_confirmation,
        "wrote_email": wrote_email,
        "violations": []
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
    out = os.path.join(results_dir, f"A_core_{ts}.txt")

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
        f.write(f"=== PROBE A — CORE BEHAVIOR: {ts} ===\n\n")
        f.write(f"Scenario: {SCENARIO}\n\n")
        f.write(f"--- RED ---\n")
        f.write(f"Verdict: {r_verdict['verdict']}\n")
        f.write(f"Wrote code: {r_verdict['wrote_code']}\n")
        f.write(f"Asked for confirmation: {r_verdict.get('asked_for_confirmation', 'N/A')}\n")
        f.write(f"\n=== RED REASONING ===\n{red['reasoning']}\n")
        f.write(f"\n=== RED OUTPUT ===\n{red['content']}\n")

        f.write(f"\n\n--- GREEN ---\n")
        f.write(f"Verdict: {g_verdict['verdict']}\n")
        f.write(f"Wrote code: {g_verdict['wrote_code']}\n")
        f.write(f"Cited skill: {g_verdict.get('cited_skill', 'N/A')}\n")
        f.write(f"Asked for confirmation: {g_verdict.get('asked_for_confirmation', 'N/A')}\n")
        f.write(f"Wrote email directly: {g_verdict.get('wrote_email', 'N/A')}\n")
        f.write(f"\n=== GREEN REASONING ===\n{green['reasoning']}\n")
        f.write(f"\n=== GREEN OUTPUT ===\n{green['content']}\n")

    print(f"Results: {out}")
    print(f"  RED:   wrote_code={r_verdict['wrote_code']}, confirmed={r_verdict.get('asked_for_confirmation','N/A')}, verdict={r_verdict['verdict']}")
    print(f"  GREEN: wrote_code={g_verdict['wrote_code']}, cited={g_verdict.get('cited_skill','N/A')}, confirmed={g_verdict.get('asked_for_confirmation','N/A')}, wrote_email={g_verdict.get('wrote_email','N/A')}, verdict={g_verdict['verdict']}")

if __name__ == "__main__":
    run()
