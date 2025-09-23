from . import Detector
class BlobsDetector(Detector):
    """Token-ish blobs: long base64/base64url runs and JWT-like 3-segment tokens."""
    name = "blobs"