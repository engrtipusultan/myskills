# Shake Down

RED-GREEN-REFACTOR testing methodology for agent skills. Tests any skill against adversarial scenarios on local models to find loopholes and rationalizations.

## How It Works

Every scenario runs twice:

1. **RED** — without the skill. The model should fail or rationalize. This proves the test is meaningful.
2. **GREEN** — with the skill injected. The model should comply.

Compare the two to find gaps, then refactor the skill and retest.

## Probe Types

| Probe | Type | What it catches |
|-------|------|-----------------|
| A — Core behavior | Single-turn | Does the model follow the skill at all? |
| B — Edge cases | Single-turn | Does it break under pressure? |
| C — Regression | Single-turn | Did new additions break existing behavior? |
| D — Terminal state | Interactive multi-turn | Does the full workflow reach the defined terminal action? |

Stop on first failure. Fix, retest all.

## Quick Start

Write a Python script that sends user messages to the llama.cpp API — once without the skill (RED) and once with it injected in `<skill>` tags (GREEN). Compare outputs manually. For probe D, drive the conversation interactively following the multi-turn guidance in the skill.
