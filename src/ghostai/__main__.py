"""
GhostAI SDK CLI 🧠
Run interactive scans directly from your terminal.

Usage:
    python -m ghostai
    python -m ghostai "scan this text"
"""

import sys
import json
from ghostai.cli.common import post_risk_sync, Metadata  # ← adjust import if needed

def main():
    # If arguments are passed (non-interactive mode)
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        metadata = Metadata(source="cli", lang="en")
        print("🔍 Running GhostAI pipeline...\n")

        try:
            result = post_risk_sync(
                text,
                tenant_id="default_tenant_id",
                call_back_url=None,
                metadata=metadata
            )
            print(json.dumps(result, indent=4))
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
        return

    # Otherwise, start interactive REPL-style CLI
    print("💬 GhostAI Interactive CLI (type 'exit' to quit)\n")

    while True:
        try:
            user_input = input("Enter text to scan: ")
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Exiting GhostAI CLI.")
            break

        if user_input.strip().lower() in ("exit", "quit"):
            print("👋 Exiting GhostAI CLI.")
            break

        if not user_input.strip():
            continue

        metadata = Metadata(source="interactive", lang="en")

        try:
            result = post_risk_sync(
                user_input,
                tenant_id="default_tenant_id",
                call_back_url=None,
                metadata=metadata
            )
            print("\n🧾 Result:")
            print(json.dumps(result, indent=4))
        except Exception as e:
            print(f"❌ Failed to scan: {e}", file=sys.stderr)
        print("\n---\n")

if __name__ == "__main__":
    main()
