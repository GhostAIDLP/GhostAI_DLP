# ghostai/__main__.py
"""
GhostAI SDK CLI 🧰
Run scans or test proxy locally.
Usage:
    python -m ghostai "scan this text"
"""

import sys
from .pipeline.pipeline import Pipeline

def main():
    # read text from command line
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "Sensitive data example: API_KEY=abcd1234"

    # init scanner pipeline
    pipeline = Pipeline(profile="runtime")

    print("🔍 Running GhostAI pipeline...\n")
    res = pipeline.run(text)

    print(f"Score: {res['score']}")
    print(f"Flags: {res['flags']}")
    print("\nBreakdown:")
    for b in res["breakdown"]:
        print(f"  - {b}")

if __name__ == "__main__":
    main()
