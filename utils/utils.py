import json
from typing import Any, Dict


def parse_ai_json(raw_input: str) -> Dict[str, Any]:
    """
    Strip Markdown code fences (```json or ```) from AI output and parse JSON.
    Raises json.JSONDecodeError if parsing fails.
    """
    if raw_input is None:
        raise TypeError("raw_input must be a string")
    s = raw_input.strip()
    if s.startswith("```json"):
        s = s[len("```json"):].replace("```", "").strip()
    elif s.startswith("```"):
        s = s.replace("```", "").strip()
    return json.loads(s)
