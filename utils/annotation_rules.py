# DOCMINDER/utils/annotation_rules.py

import os
import re
from typing import Dict, Any

def extract_legal_metadata(text: str, source_filename: str) -> Dict[str, Any]:
    """Extracts legal-specific metadata from text to enrich chunks."""
    metadata = {
        "source": os.path.basename(source_filename),
        "act_name": "N/A",
        "jurisdiction": "India",
        "rule_reference": "N/A",
        "main_point": "N/A",
        "section_number": "N/A",
        "chapter_name": "N/A",
        "act_year": "N/A",
    }

    # Infer act name from filename (add more rules as needed)
    lower_filename = source_filename.lower()
    if "motor vehicles act" in lower_filename:
        metadata["act_name"] = "Motor Vehicles Act, 1988"
        metadata["act_year"] = "1988"
    elif "trade marks act" in lower_filename:
        metadata["act_name"] = "Trade Marks Act, 1999"
        metadata["act_year"] = "1999"
    # ... add other filename-based rules from your original file ...

    # Extract specific identifiers from the chunk text
    section_match = re.search(r"(Section|Sec\.)\s*(\d+)", text, re.IGNORECASE)
    if section_match:
        metadata["section_number"] = section_match.group(0).strip()

    chapter_match = re.search(r"CHAPTER (\w+|[IVXLCDM]+)", text)
    if chapter_match:
        metadata["chapter_name"] = "Chapter " + chapter_match.group(1).strip()

    rule_match = re.search(r"(Rule)\s*(\d+)", text, re.IGNORECASE)
    if rule_match:
        metadata["rule_reference"] = rule_match.group(0).strip()

    return metadata
