"""
Classification Pipeline
Orchestrates 4-stage classification with fusion logic
Implements: S = max(S_rule, α*S_content + β*S_metadata + γ*S_entropy)
"""

import time
import math
from concurrent.futures import ThreadPoolExecutor

from .rule_based import RuleBasedDetector
from .content_analysis import ContentAnalyzer
from .metadata_scoring import MetadataScorer
from .entropy_calc import EntropyCalculator
from ..utils.data_structures import FileMetadata, ClassificationResult, SensitivityLevel


class ClassificationPipeline:
    """
    Orchestrates the 4-stage classification pipeline

    Implements the hybrid scoring formula from Solution Architecture:
    S = max(S_rule, α*S_content + β*S_metadata + γ*S_entropy)

    Args:
        alpha: Weight for content analysis (default: 0.4)
        beta: Weight for metadata scoring (default: 0.35)
        gamma: Weight for entropy calculation (default: 0.25)
    """

    def __init__(self, alpha: float = 0.4, beta: float = 0.35, gamma: float = 0.25):
        self.rule_detector = RuleBasedDetector()
        self.content_analyzer = ContentAnalyzer()
        self.metadata_scorer = MetadataScorer()
        self.entropy_calculator = EntropyCalculator()

        # Weights for heuristic stages
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def classify_file(self, file_meta: FileMetadata) -> ClassificationResult:
        """
        Execute all 4 stages sequentially and compute final sensitivity score

        Args:
            file_meta: File metadata to classify

        Returns:
            ClassificationResult with scores and classification
        """
        start_time = time.time()

        # Stage 1: Rule-based detection
        rule_score = self.rule_detector.detect(file_meta)

        # Stage 2: Content analysis
        content_score = self.content_analyzer.analyze(file_meta)

        # Stage 3: Metadata scoring
        metadata_score = self.metadata_scorer.analyze(file_meta)

        # Stage 4: Entropy calculation
        entropy_score = self.entropy_calculator.analyze(file_meta)

        # Fusion: S = max(S_rule, α*S_content + β*S_metadata + γ*S_entropy)
        heuristic_score = (
                self.alpha * content_score +
                self.beta * metadata_score +
                self.gamma * entropy_score
        )
        final_score = max(rule_score, heuristic_score)

        # Threshold-based mapping to sensitivity levels
        if final_score < 3.0:
            level = SensitivityLevel.PUBLIC
        elif final_score < 6.0:
            level = SensitivityLevel.INTERNAL
        elif final_score < 8.5:
            level = SensitivityLevel.CONFIDENTIAL
        else:
            level = SensitivityLevel.SECRET

        # Priority score for disaster recovery
        # P = w_s * S_norm + w_r * R (simplified)
        days_old = (time.time() - file_meta.modified_time) / 86400
        recency_factor = math.exp(-0.01 * days_old)
        priority_score = 0.6 * (final_score / 10.0) + 0.4 * recency_factor

        processing_time = time.time() - start_time

        return ClassificationResult(
            filename=file_meta.filename,
            rule_score=rule_score,
            content_score=content_score,
            metadata_score=metadata_score,
            entropy_score=entropy_score,
            final_score=final_score,
            sensitivity_level=level,
            priority_score=priority_score,
            processing_time=processing_time
        )

    def classify_with_threading(self, file_meta: FileMetadata, num_threads: int = 4) -> ClassificationResult:
        """
        Execute 4 stages in parallel using OpenMP simulation (ThreadPoolExecutor)

        Args:
            file_meta: File metadata to classify
            num_threads: Number of threads (simulates OpenMP threads)

        Returns:
            ClassificationResult with scores and classification
        """
        start_time = time.time()

        scores = {}

        def stage1():
            scores['rule'] = self.rule_detector.detect(file_meta)

        def stage2():
            scores['content'] = self.content_analyzer.analyze(file_meta)

        def stage3():
            scores['metadata'] = self.metadata_scorer.analyze(file_meta)

        def stage4():
            scores['entropy'] = self.entropy_calculator.analyze(file_meta)

        # Execute stages in parallel using ThreadPoolExecutor (OpenMP simulation)
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(stage1),
                executor.submit(stage2),
                executor.submit(stage3),
                executor.submit(stage4)
            ]
            # Wait for all to complete
            for future in futures:
                future.result()

        # Fusion
        heuristic_score = (
                self.alpha * scores['content'] +
                self.beta * scores['metadata'] +
                self.gamma * scores['entropy']
        )
        final_score = max(scores['rule'], heuristic_score)

        # Classification
        if final_score < 3.0:
            level = SensitivityLevel.PUBLIC
        elif final_score < 6.0:
            level = SensitivityLevel.INTERNAL
        elif final_score < 8.5:
            level = SensitivityLevel.CONFIDENTIAL
        else:
            level = SensitivityLevel.SECRET

        # Priority
        days_old = (time.time() - file_meta.modified_time) / 86400
        recency_factor = math.exp(-0.01 * days_old)
        priority_score = 0.6 * (final_score / 10.0) + 0.4 * recency_factor

        processing_time = time.time() - start_time

        return ClassificationResult(
            filename=file_meta.filename,
            rule_score=scores['rule'],
            content_score=scores['content'],
            metadata_score=scores['metadata'],
            entropy_score=scores['entropy'],
            final_score=final_score,
            sensitivity_level=level,
            priority_score=priority_score,
            processing_time=processing_time
        )