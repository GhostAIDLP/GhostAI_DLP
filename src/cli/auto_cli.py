import sys
import json
import os
from src.cli.common import post_risk_sync, Metadata

# Max file size to scan (500 KB default)
MAX_SIZE = 500_000  

def main():
    # Case 1: piped input (e.g., cat file.py | python -m src.cli.auto_cli)
    if not sys.stdin.isatty():
        text = sys.stdin.read()
        filename = os.environ.get("firewall_FILENAME", "stdin")
    # Case 2: passed as CLI args
    elif len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        filename = "args"
    else:
        print("Usage:", file=sys.stderr)
        print("  echo 'code' | python3 -m src.cli.auto_cli", file=sys.stderr)
        print("  python3 -m src.cli.auto_cli 'some code snippet'", file=sys.stderr)
        sys.exit(1)

    if not text.strip():
        print(json.dumps({
            "file": filename,
            "error": "no text provided"
        }))
        sys.exit(1)

    if len(text) > MAX_SIZE:
        print(json.dumps({
            "file": filename,
            "error": f"file too large ({len(text)} bytes, max {MAX_SIZE})"
        }))
        sys.exit(0)

    try:
        metadata = Metadata(source="automation", lang="en")
        result = post_risk_sync(
            text,
            tenant_id="default_tenant_id",
            call_back_url=None,
            metadata=metadata
        )
        output = {
            "file": filename,
            "result": result
        }
        print(json.dumps(output, indent=4))
    except Exception as e:
        print(json.dumps({
            "file": filename,
            "error": str(e)
        }, indent=4))
        sys.exit(2)

if __name__ == "__main__":
    main()
