"""
Dataset Generator
Generates synthetic files mimicking GovDocs1 and Enron characteristics
"""

import random
import time
from typing import List

from .data_structures import FileMetadata


def generate_synthetic_dataset(num_files: int, seed: int = 42) -> List[FileMetadata]:
    """
    Generate synthetic files with realistic sensitivity distributions

    Mimics characteristics of:
    - GovDocs1 Corpus: Government documents (PDF, DOC, TXT)
    - Enron Email Dataset: Email communications

    Args:
        num_files: Number of files to generate
        seed: Random seed for reproducibility

    Returns:
        List of FileMetadata objects
    """
    random.seed(seed)

    files = []

    # Content templates for different sensitivity levels
    templates = {
        'public': [
            "This is a public announcement about company events and general information.",
            "Meeting notes for team sync on project updates and quarterly planning.",
            "General information document for all employees regarding office policies.",
            "Public press release about new product launch and market expansion.",
        ],
        'internal': [
            "Internal memo regarding department restructuring and workflow changes.",
            "Budget planning document for Q3 financial review and resource allocation.",
            "Employee handbook confidential section about compensation policies.",
            "Internal communication about strategic planning and operational goals.",
        ],
        'confidential': [
            "Confidential financial report for executive review containing revenue data.",
            "Legal agreement with private terms and conditions for merger discussion.",
            "Employee records containing SSN: 123-45-6789 and salary information.",
            "Proprietary research data classified as confidential intellectual property.",
        ],
        'secret': [
            "SECRET: Classified information regarding merger acquisition strategy.",
            "Encrypted password database: admin@company.com with access credentials.",
            "Proprietary algorithm source code - restricted access only for developers.",
            "Executive compensation package with confidential financial details.",
        ]
    }

    # Directory paths correlated with sensitivity
    paths = {
        'public': ['/documents/public/', '/shared/', '/general/', '/announcements/'],
        'internal': ['/documents/internal/', '/departments/', '/planning/'],
        'confidential': ['/documents/confidential/', '/hr/', '/legal/', '/finance/'],
        'secret': ['/documents/secret/', '/executive/', '/classified/', '/proprietary/']
    }

    # Owners correlated with sensitivity
    owners = {
        'public': ['user', 'employee', 'staff'],
        'internal': ['manager', 'employee', 'user'],
        'confidential': ['admin', 'hr_manager', 'legal'],
        'secret': ['executive', 'ceo', 'root', 'admin']
    }

    # Permissions correlated with sensitivity
    permissions = {
        'public': [0o644, 0o664, 0o755],
        'internal': [0o640, 0o644],
        'confidential': [0o600, 0o640],
        'secret': [0o600, 0o400]
    }

    for i in range(num_files):
        # Random sensitivity level (realistic distribution)
        # 40% public, 30% internal, 20% confidential, 10% secret
        rand = random.random()
        if rand < 0.4:
            level_choice = 'public'
        elif rand < 0.7:
            level_choice = 'internal'
        elif rand < 0.9:
            level_choice = 'confidential'
        else:
            level_choice = 'secret'

        # Generate content
        base_content = random.choice(templates[level_choice])

        # Add document ID and filler text
        content = f"{base_content} Document ID: {i:06d}. "
        content += "Lorem ipsum dolor sit amet consectetur adipiscing elit. " * random.randint(5, 20)

        # For confidential/secret, add more sensitive patterns
        if level_choice in ['confidential', 'secret']:
            if random.random() < 0.3:
                content += f" Contact: john.doe@company.com Phone: 555-123-{random.randint(1000, 9999)}"
            if level_choice == 'secret' and random.random() < 0.2:
                content += " Password: SecretP@ss123! Access restricted."

        # Generate metadata
        filename = f"file_{i:06d}.txt"
        size = len(content.encode('utf-8'))

        # Select correlated metadata
        permission = random.choice(permissions[level_choice])
        path = random.choice(paths[level_choice]) + filename
        owner = random.choice(owners[level_choice])

        # Modification time (last 365 days, recent files slightly more likely)
        days_ago = random.expovariate(1 / 180)  # Average 180 days old
        days_ago = min(days_ago, 365)  # Cap at 1 year
        modified_time = time.time() - (days_ago * 86400)

        files.append(FileMetadata(
            filename=filename,
            size=size,
            content=content,
            permissions=permission,
            path=path,
            modified_time=modified_time,
            owner=owner
        ))

    return files


def generate_test_file(sensitivity: str = 'confidential') -> FileMetadata:
    """
    Generate a single test file of specified sensitivity

    Args:
        sensitivity: One of 'public', 'internal', 'confidential', 'secret'

    Returns:
        Single FileMetadata object
    """
    templates = {
        'public': "Public document with general information.",
        'internal': "Internal memo for department use only.",
        'confidential': "Confidential data: SSN 123-45-6789, Card 4532-1234-5678-9010",
        'secret': "SECRET classified document with password: Admin123! Restricted access."
    }

    content = templates.get(sensitivity, templates['internal'])

    return FileMetadata(
        filename=f"test_{sensitivity}.txt",
        size=len(content),
        content=content,
        permissions=0o600 if sensitivity in ['confidential', 'secret'] else 0o644,
        path=f"/test/{sensitivity}/test_{sensitivity}.txt",
        modified_time=time.time(),
        owner='admin' if sensitivity == 'secret' else 'user'
    )