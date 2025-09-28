import sys
import json
from src.cli.common import post_risk_sync, Metadata

def main():
    # Case 1: piped input
    if not sys.stdin.isatty():
        text = sys.stdin.read()
    # Case 2: passed as CLI args
    elif len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Usage:", file=sys.stderr)
        print("  echo 'code' | python3 -m src.cli.automate", file=sys.stderr)
        print("  python3 -m src.cli.automate 'some code snippet'", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print("Error: no text provided", file=sys.stderr)
        sys.exit(1)

    try:
        metadata = Metadata(source="automation", lang="en")
        result = post_risk_sync(
            text,
            tenant_id="default_tenant_id",
            call_back_url=None,
            metadata=metadata
        )
        print(json.dumps(result, indent=4))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
