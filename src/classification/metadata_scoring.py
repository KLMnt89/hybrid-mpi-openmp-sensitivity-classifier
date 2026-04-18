"""
Stage 3: Metadata Scoring
Analyzes file system metadata: permissions, paths, ownership
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.data_structures import FileMetadata


class MetadataScorer:
    """
    Stage 3: File metadata analysis
    """

    SENSITIVE_PATHS = [
        '/confidential/', '/secret/', '/private/', '/internal/',
        '/financial/', '/legal/', '/hr/', '/executive/'
    ]

    def analyze(self, file_meta) -> float:
        """
        Returns context score (0-10) based on metadata

        Args:
            file_meta: FileMetadata object

        Returns:
            float: Metadata sensitivity score (0-10)
        """
        score = 0.0

        # Path analysis (up to 5 points)
        path_lower = file_meta.path.lower()
        for sensitive_path in self.SENSITIVE_PATHS:
            if sensitive_path in path_lower:
                score += 5.0
                break

        # Permission analysis (up to 3 points)
        # Restrictive permissions (< 0o644) indicate sensitivity
        if file_meta.permissions < 0o644:
            score += 3.0

        # Ownership (up to 2 points)
        # Files owned by 'admin', 'root', 'executive' are sensitive
        if file_meta.owner in ['admin', 'root', 'executive', 'ceo']:
            score += 2.0

        return min(score, 10.0)