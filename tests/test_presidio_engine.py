def test_presidio_detects_ssn(analyzer):
    text = "My SSN is 123-45-6789"
    res = analyzer.analyze(text=text, language="en")
    entities = [r.entity_type for r in res]
    assert "US_SSN" in entities, f"Expected US_SSN, got {entities}"

def test_presidio_no_fp_on_normal_text(analyzer):
    text = "Hello world, we love burritos and unit tests."
    res = analyzer.analyze(text=text, language="en")
    assert len(res) == 0, f"Unexpected entities: {[(r.entity_type, r.score) for r in res]}"

def test_presidio_detects_phone_email(analyzer):
    text = "Call me at (415) 555-1212 or email me at test@example.com"
    res = analyzer.analyze(text=text, language="en")
    ents = {r.entity_type for r in res}
    assert {"PHONE_NUMBER", "EMAIL_ADDRESS"} & ents, f"Got: {ents}"
