# Data Directory

This directory is designated for dataset storage.

## Current Setup

The project uses **synthetic datasets** generated programmatically to simulate:
- **GovDocs1 Corpus**: Government documents with diverse formats (PDF, DOC, TXT, HTML)
- **Enron Email Dataset**: Email communications with varying sensitivity levels

Synthetic data is generated using `src/utils/dataset_generator.py` with realistic characteristics:
- Multiple sensitivity levels (PUBLIC, INTERNAL, CONFIDENTIAL, SECRET)
- Realistic metadata (permissions, paths, ownership)
- Content patterns matching real-world sensitive data

## Using Real Datasets (Optional)

If you wish to test with real datasets:

### GovDocs1 Corpus
- Download from: https://digitalcorpora.org/corpora/files
- Place files in: `data/govdocs_sample/`
- Recommended: 1000-5000 files for testing

### Enron Email Dataset
- Download from: https://www.cs.cmu.edu/~enron/
- Place files in: `data/enron_sample/`
- Recommended: 500-1000 emails for testing

## Directory Structure (if using real data)
```
data/
├── govdocs_sample/
│   ├── file_001.pdf
│   ├── file_002.doc
│   └── ...
├── enron_sample/
│   ├── email_001.txt
│   ├── email_002.txt
│   └── ...
└── README.md (this file)
```

## Note

For the research paper results, synthetic data is sufficient and provides:
- Reproducible experiments
- Controlled sensitivity distributions
- Consistent file characteristics
- No privacy/legal concerns