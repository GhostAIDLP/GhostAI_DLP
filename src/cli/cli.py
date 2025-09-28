import sys
import json
from .common import post_risk_sync, Metadata

def main():
    try:
        while True:
            lines = []
            try:
                prompt = input("Enter a code prompt (or type 'exit' to quit): ")
            except EOFError:
                print("\nEOF received — exiting.")
                break

            if prompt is None:
                continue
            if prompt.strip().lower() in ("exit", "quit"):
                print("Exiting.")
                break
            if not prompt:
                continue

            lines.append(prompt)
            while True:
                try:
                    next_line = input("Enter the next line (or press Enter to submit): ")
                except EOFError:
                    print("\nEOF received — submitting current block.")
                    next_line = ""
                if not next_line:
                    break
                if next_line.strip().lower() in ("exit", "quit"):
                    print("Exiting.")
                    return
                lines.append(next_line)

            text = "\n".join(lines)
            call_back_url = lines[2].strip() if len(lines) > 2 else None
            metadata = Metadata(source="chatgpt", lang="en")

            if not text.strip():
                print("Text is a required parameter")
                continue

            try:
                result = post_risk_sync(
                    text,
                    tenant_id="default_tenant_id",
                    call_back_url=call_back_url,
                    metadata=metadata,
                )
                print(json.dumps(result, indent=4))
            except Exception as e:
                print(f"Failed to get heuristics data: {e}", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received — exiting.")
        return

if __name__ == "__main__":
    main()
