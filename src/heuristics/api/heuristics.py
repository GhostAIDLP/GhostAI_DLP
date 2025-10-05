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

    def load_rules(self, name: str):        
        DATASETS = Path(__file__).resolve().parent.parent.parent / "datasets"

        with open(DATASETS / name, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("rules", [])

    def __init__(self):
        self.secret_rules  = self.load_rules("secret_risk.yaml")
        self.blob_rules    = self.load_rules("blob_risk.yaml")
        self.keyword_rules = self.load_rules("keyword_risk.yaml")
        self.code_risk_rules = self.load_rules("code_risk.yaml")

        self.detectors = [
            SecretsDetector(self.secret_rules),
            BlobsDetector(self.blob_rules),
            KeywordsDetector(self.keyword_rules),
            CodeRisksDetector(self.code_risk_rules),
            EntropyShapeDetector(BaseConfig.DEFAULTS),
        ]

        self.ENGINE = HeuristicsEngine(detectors=self.detectors, cfg=BaseConfig.DEFAULTS)


