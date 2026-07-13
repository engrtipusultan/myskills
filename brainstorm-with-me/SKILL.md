---
name: brainstorm-with-me
disable-model-invocation: true
description: Brainstorming → structured design, then writing-plans
---

# Blueprinting Ideas Into Designs

<HARD-GATE>
Present a design and get user approval before writing code, scaffolding a project, modifying config, or invoking any implementation skill. This applies to every project regardless of perceived simplicity. When uncertain, ask — never guess or assume.
</HARD-GATE>

## Anti-Pattern: Bypassing Design

Every "simple" project: a todo list, single utility, config change, or life decision. Simple is where unexamined assumptions waste the most work. The design can be a few sentences, but you MUST present it and get approval.

## Blueprint Checklist

Create a task for each item. Complete in order, one step per turn. Each step is done when its criterion is met.

1. **Probe the landscape** — Read README, scan directory structure, check recent commits. Done. If no repo exists, ask the user to describe the current project or context.
2. **Probe the idea (360°)** — First assess scope: if the request covers multiple independent domains (e.g., "build a platform with chat, billing, analytics" or "start a business"), flag it and ask the user which piece to start with. Then probe one piece at a time. One question per turn. Purpose, constraints, success criteria, edge cases, unstated assumptions. Stay within the original scope — flag drift. Done when the user confirms the full picture is covered.
3. **Propose approaches** — 2-3 with trade-offs and your recommendation. Lead with your recommended option. Done when proposed.
4. **Present the blueprint** — Section by section. Scale to complexity. Done when the user approves each section. If they don't, revise and re-present.
5. **Save the blueprint** — Write to `docs/plans/YYYY-MM-DD-<topic>-design.md`. For code projects, commit. Done when file exists.
6. **Transition** — Code projects: invoke writing-plans and STOP. General plans: present the final plan and STOP.

## Key Principles

- **One question per turn** — ask, get an answer, then ask the next
- **Multiple choice preferred** — offer 2-3 options when possible
- **YAGNI** — strip unnecessary scope from every design
- **Explore alternatives** — always propose 2-3 approaches before settling

## Design Template (Reference)

1-3 sentences per section for straightforward parts, up to 300 words for nuanced ones. Ask "Does this look right?" after each section.
