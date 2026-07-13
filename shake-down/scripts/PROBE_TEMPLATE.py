#!/usr/bin/env python3
"""
Shake-down probe script template.

Copy this file into a skill's tests/ directory for each new shake-down.
Only change the CUSTOMIZE sections — everything else is boilerplate.
"""
import json, os, sys, urllib.request
from datetime import datetime

# ---------------------------------------------------------------------------
# CUSTOMIZE: API config
# ---------------------------------------------------------------------------
API_URL = "http://127.0.0.1:42323/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"           # relative to this script

# ---------------------------------------------------------------------------
# CUSTOMIZE: Scenario text
# ---------------------------------------------------------------------------
SCENARIO = (
    "Replace with your adversarial scenario here. "
    "Include time pressure, authority, sunk cost, or other pressures "
    "that make the model want to bypass the skill."
)

# ---------------------------------------------------------------------------
# CUSTOMIZE: Analysis function — returns verdict dict
# ---------------------------------------------------------------------------
def analyze_red(content, reasoning):
    """Return dict with verdict and rationalizations from RED run."""
    return {
        "verdict": "review",
        "wrote_code": "```" in content,
        "rationalizations": []   # extract verbatim quotes from reasoning
    }

def analyze_green(content, reasoning):
    """Return dict with verdict and violations from GREEN run."""
    return {
        "verdict": "review",
        "wrote_code": "```" in content,
        "cited_skill": "hard-gate" in reasoning.lower() or "hard gate" in reasoning.lower(),
        "violations": []          # verbatim quotes of rationalizations
    }

# ---------------------------------------------------------------------------
# Boilerplate — do not change below this line
# ---------------------------------------------------------------------------

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
    out = os.path.join(results_dir, f"probe_{ts}.txt")

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
        f.write(f"=== SHAKE-DOWN PROBE: {ts} ===\n\n")
        f.write(f"--- RED ---\n")
        f.write(f"Verdict: {r_verdict['verdict']}\n")
        f.write(f"Wrote code: {r_verdict['wrote_code']}\n")
        if r_verdict.get("rationalizations"):
            f.write("Rationalizations:\n")
            for r in r_verdict["rationalizations"]:
                f.write(f"  - {r}\n")
        f.write(f"\n=== RED REASONING ===\n{red['reasoning']}\n")
        f.write(f"\n=== RED OUTPUT ===\n{red['content']}\n")

        f.write(f"\n\n--- GREEN ---\n")
        f.write(f"Verdict: {g_verdict['verdict']}\n")
        f.write(f"Wrote code: {g_verdict['wrote_code']}\n")
        f.write(f"Cited skill: {g_verdict.get('cited_skill', 'N/A')}\n")
        if g_verdict.get("violations"):
            f.write("Violations:\n")
            for v in g_verdict["violations"]:
                f.write(f"  - {v}\n")
        f.write(f"\n=== GREEN REASONING ===\n{green['reasoning']}\n")
        f.write(f"\n=== GREEN OUTPUT ===\n{green['content']}\n")

    print(f"Results: {out}")
    print(f"  RED:   wrote_code={r_verdict['wrote_code']}, verdict={r_verdict['verdict']}")
    print(f"  GREEN: wrote_code={g_verdict['wrote_code']}, cited={g_verdict.get('cited_skill','N/A')}, verdict={g_verdict['verdict']}")

if __name__ == "__main__":
    run()
