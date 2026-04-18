"""
Data Structures
Core data types used throughout the system
"""

from dataclasses import dataclass
from enum import Enum


class SensitivityLevel(Enum):
    """
    File sensitivity classification levels
    Based on Solution Architecture threshold mapping
    """
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    SECRET = 3


@dataclass
class FileMetadata:
    """
    Represents file metadata for classification

    Attributes:
        filename: Name of the file
        size: File size in bytes
        content: File text content
        permissions: Unix-style permissions (e.g., 0o644)
        path: Full file path
        modified_time: Last modification timestamp (Unix epoch)
        owner: File owner username
    """
    filename: str
    size: int
    content: str
    permissions: int
    path: str
    modified_time: float
    owner: str


@dataclass
class ClassificationResult:
    """
    Result from classification pipeline

    Attributes:
        filename: Name of classified file
        rule_score: Stage 1 score (0-10)
        content_score: Stage 2 score (0-10)
        metadata_score: Stage 3 score (0-10)
        entropy_score: Stage 4 score (0-10)
        final_score: Combined score (0-10)
        sensitivity_level: Classification level
        priority_score: Disaster recovery priority (0-1)
        processing_time: Time taken to classify (seconds)
    """
    filename: str
    rule_score: float
    content_score: float
    metadata_score: float
    entropy_score: float
    final_score: float
    sensitivity_level: SensitivityLevel
    priority_score: float
    processing_time: float