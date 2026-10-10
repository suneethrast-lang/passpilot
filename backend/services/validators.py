
import re
import unicodedata
from datetime import date


def normalize_name(value):
    """Normalize a name for a basic consistency comparison."""
    if not isinstance(value, str) or not value.strip():
        return ""

    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        char for char in value
        if not unicodedata.combining(char)
    )
    value = value.casefold()
    value = re.sub(r"[^\w\s]", " ", value)
    return " ".join(value.split())


def normalize_date(value):
    """Accept valid YYYY-MM-DD dates only."""
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return date.fromisoformat(value.strip()).isoformat()
    except ValueError:
        return None


def compare_field(documents, field, normalizer):
    """Compare one field across documents."""
    values = []

    for document in documents:
        fields = document.get("fields", {})
        raw_value = fields.get(field)
        normalized = normalizer(raw_value)

        if normalized:
            values.append({
                "document": document.get("type", "unknown"),
                "value": raw_value.strip()
                if isinstance(raw_value, str)
                else raw_value,
                "normalized": normalized,
            })

    if len(values) < 2:
        return {
            "check": field,
            "status": "insufficient_data",
            "reason": "At least two documents with this field are needed.",
            "next_action": "Provide the missing field information.",
        }

    distinct = {item["normalized"] for item in values}

    if len(distinct) == 1:
        return {
            "check": field,
            "status": "match",
            "reason": "The provided values are consistent.",
            "next_action": "Continue the readiness review.",
        }

    return {
        "check": field,
        "status": "review_required",
        "values": [
            {
                "document": item["document"],
                "value": item["value"],
            }
            for item in values
        ],
        "reason": "The provided values differ and need review.",
        "next_action": (
            "Check the original documents and applicable official guidance."
        ),
    }


def validate_documents(payload):
    """Validate extracted fields without claiming document authenticity."""
    documents = payload.get("documents", [])

    if not isinstance(documents, list):
        raise ValueError("'documents' must be a list.")

    if not all(isinstance(doc, dict) for doc in documents):
        raise ValueError("Each document must be an object.")

    for document in documents:
        if not isinstance(document.get("fields", {}), dict):
            raise ValueError("Each document's 'fields' must be an object.")

    checks = [
        compare_field(documents, "name", normalize_name),
        compare_field(documents, "date_of_birth", normalize_date),
    ]

    review_needed = any(
        check["status"] == "review_required"
        for check in checks
    )

    insufficient = any(
        check["status"] == "insufficient_data"
        for check in checks
    )

    return {
        "case_id": payload.get("case_id", "DEMO-001"),
        "checks": checks,
        "requires_human_review": review_needed,
        "has_insufficient_data": insufficient,
        "disclaimer": (
            "This checks consistency of supplied fields only. "
            "It does not verify authenticity, legal eligibility, "
            "or guarantee passport approval."
        ),
    }
