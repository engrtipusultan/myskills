#!/usr/bin/env python3
"""
Probe D — Multi-turn interactive: Full skill flow to terminal state.
Tests the complete: Infer → Confirm → Generate → Loop → "looks good" flow.
"""
import json, os, sys, urllib.request
from datetime import datetime

API_URL = "http://127.0.0.1:54787/v1/chat/completions"
MODEL = "Gemma-4-26B-A4B"
SKILL_PATH = "../SKILL.md"

LOG = []

def log(role, msg):
    LOG.append((role, msg))
    print(f"\n--- {role.upper()} ---")
    # Truncate long messages for readability
    text = msg.get("content", "") if isinstance(msg, dict) else msg
    if len(text) > 600:
        text = text[:600] + "... [truncated]"
    print(text)

def load_skill(path):
    with open(os.path.join(os.path.dirname(__file__), path)) as f:
        return f.read()

def query(messages, system_extra=""):
    skill_text = load_skill(SKILL_PATH)
    system = (
        "You are a helpful writing assistant. Reply concisely.\n"
        "The user has loaded a skill. Follow its instructions.\n"
        f"<skill>\n{skill_text}\n</skill>"
    )
    full_messages = [{"role": "system", "content": system}]
    for role, msg in messages:
        full_messages.append({"role": role, "content": msg["content"] if isinstance(msg, dict) else msg})

    payload = json.dumps({
        "model": MODEL,
        "messages": full_messages,
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
    }

def run():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(results_dir, f"D_interactive_{ts}.txt")

    history = []

    # --- Turn 1: User issues request ---
    user_msg = (
        "I need a short welcome email for new users who sign up for our project management tool. "
        "The tone should be friendly and energetic. Keep it under 100 words."
    )
    print("\n=== TURN 1: User request ===")
    print(user_msg)
    history.append(("user", {"content": user_msg}))
    resp = query(history)
    history.append(("assistant", resp))
    log("assistant (turn 1)", resp)

    # --- Check if model asked for confirmation ---
    content = resp["content"]
    asked_confirmation = "?" in content and ("sound" in content.lower() or "look" in content.lower() or "okay" in content.lower())
    print(f"\n  Asked for confirmation: {asked_confirmation}")

    if not asked_confirmation:
        print("  VIOLATION: Model did not ask for confirmation!")
        with open(out, "w") as f:
            f.write("=== PROBE D — VIOLATION: No confirmation requested ===\n")
            for role, msg in history:
                f.write(f"\n--- {role} ---\n{msg.get('content','') if isinstance(msg,dict) else msg}\n")
        print(f"Results: {out}")
        return

    # --- Turn 2: User confirms ---
    user_msg2 = "Sounds good, go ahead and write it."
    print(f"\n=== TURN 2: User confirmation ===")
    print(user_msg2)
    history.append(("user", {"content": user_msg2}))
    resp = query(history)
    history.append(("assistant", resp))
    log("assistant (turn 2)", resp)

    # --- Check if model generated the email ---
    content2 = resp["content"]
    wrote_email = "welcome" in content2.lower() and ("@" in content2 or "dear" in content2.lower() or "hi" in content2.lower())
    mentioned_layers = "surgical" in content2.lower() or "humanize" in content2.lower()
    # Also check reasoning for layer application
    reasoning2 = resp["reasoning"]
    applied_in_reasoning = "surgical" in reasoning2.lower() or "humanize" in reasoning2.lower() or "tone" in reasoning2.lower()
    print(f"\n  Wrote email: {wrote_email}")
    print(f"  Applied layers (reasoning): {applied_in_reasoning}")

    if not wrote_email:
        print("  VIOLATION: Model did not generate the email after confirmation!")
        with open(out, "w") as f:
            f.write("=== PROBE D — VIOLATION: No email generated after confirmation ===\n")
            for role, msg in history:
                f.write(f"\n--- {role} ---\n{msg.get('content','') if isinstance(msg,dict) else msg}\n")
        print(f"Results: {out}")
        return

    # --- Turn 3: User requests revision ---
    user_msg3 = "Make it a bit warmer, add a line about our support team being available."
    print(f"\n=== TURN 3: User revision request ===")
    print(user_msg3)
    history.append(("user", {"content": user_msg3}))
    resp = query(history)
    history.append(("assistant", resp))
    log("assistant (turn 3)", resp)

    content3 = resp["content"]
    has_support = "support" in content3.lower()
    asked_again = "?" in content3 and ("sound" in content3.lower() or "look" in content3.lower())
    print(f"\n  Has support mention: {has_support}")
    print(f"  Asked for confirmation again: {asked_again}")
    # Asking again is a slight issue — the skill says to regenerate and deliver, then loop.
    # The skill says "Regenerate with all three layers for changes. Repeat until done."
    # It should deliver the revision, not ask again.

    if not has_support:
        print("  WARNING: Revision may not have incorporated the support request")

    # --- Turn 4: Terminal state ---
    user_msg4 = "Looks good, thanks!"
    print(f"\n=== TURN 4: Terminal ===")
    print(user_msg4)
    history.append(("user", {"content": user_msg4}))
    resp = query(history)
    history.append(("assistant", resp))
    log("assistant (turn 4)", resp)

    content4 = resp["content"]
    terminal_ack = "welcome" in content4.lower() or "glad" in content4.lower() or "happy" in content4.lower() or "you're welcome" in content4.lower()
    print(f"\n  Terminal acknowledgment: {terminal_ack}")

    # --- Write results ---
    with open(out, "w") as f:
        f.write(f"=== PROBE D — MULTI-TURN INTERACTIVE: {ts} ===\n\n")
        for i, (role, msg) in enumerate(history):
            f.write(f"\n--- TURN {i//2 + 1} ({role}) ---\n")
            if isinstance(msg, dict):
                f.write(msg.get("content", ""))
                if msg.get("reasoning"):
                    f.write(f"\n\n[REASONING]\n{msg['reasoning']}")
            else:
                f.write(msg)
            f.write("\n")
        f.write(f"\n\n=== SUMMARY ===\n")
        f.write(f"Confirmation asked (turn 1): {asked_confirmation}\n")
        f.write(f"Email generated (turn 2): {wrote_email}\n")
        f.write(f"Layers applied (reasoning): {applied_in_reasoning}\n")
        f.write(f"Revision incorporated (turn 3): {has_support}\n")
        f.write(f"Terminal acknowledged (turn 4): {terminal_ack}\n")

    print(f"\n\nResults: {out}")
    print(f"  Confirmation asked: {asked_confirmation}")
    print(f"  Email generated: {wrote_email}")
    print(f"  Layers applied: {applied_in_reasoning}")
    print(f"  Terminal acknowledged: {terminal_ack}")

if __name__ == "__main__":
    run()
