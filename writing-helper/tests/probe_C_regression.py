#!/usr/bin/env python3
"""
Probe C — Regression: Existing text rewrite.
The skill has an explicit rule for this ("Existing text to rewrite: same flow").
Test that the three mandatory layers (surgical correction, tone, humanize) are applied.
"""
import json, os, sys, urllib.request
from datetime import datetime

API_URL = "http://127.0.0.1:54787/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"

SCENARIO = (
    "Rewrite this email to be more professional:\n\n"
    "Hey Bob,\n"
    "Just wanted to shoot you a quick note about the project. Things are going pretty well I guess. "
    "We're kinda behind schedule but it's not a big deal. Let me know if you wanna chat about it.\n"
    "Cheers,\nAlex"
)

def analyze_red(content, reasoning):
    wrote_code = "```" in content
    # RED — likely rewrites freely without any structure
    return {
        "verdict": "pass",
        "wrote_code": wrote_code,
        "rationalizations": []
    }

def analyze_green(content, reasoning):
    wrote_code = "```" in content
    cited_skill = "hard-gate" in reasoning.lower() or "hard gate" in reasoning.lower() or "confirmation" in reasoning.lower()
    # GREEN with skill — should propose confirmation before rewriting
    asked_confirmation = "?" in content and ("sound" in content.lower() or "look" in content.lower() or "okay" in content.lower() or "proceed" in content.lower())
    rewrote_directly = "hey bob" not in content.lower() and "dear bob" in content.lower() or "dear" in content.lower()
    # Check if it applied humanize / tone / correction
    applied_layers = "surgical" in reasoning.lower() or "humanize" in reasoning.lower() or "tone" in reasoning.lower()
    return {
        "verdict": "pass" if asked_confirmation else "violation" if not asked_confirmation else "review",
        "wrote_code": wrote_code,
        "cited_skill": cited_skill,
        "asked_confirmation": asked_confirmation,
        "applied_layers": applied_layers,
        "violations": ["Rewrote without confirmation"] if not asked_confirmation else []
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
    out = os.path.join(results_dir, f"C_regression_{ts}.txt")

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
        f.write(f"=== PROBE C — REGRESSION: {ts} ===\n\n")
        f.write(f"Scenario: {'Rewrite casual email to professional'}\n\n")
        f.write(f"--- RED ---\n")
        f.write(f"Verdict: {r_verdict['verdict']}\n")
        f.write(f"Wrote code: {r_verdict['wrote_code']}\n")
        f.write(f"\n=== RED REASONING ===\n{red['reasoning']}\n")
        f.write(f"\n=== RED OUTPUT ===\n{red['content']}\n")

        f.write(f"\n\n--- GREEN ---\n")
        f.write(f"Verdict: {g_verdict['verdict']}\n")
        f.write(f"Wrote code: {g_verdict['wrote_code']}\n")
        f.write(f"Cited skill: {g_verdict.get('cited_skill', 'N/A')}\n")
        f.write(f"Asked confirmation: {g_verdict.get('asked_confirmation', 'N/A')}\n")
        f.write(f"Applied layers: {g_verdict.get('applied_layers', 'N/A')}\n")
        if g_verdict.get("violations"):
            f.write("Violations:\n")
            for v in g_verdict["violations"]:
                f.write(f"  - {v}\n")
        f.write(f"\n=== GREEN REASONING ===\n{green['reasoning']}\n")
        f.write(f"\n=== GREEN OUTPUT ===\n{green['content']}\n")

    print(f"Results: {out}")
    print(f"  RED:   verdict={r_verdict['verdict']}")
    print(f"  GREEN: verdict={g_verdict['verdict']}, cited={g_verdict.get('cited_skill','N/A')}, confirmed={g_verdict.get('asked_confirmation','N/A')}")

if __name__ == "__main__":
    run()
