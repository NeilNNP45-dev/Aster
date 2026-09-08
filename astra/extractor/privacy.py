"""Privacy filter enforcing strict exclusion of free-text and PII fields."""

from typing import Dict, Any, List
from astra.config import FORBIDDEN_TEXT_FIELDS


class PrivacyFilter:
    """Enforces privacy-first constraints on all extracted ML records."""

    @staticmethod
    def is_safe_field(field_name: str) -> bool:
        """Check if a field name is permitted (not a text/PII field)."""
        field_lower = field_name.lower().strip()
        return field_lower not in FORBIDDEN_TEXT_FIELDS

    @classmethod
    def sanitize_record(cls, record: Dict[str, Any]) -> Dict[str, Any]:
        """Strip any forbidden text or PII fields from a dictionary record."""
        sanitized = {}
        for key, val in record.items():
            if cls.is_safe_field(key):
                sanitized[key] = val
        return sanitized

    @classmethod
    def validate_dataset_schema(cls, columns: List[str]) -> bool:
        """Verify that a list of dataset column names contains zero forbidden text fields.
        
        Raises ValueError if a forbidden column is found.
        """
        for col in columns:
            if not cls.is_safe_field(col):
                raise ValueError(
                    f"Privacy Violation: Forbidden field '{col}' detected in dataset schema!"
                )
        return True
