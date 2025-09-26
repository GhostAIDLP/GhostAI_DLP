# api/heuristics.py (loader + engine wiring)
from pathlib import Path
import yaml
from heuristics.engine import HeuristicsEngine
from heuristics.detectors.secrets import SecretsDetector
from heuristics.detectors.blobs import BlobsDetector
from heuristics.detectors.keywords import KeywordsDetector
from heuristics.detectors.entropy_shape import EntropyShapeDetector
from heuristics.detectors.code_risks import CodeRisksDetector
from heuristics.config import BaseConfig

class Heuristics(object):

    def load_rules(name: str):        
        DATASETS = Path(__file__).resolve().parent.parent.parent / "datasets"

        with open(DATASETS / name, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("rules", [])

    secret_rules  = load_rules("secret_risk.yaml")
    blob_rules    = load_rules("blob_risk.yaml")
    keyword_rules = load_rules("keyword_risk.yaml")
    code_risk_rules = load_rules("code_risk.yaml")

    detectors = [
        SecretsDetector(secret_rules),
        BlobsDetector(blob_rules),
        KeywordsDetector(keyword_rules),
        CodeRisksDetector(code_risk_rules),
        EntropyShapeDetector(BaseConfig.DEFAULTS),
    ]

    ENGINE = HeuristicsEngine(detectors=detectors, cfg=BaseConfig.DEFAULTS)


