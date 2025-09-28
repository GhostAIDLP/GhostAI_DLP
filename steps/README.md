1. DB + Scanning

-Create scan_results + scan_breakdowns tables (repo, file, severity, score, flags, breakdowns).

-Add source column (ours, gitleaks, trufflehog).

-Create scan_labels table for TP/FP feedback.

-Run our scanner on full repo → ingest JSON into Postgres.

-Run Gitleaks + TruffleHog in parallel → normalize into same schema.

2. Consensus + Labeling

-Consensus: ≥2 tools flag → likely TP.

-Unique: 1 tool flag → needs review.

-Auto-suppress: FP labels apply across future runs by fingerprint.

-UI/CLI lets devs mark TP/FP.

-Store labels → suppress repeats → export dataset for analysis.

3. AI + Observability + Integration

-Analyze labeled data for weak detectors (e.g., entropy high FP rate).

-Train simple classifier (detector, entropy, line_count, keywords).

-Later: embeddings (pgvector) for similarity search → suggest FP/TP.

-Dashboard: TP/FP ratio, detector precision, repo severity, leak velocity.

-Drilldown: detector/repo findings.

-Integrate as post-SAST guardrail in pre-commit/CI (don’t replace SAST).

###
prev
###
Steps RN for DLP Project:

1. Automate DB creation by calling cli on prompts
2. Create prompts, we create to test edge cases and issue bury it fuzzy it, bullet proof
3. Failure == Good (Have AI give sus/obvious) -> DLP sus prompts and store the score
    - Steps DB + Automate + Log Results
    - Basic sleep and have it run

Final is gonna be integrating DLP in the pre commit pipeline!


Goal add to become a SAST guardrail, dont become a SAST hybrid but simply add a check after SAST scans to check for data leaks so run this on a sast scan and the