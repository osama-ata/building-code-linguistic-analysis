# Agent Instructions (`AGENTS.md`)

Welcome! If you are an AI agent assisting with the `building-code-linguistic-analysis` repository, please adhere to the following guidelines and context to ensure consistency across the project.

## Project Context
This project transforms raw building code regulations (Markdown format) into structured, computationally accessible formats (JSON/LegalRuleML) using an extensive Natural Language Processing pipeline. 

The pipeline consists of four main phases:
- **Phase A (Preprocessing)**: Chunking raw `.md` documents into smaller semantic chapters (via `src/preprocessing/section_splitter.py` or `.md_parser.py`).
- **Phase B (Linguistic Analysis)**: Custom NER for the construction domain, dependency parsing, coreference resolution.
- **Phase C (Classification & Deontic Logic)**: Determining prescriptive vs. informative classes and modal verbs (Obligation, Permission, Prohibition).
- **Phase D (Rule Extraction)**: Exporting the SVO mapping and conditions into JSON Lines or LegalRuleML.

## Environment & Commands
- **Operating System Note**: The user is using Windows. **Do not run `make` commands** without explicitly checking if `make` is installed on their system. Instead, run the underlying python commands directly.
- **Dependency Management**: The project uses `pyproject.toml`. Standard execution should use `-m` flags or direct path pointing.
- **Execution Script**:
  - Run pipeline tests or executions via: `python scripts/run_pipeline.py`
  - Preprocess massive docs via: `python scripts/curate_raw_markdown.py -i data/01_raw/<file>.md -o data/02_curated/<folder-name>`

## Coding Conventions
- Prioritize using the `spaCy` (>= 3.7) NLP backbone.
- Keep structural modifications isolated inside of `src/preprocessing/`; do not bleed text manipulation logic into the ML classification zones (`src/classification/`).
- Make use of configurations driven by `configs/pipeline.yaml`.
- Whenever a script is added or modified to the user-facing CLI routines, proactively **update `README.md`** with a usage example.
- **ALWAYS REMEMBER** to update files in the `scripts/` directory as you update other core modules to ensure full repository consistency.
- **ALWAYS** update `PROJECT_STATUS_CHECKLIST.md` after completing successful steps in the workflow so that progress and next steps are transparently tracked.

## Testing Strategy
- Tests are contained within `tests/`. Use `pytest` for running integrations.
- Always provide mock data fixtures within `tests/conftest.py` if writing a new component test.
