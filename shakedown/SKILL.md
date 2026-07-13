---
name: shakedown
disable-model-invocation: true
description: RED-GREEN-REFACTOR skill testing against local llama.cpp — write scripts, run scenarios, refactor
---

# Shakedown: RED-GREEN-REFACTOR for Skills

Run a shakedown cruise on any skill: feed it adversarial scenarios through a local llama.cpp API, watch it pass or rationalize, then refactor and retest.

Supports two testing modes:
- **Single-turn probes** (batch) — quick pass/fail for specific behaviors
- **Interactive multi-turn** (real-time) — validates terminal state through full conversation

## Prerequisites

- A local llama.cpp server running at a known port with the target model loaded
- Python 3 with `urllib.request` (stdlib — no dependencies)

## Shakedown Checklist

Create a task for each step. Complete in order. Each step is done when its criterion is met.

1. **Write the shakedown script** — Copy `scripts/PROBE_TEMPLATE.py` into the target skill's `tests/` directory. Customize `SCENARIO`, `API_URL`, `MODEL`, and `SKILL_PATH`. Done when one full RED+GREEN cycle runs and writes a result file.
2. **Run RED shakedown** — Run each scenario against the RED prompt (no skill loaded). Done when every scenario has a result file with the model's raw response.
3. **Run GREEN shakedown** — Run each scenario against the GREEN prompt (skill injected into `<skill>` tags in system prompt). Done when every scenario has a result file.
4. **Compare shakedown results** — For each scenario: did RED write code or skip the skill's process? Did GREEN follow the skill? Capture rationalizations verbatim from `reasoning_content`. Done when every scenario has a pass/fail verdict and all rationalizations are quoted.
5. **REFACTOR** — For each GREEN violation, edit the skill to close the specific loophole. Re-run the scenario. Done when that scenario passes. Repeat until no violations remain.

## Probe Flow (Progressive)

Run probes in order — earlier ones are faster, later ones validate terminal state:

1. **A — Core behavior** (single-turn): Does the model follow the skill's core directive? (e.g., if the skill says "ask before acting", does it ask?)
2. **B — Edge cases** (single-turn): Does it handle adversarial inputs? (e.g., scope creep, time pressure, authority override, sunk cost)
3. **C — Regression** (single-turn): Do new additions break existing behavior? (e.g., a simple standard case that should work unchanged)
4. **D — Multi-turn terminal state** (interactive): Does the model reach the terminal state through a full conversation? Must be driven interactively — scripts cannot adapt to unexpected turns.

Stop on first failure. Fix the skill, re-run all probes.

## Shakedown Script Template

Disclosed in [`scripts/PROBE_TEMPLATE.py`](scripts/PROBE_TEMPLATE.py). Every shakedown starts from this — only the scenario text and target model name change between runs.

## Running the Shakedown

```bash
# Single-turn probes (A, B, C):
python3 tests/probe.py            # RED + GREEN for one scenario (from PROBE_TEMPLATE.py)

# Multi-turn interactive probe (D):
# Drive manually — talk to the model API turn by turn, see below
```

## Multi-Turn Interactive Testing

Single-turn probes cannot validate **terminal state** (the skill-defined action that ends the workflow). Only a multi-turn conversation can prove the model progresses through all skill steps. Drive it interactively — do NOT script answers.

### When to use

| Approach | Best for | Why |
|----------|----------|-----|
| Single-turn batch script | Specific behaviors (scope check, YAGNI, regression) | Fast, reproducible, easy to compare RED vs GREEN |
| Interactive multi-turn | Terminal state, full skill flow | Scripted answers derail when the model asks something unexpected |

### The Interactive Loop

For each turn:

1. **Send user message** to the model API with full conversation history
2. **Read the model's response** — examine both `content` and `reasoning_content`
3. **Detect the phase** from the model's output:
   - **Probe**: model asks a question → answer it helpfully
   - **Options**: model proposes approaches → pick one
   - **Design**: model presents blueprint sections → approve each section
   - **Terminal**: model invokes the skill's defined terminal action → done
   - **Violation**: model writes code without approval → abort, REFACTOR
4. **Generate a natural reply** — be cooperative, advance the conversation. Short keyword-matched answers cause loops — give complete, informative responses.
5. **Repeat** until terminal state or max turns

### Phase Detection Heuristics

Check the model's **output content** (not reasoning) for:

```
Probe:   ends with "?" — model is gathering requirements
Options: mentions "option", "approach", "recommend" — pick one
Design:  presents sections, asks "Does this look right?" — approve
Terminal: mentions the terminal action verbatim — stop
```

### Standard Scenario

Use a scenario that exercises multiple steps of the skill, including its terminal action:

> A request that requires the skill's full workflow — probing, options, design, approval, and terminal transition.

### Handling Repetition

If the model repeats the same question (stuck loop):
- Your last answer was probably too short or off-topic
- Give a more complete answer that directly addresses the question
- If the model restates facts from history (e.g., "since you're on Linux"), do not re-match those keywords — it's self-talk, not a question

## Shakedown Checks

When comparing RED and GREEN outputs, mark these:

- **Code written?** Did the model emit code blocks without being asked?
- **Skill cited?** Did the model reference the skill or HARD-GATE in its reasoning?
- **Steps followed?** Did the model progress through the skill's checklist in order?
- **Rationalization captured?** Did the model explain why it deviated?
- **Terminal reached?** (multi-turn only) Did the model reach the skill-defined terminal state?
