import requests
import json
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
from json import JSONEncoder

class Metadata(BaseModel):
    source: str
    lang: str

class CustomJSONEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Metadata):
            return o.model_dump()
        return super().default(o)

def get_heuristics_data(text: str, tenant_id: Optional[str] = None, call_back_url: Optional[str] = None, metadata: Optional[Metadata] = None):
    if not text:
        raise ValueError("Text is a required parameter")

    url = "http://127.0.0.1:5000/risk:sync"
    headers = {"Content-Type": "application/json"}
    data = {
        "text": text,
        "tenant_id": tenant_id or "default_tenant_id",
        "call_back_url": call_back_url or None,
        "metadata": metadata or Metadata(source="chatgpt", lang="en").model_dump()
    }

    response = requests.post(url, headers=headers, data=json.dumps(data, cls=CustomJSONEncoder))
    if response.status_code == 200:
        return response.json()
    else:
        return None


def main():
    while True:
        lines = []
        prompt = input("Enter a code prompt: ")
        if not prompt:
            continue

        lines.append(prompt)
        while True:
            next_line = input("Enter the next line (or press Enter to submit): ")
            if not next_line:
                break
            lines.append(next_line)

        text = "\n".join(lines)
        call_back_url = lines[2].strip() if len(lines) > 2 else None
        metadata = Metadata(source="chatgpt", lang="en")

        if not text:
            print("Text is a required parameter")
            continue

        response = get_heuristics_data(text, tenant_id="default_tenant_id", call_back_url=call_back_url, metadata=metadata)
        if response:
            print(json.dumps(response, indent=4))
        else:
            print("Failed to get heuristics data")

if __name__ == "__main__":
    main()