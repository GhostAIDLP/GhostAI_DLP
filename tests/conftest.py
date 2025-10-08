import pytest
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, Pattern, PatternRecognizer
from presidio_analyzer.nlp_engine import SpacyNlpEngine

@pytest.fixture(scope="session")
def spacy_engine():
    return SpacyNlpEngine(models={"en": "en_core_web_lg"})

@pytest.fixture(scope="session")
def recognizer_registry():
    reg = RecognizerRegistry()
    reg.load_predefined_recognizers()  # US_SSN, EMAIL_ADDRESS, PHONE_NUMBER, etc.
    # Belt & suspenders: force an SSN regex so demo never misses
    reg.add_recognizer(PatternRecognizer(
        supported_entity="US_SSN",
        patterns=[Pattern(name="us_ssn", regex=r"\b\d{3}-\d{2}-\d{4}\b", score=0.8)]
    ))
    return reg

@pytest.fixture(scope="session")
def analyzer(spacy_engine, recognizer_registry):
    return AnalyzerEngine(nlp_engine=spacy_engine, registry=recognizer_registry)
