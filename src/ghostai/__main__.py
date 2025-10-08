"""
GhostAI SDK CLI 🧠
Run interactive scans directly from your terminal.

Usage:
    python -m ghostai
    python -m ghostai "scan this text"
"""

import sys
import json
from ghostai.pipeline.pipeline import Pipeline

def main():
    # If arguments are passed (non-interactive mode)
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print("🔍 Running GhostAI pipeline...\n")

        try:
            pipeline = Pipeline()
            result = pipeline.run(text)
            print(json.dumps(result, indent=4))
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
        return

    # Otherwise, start interactive REPL-style CLI
    print("💬 GhostAI Interactive CLI (type 'exit' to quit)\n")

    try:
        pipeline = Pipeline()
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {e}", file=sys.stderr)
        return

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

        try:
            result = pipeline.run(user_input)
            print("\n🧾 Result:")
            print(json.dumps(result, indent=4))
        except Exception as e:
            print(f"❌ Failed to scan: {e}", file=sys.stderr)
        print("\n---\n")

if __name__ == "__main__":
    main()
