"""
Real File Loader
Loads actual files from GovDocs1 and Enron Email datasets
Replaces the synthetic dataset generator with real file reading
"""

import os
import sys
import time
import email
from pathlib import Path
from typing import List, Optional
import mimetypes

# PDF support
try:
    import PyPDF2

    HAS_PDF = True
except ImportError:
    print("WARNING: PyPDF2 not installed. PDF files will be skipped.")
    print("Install: pip install PyPDF2")
    HAS_PDF = False

# DOCX support
try:
    import docx

    HAS_DOCX = True
except ImportError:
    print("WARNING: python-docx not installed. DOCX files will be skipped.")
    print("Install: pip install python-docx")
    HAS_DOCX = False

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.utils.data_structures import FileMetadata


class RealFileLoader:
    """
    Loads real files from filesystem

    Supports:
    - GovDocs1 Corpus: PDF, DOC, DOCX, XLS, TXT, HTML
    - Enron Email Dataset: .eml email files
    - General text files
    """

    def __init__(self):
        self.supported_extensions = {
            '.txt', '.text',  # Plain text
            '.pdf',  # PDF documents
            '.doc', '.docx',  # Word documents
            '.eml', '.msg',  # Email files
            '.html', '.htm',  # HTML files
            '.csv', '.tsv',  # Spreadsheets (as text)
            '.log',  # Log files
            '.md', '.markdown',  # Markdown
        }

        self.files_loaded = 0
        self.files_skipped = 0
        self.errors = []

    def load_from_directory(self,
                            directory: str,
                            max_files: Optional[int] = None,
                            recursive: bool = True) -> List[FileMetadata]:
        """
        Load all supported files from a directory

        Args:
            directory: Path to directory containing files
            max_files: Maximum number of files to load (None = all)
            recursive: Search subdirectories recursively

        Returns:
            List of FileMetadata objects
        """
        print(f"\n{'=' * 70}")
        print(f"LOADING REAL FILES FROM: {directory}")
        print(f"{'=' * 70}")

        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = []
        directory_path = Path(directory)

        # Find all files
        if recursive:
            file_paths = list(directory_path.rglob('*'))
        else:
            file_paths = list(directory_path.glob('*'))

        # Filter for files only
        file_paths = [p for p in file_paths if p.is_file()]

        print(f"Found {len(file_paths)} total files")
        print(f"Filtering for supported types: {self.supported_extensions}")

        # Process files
        for i, filepath in enumerate(file_paths):
            if max_files and len(files) >= max_files:
                print(f"\nReached max_files limit: {max_files}")
                break

            # Check if supported
            if filepath.suffix.lower() not in self.supported_extensions:
                self.files_skipped += 1
                continue

            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Processing file {i + 1}/{len(file_paths)}...", end='\r')

            # Load file
            try:
                file_meta = self._load_single_file(filepath)
                if file_meta:
                    files.append(file_meta)
                    self.files_loaded += 1
            except Exception as e:
                self.errors.append((str(filepath), str(e)))
                self.files_skipped += 1

        # Summary
        print(f"\n{'=' * 70}")
        print(f"LOADING COMPLETE")
        print(f"{'=' * 70}")
        print(f"✓ Successfully loaded: {self.files_loaded} files")
        print(f"✗ Skipped/Errors:      {self.files_skipped} files")
        if self.errors:
            print(f"\nFirst 5 errors:")
            for filepath, error in self.errors[:5]:
                print(f"  {filepath}: {error}")
        print(f"{'=' * 70}\n")

        return files

    def _load_single_file(self, filepath: Path) -> Optional[FileMetadata]:
        """
        Load a single file and extract metadata

        Args:
            filepath: Path to file

        Returns:
            FileMetadata object or None if failed
        """
        try:
            # Get file stats from OS
            stat = os.stat(filepath)

            # Extract content based on file type
            content = self._extract_content(filepath)

            # Skip empty files
            if not content or len(content.strip()) == 0:
                return None

            # Get owner (Unix/Linux only)
            try:
                import pwd
                owner = pwd.getpwuid(stat.st_uid).pw_name
            except:
                owner = "unknown"

            return FileMetadata(
                filename=filepath.name,
                size=stat.st_size,
                content=content,
                permissions=stat.st_mode & 0o777,  # Extract permission bits
                path=str(filepath),
                modified_time=stat.st_mtime,
                owner=owner
            )

        except Exception as e:
            raise Exception(f"Failed to load file: {e}")

    def _extract_content(self, filepath: Path) -> str:
        """
        Extract text content from file based on type

        Args:
            filepath: Path to file

        Returns:
            Extracted text content
        """
        extension = filepath.suffix.lower()

        # Plain text files
        if extension in {'.txt', '.text', '.log', '.md', '.markdown',
                         '.csv', '.tsv', '.html', '.htm'}:
            return self._read_text_file(filepath)

        # PDF files
        elif extension == '.pdf':
            if not HAS_PDF:
                return ""
            return self._read_pdf_file(filepath)

        # Word documents
        elif extension in {'.docx', '.doc'}:
            if extension == '.docx' and HAS_DOCX:
                return self._read_docx_file(filepath)
            else:
                return ""  # .doc (old format) not supported

        # Email files
        elif extension in {'.eml', '.msg'}:
            return self._read_email_file(filepath)

        else:
            return ""

    def _read_text_file(self, filepath: Path) -> str:
        """Read plain text file"""
        try:
            # Try UTF-8 first
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1
            try:
                with open(filepath, 'r', encoding='latin-1') as f:
                    return f.read()
            except:
                # Last resort: binary read and decode with errors='ignore'
                with open(filepath, 'rb') as f:
                    return f.read().decode('utf-8', errors='ignore')

    def _read_pdf_file(self, filepath: Path) -> str:
        """Extract text from PDF"""
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""

                # Extract from all pages
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

                return text
        except Exception as e:
            # PDF might be corrupted or encrypted
            return ""

    def _read_docx_file(self, filepath: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(filepath)
            paragraphs = [para.text for para in doc.paragraphs]
            return "\n".join(paragraphs)
        except Exception as e:
            return ""

    def _read_email_file(self, filepath: Path) -> str:
        """Extract text from email file (.eml)"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                msg = email.message_from_file(f)

                # Extract headers
                subject = msg.get('Subject', '')
                from_addr = msg.get('From', '')
                to_addr = msg.get('To', '')
                date = msg.get('Date', '')

                # Extract body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='ignore')
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')

                # Combine
                email_text = f"""
Subject: {subject}
From: {from_addr}
To: {to_addr}
Date: {date}

{body}
"""
                return email_text

        except Exception as e:
            return ""


def load_govdocs1_sample(govdocs_dir: str, max_files: int = 1000) -> List[FileMetadata]:
    """
    Load sample from GovDocs1 Corpus

    Args:
        govdocs_dir: Path to GovDocs1 directory
        max_files: Maximum files to load

    Returns:
        List of FileMetadata
    """
    print("\n📂 Loading GovDocs1 Corpus...")
    loader = RealFileLoader()
    return loader.load_from_directory(govdocs_dir, max_files=max_files)


def load_enron_emails(enron_dir: str, max_files: int = 1000) -> List[FileMetadata]:
    """
    Load sample from Enron Email Dataset

    Args:
        enron_dir: Path to Enron email directory
        max_files: Maximum files to load

    Returns:
        List of FileMetadata
    """
    print("\n📧 Loading Enron Email Dataset...")
    loader = RealFileLoader()
    return loader.load_from_directory(enron_dir, max_files=max_files)


def load_mixed_dataset(govdocs_dir: str,
                       enron_dir: str,
                       total_files: int = 1000) -> List[FileMetadata]:
    """
    Load mixed dataset from both GovDocs1 and Enron

    Args:
        govdocs_dir: Path to GovDocs1
        enron_dir: Path to Enron emails
        total_files: Total files to load (split 50/50)

    Returns:
        Combined list of FileMetadata
    """
    print(f"\n📊 Loading mixed dataset ({total_files} total files)...")

    # Load 50% from each
    half = total_files // 2

    govdocs_files = load_govdocs1_sample(govdocs_dir, max_files=half)
    enron_files = load_enron_emails(enron_dir, max_files=half)

    combined = govdocs_files + enron_files

    print(f"\n✓ Loaded {len(combined)} total files:")
    print(f"  - GovDocs1: {len(govdocs_files)} files")
    print(f"  - Enron:    {len(enron_files)} files")

    return combined


# Example usage
if __name__ == "__main__":
    # Test the loader
    import argparse

    parser = argparse.ArgumentParser(description='Load real files for classification')
    parser.add_argument('--govdocs', type=str, help='Path to GovDocs1 directory')
    parser.add_argument('--enron', type=str, help='Path to Enron email directory')
    parser.add_argument('--dir', type=str, help='Path to any directory')
    parser.add_argument('--max-files', type=int, default=100, help='Maximum files to load')

    args = parser.parse_args()

    if args.govdocs:
        files = load_govdocs1_sample(args.govdocs, max_files=args.max_files)
    elif args.enron:
        files = load_enron_emails(args.enron, max_files=args.max_files)
    elif args.dir:
        loader = RealFileLoader()
        files = loader.load_from_directory(args.dir, max_files=args.max_files)
    else:
        print("Please specify --govdocs, --enron, or --dir")
        sys.exit(1)

    # Show sample
    if files:
        print(f"\n{'=' * 70}")
        print("SAMPLE FILE:")
        print(f"{'=' * 70}")
        sample = files[0]
        print(f"Filename:    {sample.filename}")
        print(f"Size:        {sample.size} bytes")
        print(f"Path:        {sample.path}")
        print(f"Permissions: {oct(sample.permissions)}")
        print(f"Owner:       {sample.owner}")
        print(f"Modified:    {time.ctime(sample.modified_time)}")
        print(f"Content preview:\n{sample.content[:500]}...")
        print(f"{'=' * 70}")