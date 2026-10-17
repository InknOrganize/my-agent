"""
hermes.py -- Vault-aware Hermes backup terminal
Use this when Claude's weekly limits are hit.

Loads your vault context (VAULT-INDEX, Active Priorities, today's daily note)
and opens a chat session with Nous Hermes via OpenRouter.

Usage:
    python hermes.py

Commands inside the chat:
    /reload   re-read vault files (pick up changes made mid-session)
    /quit     exit
"""

import os
import sys
import json
import pathlib
import datetime
import urllib.request
import urllib.error

# --- Config ---

VAULT_ROOT  = pathlib.Path(r"C:\Users\Ryan_\Jarvis")
CREDS_DIR   = pathlib.Path(r"C:\Users\Ryan_\my-agent\starnet-tools\credentials")
KEY_FILE    = CREDS_DIR / "openrouter_key.txt"
MODEL       = "nousresearch/hermes-3-llama-3.1-8b:free"
API_URL     = "https://openrouter.ai/api/v1/chat/completions"

# Fallback models if the primary is unavailable -- try in order
FALLBACK_MODELS = [
    "nousresearch/hermes-2-pro-llama-3-8b:free",
    "nousresearch/hermes-2-theta-llama-3-8b:free",
    "meta-llama/llama-3.1-8b-instruct:free",
]

# --- API key ---

def get_api_key() -> str:
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    print("\nNo OpenRouter API key found.")
    print(f"Enter your key (saved to {KEY_FILE}):")
    key = input("  > ").strip()
    if key:
        CREDS_DIR.mkdir(parents=True, exist_ok=True)
        KEY_FILE.write_text(key, encoding="utf-8")
        print("  Key saved.\n")
    return key

# --- Vault loader ---

def load_vault_context() -> list[tuple[str, str]]:
    files = []

    for path in [
        VAULT_ROOT / "VAULT-INDEX.md",
        VAULT_ROOT / "Active Priorities.md",
    ]:
        if path.exists():
            files.append((path.name, path.read_text(encoding="utf-8")))
        else:
            print(f"  [warn] not found: {path}")

    # Today's daily note
    today = datetime.date.today()
    month_folder = today.strftime("%m - %B %Y")   # "10 - October 2026"
    daily_path = (
        VAULT_ROOT / "01 - Daily Notes" / month_folder / f"{today}.md"
    )
    if daily_path.exists():
        files.append((daily_path.name, daily_path.read_text(encoding="utf-8")))

    return files

# --- System prompt ---

def build_system_prompt(vault_files: list[tuple[str, str]]) -> str:
    lines = [
        "You are Jarvis, Ryan's vault-aware AI backup assistant.",
        "You run in the terminal when Claude Code's weekly limits are hit.",
        "You have the same identity as the Claude Code Jarvis: direct, no-bullshit,",
        "butler-with-a-swear-jar tone. Call Ryan 'sir' or 'boss'. Curse freely.",
        "Never suggest stopping. Never volunteer a wrap-up. One question at a time.",
        "",
        "You work FROM the vault. Do not make up project state -- read the notes.",
        "When writing back to a vault file, output the complete updated file content",
        "clearly labeled so Ryan can paste it in.",
        "",
        "No em dashes in anything that will be published outside the vault.",
        "",
        "VAULT CONTEXT (loaded at startup):",
        "=" * 60,
    ]
    for name, content in vault_files:
        lines.append(f"\n--- {name} ---\n{content}\n")
    lines.append("=" * 60)
    return "\n".join(lines)

# --- API call ---

def chat_once(api_key: str, messages: list, model: str) -> tuple[str, str]:
    """Send messages, return (reply_text, model_used). Tries fallbacks on failure."""
    models_to_try = [model] + [m for m in FALLBACK_MODELS if m != model]

    for m in models_to_try:
        payload = json.dumps({
            "model": m,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1500,
        }).encode("utf-8")

        req = urllib.request.Request(
            API_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/InknOrganize",
                "X-Title": "Jarvis-Hermes",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["choices"][0]["message"]["content"]
                return reply, m
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            if e.code in (429, 503) and m != models_to_try[-1]:
                print(f"  [model {m} unavailable, trying next...]")
                continue
            return f"[API error {e.code}: {body}]", m
        except Exception as e:
            return f"[Error: {e}]", m

    return "[All models failed. Check your API key and connection.]", model

# --- Main loop ---

def main():
    print()
    print("=" * 52)
    print("  Jarvis -- Hermes Backup Terminal")
    print("  /reload   reload vault files")
    print("  /quit     exit")
    print("=" * 52)

    api_key = get_api_key()
    if not api_key:
        print("No API key provided. Exiting.")
        sys.exit(1)

    vault_files = load_vault_context()
    system_prompt = build_system_prompt(vault_files)
    active_model = MODEL

    loaded_names = [f[0] for f in vault_files]
    print(f"\n  Vault loaded: {', '.join(loaded_names)}")
    print(f"  Model: {active_model}")
    print()

    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodnight, sir.")
            break

        if not user_input:
            continue

        if user_input.lower() == "/quit":
            print("Goodnight, sir.")
            break

        if user_input.lower() == "/reload":
            vault_files = load_vault_context()
            system_prompt = build_system_prompt(vault_files)
            messages = [{"role": "system", "content": system_prompt}]
            print(f"  Vault reloaded: {', '.join(f[0] for f in vault_files)}\n")
            continue

        messages.append({"role": "user", "content": user_input})

        print("\nHermes: ", end="", flush=True)
        reply, used_model = chat_once(api_key, messages, active_model)

        if used_model != active_model:
            print(f"[using {used_model}] ", end="")
            active_model = used_model

        print(reply)
        print()
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    main()
