import json
from json import JSONEncoder
from typing import Any, Optional
import requests
from pydantic import BaseModel

class Metadata(BaseModel):
    source: str
    lang: str

class CustomJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Metadata):
            return o.model_dump()
        return super().default(o)

def post_risk_sync(
    text: str,
    tenant_id: Optional[str] = None,
    call_back_url: Optional[str] = None,
    metadata: Optional[Metadata] = None,
    url: str = "http://127.0.0.1:5000/risk:sync",
):
    """
    Send text to the risk:sync API and return the parsed JSON.
    Raises RuntimeError on non-200 responses.
    """
    if not text or not text.strip():
        raise ValueError("text is required")

    payload = {
        "text": text,
        "tenant_id": tenant_id or "default_tenant_id",
        "call_back_url": call_back_url,
        "metadata": (
            metadata.model_dump() if isinstance(metadata, Metadata) else metadata
        ) or {"source": "automation", "lang": "en"},
    }

    resp = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload, cls=CustomJSONEncoder),
    )
    if resp.status_code == 200:
        return resp.json()
    else:
        raise RuntimeError(f"Request failed [{resp.status_code}]: {resp.text}")
