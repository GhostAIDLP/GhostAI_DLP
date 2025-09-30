import json, argparse
from pathlib import Path

def ensure_parent(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

def payload(tool, file_path, reasons, score=None, severity=None):
    return {
        "file": file_path,
        "result": {
            "breakdown": [
                {"name": tool, "reasons": reasons, "score": float(score or 0)}
            ],
            "flags": {
                "line_count": None, "avg_line_len": None, "max_line_len": None,
                "orig_len": None, "truncated": False
            },
            "latency_ms": 0.0,
            "request_id": tool,
            "score": float(score or 0),
            "severity": severity or "medium",
        },
    }

def write(out_dir: Path, file_path: str, tool: str, obj: dict):
    out = out_dir / f"{file_path}.{tool}.json"  # e.g., dlp_results/src/app.py.gitleaks.json
    ensure_parent(out)
    out.write_text(json.dumps(obj))

def normalize_gitleaks(gitleaks_path: Path, out_dir: Path) -> int:
    if not gitleaks_path or not gitleaks_path.exists():
        return 0
    raw = gitleaks_path.read_text() or "[]"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = []
    leaks = data.get("leaks") if isinstance(data, dict) else data
    n = 0
    for leak in leaks or []:
        fp = leak.get("File") or leak.get("file") or leak.get("Path") or "unknown"
        rule = (
            leak.get("RuleID")
            or leak.get("Rule")
            or leak.get("Description")
            or "rule"
        )
        match = leak.get("Match") or leak.get("Secret") or ""
        line = leak.get("StartLine") or leak.get("Line") or ""
        obj = payload(
            "gitleaks",
            fp,
            [f"rule={rule}", f"match={match}", f"line={line}"],
            score=1.0,
            severity="high",
        )
        write(out_dir, fp, "gitleaks", obj)
        n += 1
    return n


def _iter_trufflehog_objects(th_path: Path):
    """Yield JSON objects from TruffleHog output (supports JSONL or JSON array)."""
    text = th_path.read_text().strip()
    if not text:
        return
    if text.startswith("["):
        try:
            arr = json.loads(text)
            for o in arr:
                if isinstance(o, dict):
                    yield o
        except json.JSONDecodeError:
            return
    else:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
                if isinstance(o, dict):
                    yield o
            except json.JSONDecodeError:
                continue


def normalize_trufflehog(th_path: Path, out_dir: Path) -> int:
    if not th_path or not th_path.exists():
        return 0
    n = 0
    for o in _iter_trufflehog_objects(th_path):
        data = o.get("SourceMetadata", {}).get("Data", {})
        fs = data.get("Filesystem", {})
        git = data.get("Git", {})
        fp = fs.get("file") or git.get("file") or o.get("Path") or "unknown"
        ln = fs.get("line") or git.get("line") or o.get("Line") or ""
        det = o.get("DetectorName") or str(o.get("DetectorType", "trufflehog"))
        ver = bool(o.get("Verified"))
        red = o.get("Redacted") or o.get("Raw") or ""
        sev = "high" if ver else "medium"
        score = 1.0 if ver else 0.8
        obj = payload(
            "trufflehog",
            fp,
            [f"detector={det}", f"verified={ver}", f"line={ln}", f"sample={red}"],
            score=score,
            severity=sev,
        )
        write(out_dir, fp, "trufflehog", obj)
        n += 1
    return n

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gitleaks", default="")
    ap.add_argument("--trufflehog", default="")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    g = normalize_gitleaks(Path(args.gitleaks), out_dir) if args.gitleaks else 0
    t = normalize_trufflehog(Path(args.trufflehog), out_dir) if args.trufflehog else 0
    print(f"[normalize] gitleaks={g}, trufflehog={t}")

if __name__ == "__main__":
    main()
