# upload_results.py
import os
import json
import argparse
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import DlpFinding  # your declarative ORM class

def get_engine():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set. Put it in .env or export it.")
    return create_engine(db_url, pool_pre_ping=True)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--folder", default="dlp_results", help="Folder containing JSON artifacts")
    p.add_argument("--repo", required=True, help="Repository name (e.g. owner/repo)")
    return p.parse_args()

# inside map_json_to_model(...), add a new param 'tool' and pass it in - trufflehog 
# integration needs to be done soon
def map_json_to_model(payload: dict, file_path: str, repo: str, tool: str) -> DlpFinding:
    result = payload.get("result", {}) or {}
    flags  = result.get("flags", {}) or {}
    return DlpFinding(
        repo=repo,
        file_path=file_path,
        detector=tool,                       # 'ghostai' | 'gitleaks' | 'trufflehog'
        score=result.get("score", 0.0),
        reasons=result.get("breakdown"),
        severity=result.get("severity"),
        line_count=flags.get("line_count"),
        avg_line_len=flags.get("avg_line_len"),
        max_line_len=flags.get("max_line_len"),
    )


def iter_artifacts(folder: Path):
    """Yield absolute artifact paths under folder (recursively) ending with .json."""
    for p in folder.rglob("*.json"):
        if p.is_file():
            yield p

def artifact_to_file_path(artifact: Path, root_folder: Path) -> str:
    """
    dlp_results/pkg/file.py.json               -> pkg/file.py
    dlp_results/pkg/file.py.gitleaks.json      -> pkg/file.py
    dlp_results/pkg/file.py.trufflehog.json    -> pkg/file.py
    """
    rel = artifact.relative_to(root_folder)
    s = str(rel)
    for suf in (".gitleaks.json", ".trufflehog.json", ".json"):
        if s.endswith(suf):
            return s[: -len(suf)]
    return s

def main():
    args = parse_args()
    root = Path(args.folder)
    if not root.exists():
        print(f"[upload_results] No such folder: {root}")
        return

    engine = get_engine()
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    total_files = 0
    total_rows = 0

    with Session() as session:
        for artifact in iter_artifacts(root):
            total_files += 1
            try:
                data = json.loads(artifact.read_text())
            except json.JSONDecodeError:
                print(f"[upload_results] Skipping invalid JSON: {artifact}")
                continue

            file_path = artifact_to_file_path(artifact, root)

            # Handle either a single object or a list of objects
            objs = data if isinstance(data, list) else [data]
            tool = "ghostai"
            name = str(artifact.name)
            if name.endswith(".gitleaks.json"): tool = "gitleaks"
            elif name.endswith(".trufflehog.json"): tool = "trufflehog"

            rows = [map_json_to_model(obj, file_path, args.repo, tool) for obj in objs]

            session.add_all(rows)
            total_rows += len(rows)

        session.commit()

    print(f"[upload_results] Inserted {total_rows} row(s) from {total_files} artifact file(s).")

if __name__ == "__main__":
    main()