"""
Stage 2: Content Analysis
Shannon entropy and keyword density computation
"""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.data_structures import FileMetadata


class ContentAnalyzer:
    """
    Stage 2: Statistical text analysis
    Computes Shannon entropy H = -Σ p_i * log2(p_i) and keyword density
    """

    SENSITIVE_KEYWORDS = [
        'password', 'confidential', 'secret', 'private', 'classified',
        'proprietary', 'internal', 'restricted', 'financial', 'credit'
    ]

    def shannon_entropy(self, text: str) -> float:
        """
        Calculate Shannon entropy: H = -Σ p_i * log2(p_i)
        High entropy indicates encrypted/compressed data

        Args:
            text: Input text

        Returns:
            float: Entropy value (0-8 typical range)
        """
        if not text:
            return 0.0

        # Character frequency distribution
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        # Calculate entropy
        entropy = 0.0
        text_len = len(text)
        for count in freq.values():
            p_i = count / text_len
            entropy -= p_i * math.log2(p_i)

        return entropy

    def keyword_density(self, text: str) -> float:
        """
        Calculate density of sensitive keywords

        Returns:
            float: Percentage of sensitive keywords
        """
        text_lower = text.lower()
        words = text_lower.split()
        if not words:
            return 0.0

        keyword_count = sum(1 for word in words if word in self.SENSITIVE_KEYWORDS)
        return (keyword_count / len(words)) * 100  # percentage

    def analyze(self, file_meta) -> float:
        """
        Returns heuristic score (0-10) based on entropy and keywords

        Args:
            file_meta: FileMetadata object

        Returns:
            float: Content sensitivity score (0-10)
        """
        entropy = self.shannon_entropy(file_meta.content)
        keyword_dens = self.keyword_density(file_meta.content)

        # High entropy (>7.5) indicates encryption
        entropy_score = min(entropy / 7.5, 1.0) * 5
        # Keyword density contributes up to 5 points
        keyword_score = min(keyword_dens / 2.0, 1.0) * 5

        return entropy_score + keyword_score