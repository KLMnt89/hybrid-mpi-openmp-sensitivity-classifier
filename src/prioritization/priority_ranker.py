"""
Priority Ranker
Implements disaster recovery prioritization based on sensitivity, criticality, and recency
Formula: P = w_s * S_norm + w_c * C + w_r * R
"""

import time
import math
from typing import List
from ..utils.data_structures import ClassificationResult, FileMetadata


class PriorityRanker:
    """
    Disaster Recovery Priority Ranker

    Combines multiple factors to determine recovery priority:
    - Sensitivity score (normalized)
    - Business criticality (file type, directory)
    - Recency factor (recently modified files prioritized)

    Formula: P = w_s * S_norm + w_c * C + w_r * R
    """

    def __init__(self, w_sensitivity: float = 0.45, w_criticality: float = 0.35, w_recency: float = 0.20):
        """
        Args:
            w_sensitivity: Weight for sensitivity score (default: 0.45)
            w_criticality: Weight for business criticality (default: 0.35)
            w_recency: Weight for recency factor (default: 0.20)
        """
        self.w_sensitivity = w_sensitivity
        self.w_criticality = w_criticality
        self.w_recency = w_recency

    def compute_criticality(self, file_meta: FileMetadata) -> float:
        """
        Compute business criticality score based on file type and directory

        Args:
            file_meta: File metadata

        Returns:
            float: Criticality score (0-1)
        """
        score = 0.5  # Base score

        # Critical directories
        critical_paths = ['/financial/', '/legal/', '/executive/', '/database/', '/backup/']
        for path in critical_paths:
            if path in file_meta.path.lower():
                score += 0.3
                break

        # Critical file types (based on extension simulation)
        if 'database' in file_meta.filename or 'backup' in file_meta.filename:
            score += 0.2

        return min(score, 1.0)

    def compute_recency(self, modified_time: float) -> float:
        """
        Compute recency factor using exponential decay
        R = e^(-λ * Δt) where Δt is days since modification

        Args:
            modified_time: Last modification timestamp (Unix epoch)

        Returns:
            float: Recency factor (0-1)
        """
        days_old = (time.time() - modified_time) / 86400  # Convert to days
        lambda_decay = 0.01  # Decay constant
        recency_factor = math.exp(-lambda_decay * days_old)
        return recency_factor

    def compute_priority(self, classification_result: ClassificationResult, file_meta: FileMetadata) -> float:
        """
        Compute overall priority score
        P = w_s * S_norm + w_c * C + w_r * R

        Args:
            classification_result: Result from classification pipeline
            file_meta: Original file metadata

        Returns:
            float: Priority score (0-1)
        """
        # Normalize sensitivity score (0-10 → 0-1)
        s_norm = classification_result.final_score / 10.0

        # Compute criticality
        criticality = self.compute_criticality(file_meta)

        # Compute recency
        recency = self.compute_recency(file_meta.modified_time)

        # Weighted combination
        priority = (
                self.w_sensitivity * s_norm +
                self.w_criticality * criticality +
                self.w_recency * recency
        )

        return priority

    def rank_files(self, classification_results: List[ClassificationResult],
                   file_metadata: List[FileMetadata]) -> List[tuple]:
        """
        Rank files by priority for disaster recovery

        Args:
            classification_results: List of classification results
            file_metadata: List of original file metadata

        Returns:
            List of tuples: (filename, priority_score, sensitivity_level)
            Sorted by descending priority
        """
        ranked = []

        for result, meta in zip(classification_results, file_metadata):
            priority = self.compute_priority(result, meta)
            ranked.append((
                result.filename,
                priority,
                result.sensitivity_level.name,
                result.final_score
            ))

        # Sort by priority (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)

        return ranked