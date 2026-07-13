# My Skills

A collection of agent skills optimized for local inference on small models (tested on Gemma-4-26B and Qwen-A3B-35B).

## Skills

- **BrainstormWithMe** — Cross-domain brainstorming skill. Guides structured design before any action, for code projects, life decisions, or creative work. Validated on Gemma-4-26B and Qwen-A3B-35B.
- **Shakedown** — RED-GREEN-REFACTOR testing methodology for validating agent skills against adversarial scenarios on local models. Tested with both single-turn batch probes and interactive multi-turn terminal-state validation.

## Usage

Each skill is self-contained in its folder with a `SKILL.md` (the skill itself) and `README.md` (quickstart). Load the skill in an agent session and follow its checklist.

## Models Verified

| Skill | Gemma-4-26B | Qwen-A3B-35B |
|-------|-------------|--------------|
| BrainstormWithMe | ✅ All 4 probes passed | ✅ All 4 probes passed |
| Shakedown | ✅ Methodology validated | ✅ Methodology validated |
