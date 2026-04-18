"""
Stage 4: Entropy Calculation
Byte-frequency distributions and compression detection
"""

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.data_structures import FileMetadata


class EntropyCalculator:
    """
    Stage 4: Byte-level entropy and compression analysis
    """

    def byte_frequency_entropy(self, content: str) -> float:
        """
        Calculate entropy at byte level

        Returns:
            float: Byte-level entropy
        """
        if not content:
            return 0.0

        byte_array = content.encode('utf-8', errors='ignore')
        freq = {}
        for byte in byte_array:
            freq[byte] = freq.get(byte, 0) + 1

        entropy = 0.0
        total_bytes = len(byte_array)
        for count in freq.values():
            p_i = count / total_bytes
            entropy -= p_i * math.log2(p_i)

        return entropy

    def simulated_compression_ratio(self, content: str) -> float:
        """
        Simulate compression ratio
        Low ratio (<1.5) indicates already compressed/encrypted data

        Returns:
            float: Compression ratio (1.0-6.0)
        """
        unique_chars = len(set(content))
        total_chars = len(content)
        if total_chars == 0:
            return 1.0

        # Higher uniqueness = lower compression
        uniqueness = unique_chars / total_chars
        return 1.0 + (1.0 - uniqueness) * 5.0  # Range: 1.0 to 6.0

    def analyze(self, file_meta) -> float:
        """
        Returns encryption score (0-10)

        Args:
            file_meta: FileMetadata object

        Returns:
            float: Entropy-based sensitivity score (0-10)
        """
        byte_entropy = self.byte_frequency_entropy(file_meta.content)
        comp_ratio = self.simulated_compression_ratio(file_meta.content)

        # High byte entropy indicates encryption
        entropy_score = min(byte_entropy / 8.0, 1.0) * 7

        # Low compression ratio indicates encryption
        if comp_ratio < 1.5:
            comp_score = 3.0
        else:
            comp_score = 0.0

        return min(entropy_score + comp_score, 10.0)
