"""
claude-a2a-server.py -- Claude Code A2A endpoint

Exposes Claude (Sonnet via OpenRouter) as an A2A-compatible agent on localhost
so Hermes can delegate tasks to Claude using a2a_call / a2a_discover.

Usage:
    python claude-a2a-server.py [--port 8643]

Uses OpenRouter key from:
    C:\\Users\\Ryan_\\my-agent\\starnet-tools\\credentials\\openrouter_key.txt
or OPENROUTER_API_KEY environment variable.
"""

import json
import pathlib
import http.server
import urllib.request
import argparse
import os
import sys

PORT      = 8643
MODEL     = "anthropic/claude-sonnet-4-6"
API_URL   = "https://openrouter.ai/api/v1/chat/completions"
KEY_FILE  = pathlib.Path(r"C:\Users\Ryan_\my-agent\starnet-tools\credentials\openrouter_key.txt")

AGENT_CARD = {
    "name": "Claude Code — Jarvis Primary",
    "description": (
        "Claude Sonnet 4.6 running as the primary Jarvis agent in Claude Code. "
        "Handles vault work, code, writing, analysis, and strategic tasks."
    ),
    "url": f"http://127.0.0.1:{PORT}",
    "version": "1.0.0",
    "provider": {"organization": "Anthropic", "url": "https://anthropic.com"},
    "capabilities": {"streaming": False},
    "skills": [
        {
            "id": "general",
            "name": "General reasoning and task execution",
            "description": "Any task — reasoning, code, writing, vault notes, strategy.",
        }
    ],
}

SYSTEM_PROMPT = (
    "You are Jarvis, Ryan's primary AI agent running as Claude Sonnet in Claude Code. "
    "You are receiving a delegated task from Hermes Agent (the backup Jarvis instance). "
    "Be direct and complete. Return the finished result, not a plan."
)


def get_api_key() -> str:
    if KEY_FILE.exists():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
    return os.environ.get("OPENROUTER_API_KEY", "").strip()


def call_claude(text: str) -> str:
    api_key = get_api_key()
    if not api_key:
        return "[Error: No OpenRouter API key found at credentials/openrouter_key.txt]"

    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": text},
        ],
        "max_tokens": 2000,
        "temperature": 0.3,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization":  f"Bearer {api_key}",
            "Content-Type":   "application/json",
            "HTTP-Referer":   "https://github.com/InknOrganize",
            "X-Title":        "Jarvis-Claude-A2A",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.request.HTTPError as e:
        body = e.read().decode(errors="replace")
        return f"[API error {e.code}: {body[:200]}]"
    except Exception as e:
        return f"[Error: {e}]"


def extract_text(params: dict) -> str:
    """Pull plain text out of an A2A message params block."""
    message = params.get("message", {})
    parts   = message.get("parts", [])
    if parts:
        return " ".join(p.get("text", "") for p in parts if p.get("type") == "text")
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(params)


class A2AHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"  [{self.address_string()}] {fmt % args}", flush=True)

    def send_json(self, code: int, body: dict):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/.well-known/agent-card.json", "/agent.json"):
            self.send_json(200, AGENT_CARD)
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw    = self.rfile.read(length)

        try:
            req = json.loads(raw)
        except json.JSONDecodeError:
            self.send_json(400, {
                "jsonrpc": "2.0", "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            })
            return

        req_id = req.get("id")
        params = req.get("params", {})
        text   = extract_text(params)

        if not text:
            self.send_json(200, {
                "jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32602, "message": "No text content in message"},
            })
            return

        preview = text[:100] + ("..." if len(text) > 100 else "")
        print(f"\n  >> Task from Hermes: {preview}", flush=True)

        reply = call_claude(text)

        print(f"  << Reply: {reply[:100]}{'...' if len(reply) > 100 else ''}\n", flush=True)

        self.send_json(200, {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "id":     params.get("id", "task-1"),
                "status": {"state": "completed"},
                "artifacts": [
                    {"parts": [{"type": "text", "text": reply}]}
                ],
            },
        })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Claude Code A2A server")
    parser.add_argument("--port", type=int, default=PORT, help=f"Port to listen on (default: {PORT})")
    args = parser.parse_args()

    AGENT_CARD["url"] = f"http://127.0.0.1:{args.port}"

    server = http.server.HTTPServer(("127.0.0.1", args.port), A2AHandler)
    print(f"\nClaude Code A2A server running on http://127.0.0.1:{args.port}")
    print(f"Agent card:  http://127.0.0.1:{args.port}/.well-known/agent-card.json")
    print("Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        sys.exit(0)
