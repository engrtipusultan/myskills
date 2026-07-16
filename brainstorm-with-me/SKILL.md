---
name: brainstorm-with-me
disable-model-invocation: true
description: Explore and clarify ideas, then produce a validated outcome
---

# Ideas Into Clarity

<HARD-GATE>
Present a clear outcome and get user approval before writing or editing any file, scaffolding a project, modifying config, or invoking any implementation skill. This applies to every project regardless of perceived simplicity. When uncertain, ask — never guess or assume.
</HARD-GATE>

## Anti-Pattern: Bypassing Clarity

Every "simple" project: a todo list, single utility, config change, or life decision. Simple is where unexamined assumptions waste the most work. The outcome can be a few sentences, but you MUST present it and get approval.

## Process Checklist

Create a task for each item. Complete in order, one step per turn. Each step is done when its criterion is met.

1. **Probe the landscape** — Read README, scan directory structure, check recent commits. Done. If no repo exists, ask the user to describe the current project or context.
2. **Probe the idea (360°)** — First assess scope: if the request covers multiple independent domains (e.g., "build a platform with chat, billing, analytics" or "start a business"), flag it and ask the user which piece to start with. Then probe one piece at a time. One question per turn. Purpose, constraints, success criteria, edge cases, unstated assumptions, fuzzy or overloaded terms. Press on vague terms with concrete scenarios that stress-test boundaries. Stay within the original scope — flag drift. Done when the user confirms the full picture is covered.
3. **Propose approaches** — 2-3 with trade-offs and your recommendation. Lead with your recommended option. Done when proposed.
4. **Present the outcome** — Section by section. Scale to complexity. For design outcomes, break into units with one clear purpose each, communicating through well-defined interfaces. Know what each unit does, how to use it, and what it depends on. Done when the user approves each section. If they don't, revise and re-present.
5. **Record the outcome** — Write to `docs/clarified-outcomes/YYYY-MM-DD-clarified-outcome-<topic>.md` where `<topic>` is a short slug (max 30 chars, lowercase, hyphenated, no stop words) derived from the core subject. For code projects, commit. Done when file exists.
6. **Self-review the outcome** — Quick inline check: any placeholders ("TBD", "TODO")? Any contradictions between sections? Any requirement that could be read two ways? Fix issues silently. Done when clean.
7. **User reviews the outcome** — Ask the user to review the file. If they request changes, make them and re-run step 6. Done when user approves.
8. **Transition** — For code projects: write the implementation yourself step by step. Break the plan into small, ordered tasks and execute them one at a time. For other outcomes: present the final outcome and STOP.

## Key Principles

- **One question per turn** — ask, get an answer, then ask the next
- **Multiple choice preferred** — offer 2-3 options when possible
- **YAGNI** — strip unnecessary scope from every outcome
- **Explore alternatives** — always propose 2-3 approaches before settling

## Outcome Template (Reference)

1-3 sentences per section for straightforward parts, up to 300 words for nuanced ones. Ask "Does this look right?" after each section.
