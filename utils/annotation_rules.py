# DOCMINDER/utils/annotation_rules.py

import os
import re
from typing import Dict, Any, Optional


# Regex for standard Indian statute header: "THE <NAME> ACT, <YEAR>"
_ACT_HEADER_RE = re.compile(r"THE\s+([A-Z][A-Z\s,]+?)\s+ACT,?\s+(\d{4})")


def extract_legal_metadata(
    text: str,
    source_filename: str,
    doc_header_text: str = "",
    page: Optional[int] = None,
) -> Dict[str, Any]:
    """Extracts legal-specific metadata from text to enrich chunks.

    Args:
        text: The chunk text content.
        source_filename: Original document filename / path.
        doc_header_text: First-page text of the document (used once per
            document to detect act name via regex).
        page: 1-indexed page number, for logging purposes only.
    """
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

    # --- Act name detection ---
    # 1. Try regex on the document's first-page text (most reliable)
    act_detected = False
    if doc_header_text:
        match = _ACT_HEADER_RE.search(doc_header_text.upper())
        if match:
            act_name_raw = match.group(1).strip()
            act_year = match.group(2).strip()
            metadata["act_name"] = f"The {act_name_raw.title()} Act, {act_year}"
            metadata["act_year"] = act_year
            act_detected = True

    # 2. Fall back to filename-substring check
    if not act_detected:
        lower_filename = source_filename.lower()
        if "motor vehicles act" in lower_filename:
            metadata["act_name"] = "Motor Vehicles Act, 1988"
            metadata["act_year"] = "1988"
        elif "trade marks act" in lower_filename:
            metadata["act_name"] = "Trade Marks Act, 1999"
            metadata["act_year"] = "1999"
        # ... additional filename-based fallbacks can go here ...

    # --- Extract specific identifiers from the chunk text ---
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
