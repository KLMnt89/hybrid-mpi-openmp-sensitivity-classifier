"""
Stage 1: Rule-Based Detection
DFA pattern matching for PII, financial data, confidential markers
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.data_structures import FileMetadata


class RuleBasedDetector:
    """
    Stage 1: Deterministic finite automata (DFA) for pattern matching
    """

    PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',  # Social Security Number
        'cc': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit Card
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'confidential': r'\b(confidential|secret|classified|restricted)\b',
    }

    def detect(self, file_meta) -> float:
        """
        Returns binary score: 10 if sensitive patterns found, 0 otherwise

        Args:
            file_meta: FileMetadata object

        Returns:
            float: 10.0 if sensitive, 0.0 otherwise
        """
        content_lower = file_meta.content.lower()

        for pattern_name, pattern in self.PATTERNS.items():
            if re.search(pattern, content_lower):
                return 10.0  # Definitive match

        return 0.0