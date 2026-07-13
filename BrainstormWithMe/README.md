# BrainstormWithMe

Cross-domain brainstorming skill. Works for code projects, life decisions, creative work — anything that needs thinking through before acting.

## How It Works

The skill guides a 6-step structured conversation:

1. **Probe the landscape** — understand context and constraints
2. **Probe the idea 360°** — one question per turn, covering purpose, scope, edge cases, assumptions
3. **Propose approaches** — 2-3 options with trade-offs and a recommendation
4. **Present the blueprint** — section by section, get approval on each
5. **Save the blueprint** — write to `docs/plans/`
6. **Transition** — invoke writing-plans and STOP (code) or present final plan (general)

Key guardrails: no code before approval, one step per turn, flag scope drift, YAGNI.

## Usage

Load the skill in an agent session and state your intents — the skill handles the rest.

```bash
# The skill auto-triggers on brainstorming tasks
"Let's build a todo list app"
"I need to plan a career change"
"How should I structure this project?"
```
