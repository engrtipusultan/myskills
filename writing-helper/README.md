# Writing Helper

Write or rewrite any text — docs, emails, articles, stories, reports — with always-on grammar correction and human-sounding polish.

## Quickstart

Load the skill in an agent session. The skill will:
1. Infer format, tone, audience, and purpose from your request
2. Confirm the plan with a structure proposal (inline or file path)
3. Generate output with grammar correction + tone match + human polish
4. Loop on revisions until you say "looks good"

## Reference Files

- `references/grammar-correction.md` — Minimal-change grammar rules
- `references/tones.md` — 7 tones (Formal, Professional, Technical, Neutral, Casual, Exciting, Friendly)
- `references/authentic-writing.md` — Guidelines for removing AI tells

## Validation

All 4 probes pass on Gemma-4-26B and Qwen-A3B-35B:
- **A** — Core behavior: infer → confirm → generate → loop
- **B** — Authority override: conscious override with mandatory layers still applied
- **C** — Regression: existing text rewrite with confirmation
- **D** — Multi-turn interactive: adjustments and terminal state
