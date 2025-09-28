Steps RN for DLP Project:

1. Automate DB creation by calling cli on prompts
2. Create prompts, we create to test edge cases and issue bury it fuzzy it, bullet proof
3. Failure == Good (Have AI give sus/obvious) -> DLP sus prompts and store the score
    - Steps DB + Automate + Log Results
    - Basic sleep and have it run

Final is gonna be integrating DLP in the pre commit pipeline!


Goal add to become a SAST guardrail, dont become a SAST hybrid but simply add a check after SAST scans to check for data leaks so run this on a sast scan and the