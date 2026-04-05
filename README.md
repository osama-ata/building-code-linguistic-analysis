# building-code-linguistic-analysis

Linguistic analysis of building codes involves the application of Natural Language Processing (NLP), syntactic parsing, and semantic analysis to transform technical, natural language regulations into computer-processable formats for automated compliance checking (ACC).

## Project Overview

This repository provides an NLP pipeline specifically tailored for parsing, analyzing, and extracting structured rules from building codes available as Markdown (`.md`) files.

The pipeline comprises several distinct workflows:

- **Phase A — Preprocessing:** Structural parsing of markdown files into hierarchical trees (Chapter → Section → Clause) and resolution of cross-references.
- **Phase B — Linguistic Analysis:** Custom Name Entity Recognition (NER) for the construction domain, SVO (Subject-Verb-Object) extraction through dependency parsing, and coreference resolution.
- **Phase C — Classification & Deontic Logic:** Classification of sentences (e.g. prescriptive vs. informative) and extraction of deontic operators (Obligation, Permission, Prohibition, Exemption).
- **Phase D — Rule Extraction & Export:** Processing constraints, mapping values and conditions, and building structured models such as JSON Lines and LegalRuleML.

## Architecture & Tech Stack

- **NLP Backbone:** `spaCy` 3.x for production-ready dependency parsing and custom NER models.
- **Code Structuring:** Modern Python setup utilizing `pyproject.toml` alongside code quality checks (`ruff`, `mypy`).
- **Tooling Interface:** Automation and scaffolding provided via `Makefile`.

## Setup Instructions

### Requirements

- Python `>= 3.10`
- Familiarity with NLP concepts and environment management.

### Installation

You can initialize the environment using your preferred package manager (such as `uv` or `pip`).

Using `uv` and Makefile:

```bash
make setup

```

Or standard pip:

```bash
pip install -e .[dev,ml]
```

### Usage

#### 1. Data Curation (Phase A)

Drop your raw, extended `.md` formatted building code files into `data/01_raw/` and use the curation script to segment them into logical chapters:

```bash
python scripts/curate_raw_markdown.py -i data/01_raw/SBC-201-2007.md -o data/02_curated/sbc_201_2007
```

This script will produce structural chunks (e.g., `chapter_01_definitions.md`), depositing them into the `data/02_curated/` folders.

#### 1.5 Corpus Statistics

To generate a baseline understanding of your dataset vocabulary and sentence complexity, run the corpus statistics script:

```bash
uv run python scripts/corpus_statistics.py
```

```text
INFO: Loading NLP model...
INFO: Processing: SBC-201-2007.md
INFO: Statistics generated and saved to data\04_processed\corpus_statistics.json

--- Corpus Statistics ---
files_processed: 1
total_characters: 1698576
total_words: 152417
total_sentences: 9334
vocab_size: 8953
average_sentence_length: 16.33
Top 20 words: ['shall', 'section', 'required', 'mm', 'astm', 'fire', 'building', 'area', 'provided', 'accordance', 'exit', 'egress', 'construction', 'roof', 'system', 'buildings', 'requirements', 'group', 'accessible', 'materials', 'permitted', 'sbc', 'exterior', 'floor', 'type', 'means', 'units', 'minimum', 'table', 'areas', 'meters', 'comply', 'height', 'west', 'international', 'occupancy', 'wall', 'approved', 'drive', 'doors', 'pa', 'rooms', 'barr', 'harbor', 'conshohocken', 'access', 'walls', 'occupancies', 'glass', 'use', 'chapter', 'width', 'spaces', 'applicable', 'installed', 'space', 'open', 'horizontal', 'plastic', 'code', 'automatic', 'wood', 'storage', 'material', 'exception', 'resistance', 'specification', 'systems', 'smoke', 'percent', 'maximum', 'openings', 'protection', 'located', 'interior', 'provisions', 'following', 'exceed', 'assembly', 'structures', 'vertical', 'room', 'gypsum', 'general', 'door', 'control', 'unit', 'load', 'parking', 'class', 'facilities', 'sprinkler', 'sections', 'level', 'emergency', 'having', 'slope', 'structure', 'distance', 'public']
```

This performs a quick natural language pass over `data/01_raw/` and exports findings to `data/04_processed/corpus_statistics.json`.

#### 2. Execute Full Pipeline

Once curated, execute the main linguistic extraction pipeline:

```bash
make run-pipeline
# or
python scripts/run_pipeline.py
```

## Repository Highlights

Key directories:

- `configs/` - Centralized ML and pipeline config files.
- `data/` - Holds raw `.md`, curated texts, gold-standard human annotations, and final `.jsonl`/`.xml` output rules.
- `domain/` - Lexicons, regex deontic patterns, and domain constraints isolated from source code.
- `src/` - The core application codebase structured into `preprocessing`, `nlp_pipeline`, `classification`, `rule_extraction`, and `export`.
- `docs/decisions/` - Architecture Decision Records (ADRs) tracking implementation choices.
