class BaseConfig(object):
    DEFAULTS = {
        "max_input_len": 10_000,
        "severity_thresholds": {"high": 0.80, "medium": 0.50},
        "reason_limit": 5,
        "entropy_len_min": 40,
        "entropy_cutoff": 3.5,
        "entropy_weight": 0.25,
        "long_line_len": 200,
        "shape_weight": 0.15,
        "max_reasons_per_detector": 3
    }

    HIGH_SEVERITY: int = 0.8
    MEDIUM_SEVERITY: int = 0.5
    LOW_SEVERITY: int = 0.0
