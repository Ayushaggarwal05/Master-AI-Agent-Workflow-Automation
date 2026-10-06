import re
from typing import Any, List, Optional

def parse_delimited_list(
    value: Any, 
    custom_delimiters: Optional[List[str]] = None
) -> List[str]:
    """
    Parses a string or object from an Excel cell into a clean list of strings.
    Handles multiple delimiters (;, ,, \n, →, ->), numbered steps (1., 2.), 
    bullet points (•, -), and strips extraneous quotes/whitespace.
    """
    if value is None:
        return []
        
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
        
    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "null", "n/a"):
        return []

    # If steps are delimited by arrows (→, ->)
    if "→" in text or "->" in text:
        parts = re.split(r"\s*(?:→|->)\s*", text)
        result = []
        for part in parts:
            cleaned = clean_step_item(part)
            if cleaned:
                result.append(cleaned)
        return result

    # Check for newline-delimited items
    if "\n" in text:
        lines = text.split("\n")
        result = []
        for line in lines:
            cleaned = clean_step_item(line)
            if cleaned:
                result.append(cleaned)
        return result

    # Standard delimiters: semicolon or comma
    # If custom_delimiters are provided, use them
    if custom_delimiters:
        pattern = "|".join(re.escape(d) for d in custom_delimiters)
        tokens = re.split(pattern, text)
    elif ";" in text:
        tokens = text.split(";")
    elif "," in text:
        tokens = text.split(",")
    else:
        tokens = [text]

    result = []
    for token in tokens:
        cleaned = clean_token(token)
        if cleaned:
            result.append(cleaned)
            
    return result

def clean_token(token: str) -> str:
    """Cleans a single token by stripping whitespace, trailing dots, bullet points, and quotes."""
    cleaned = token.strip()
    # Strip leading bullet points (including unicode •, -, *, etc.) or numbers
    cleaned = re.sub(r"^[\s\u2022\u2023\u25E6\u2043\u2219•\-\*\d+\.\)]+", "", cleaned).strip()
    # Strip wrapping quotes
    cleaned = cleaned.strip("\"'").strip()
    return cleaned

def clean_step_item(item: str) -> str:
    """Cleans an individual workflow step string."""
    cleaned = item.strip()
    # Strip leading bullets, step numbers like '1.', 'Step 1:', '1)', or bullet points
    cleaned = re.sub(r"^(?:step\s*\d+[:\.\-]?|\d+[\.\)]\s*|[\s\u2022\u2023\u25E6\u2043\u2219•\-\*]+\s*)", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = cleaned.strip("\"'").strip()
    return cleaned
