import argparse
import json
import logging
from pathlib import Path
from collections import Counter
import spacy

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# TODO: Add more statistics, such as:
# - Number of chapters
# - Number of sections
# - Number of clauses
# - Number of tables
# - Number of figures
# - Number of references
# - Number of exceptions
# - Number of notes
# - Number of definitions
# - Number of requirements
# - Number of prohibitions
# - Number of permissions
# - Number of exemptions
# - Number of recommendations
# - Number of standards
# - Number of codes
# - Number of specifications
# - Number of guidelines
# - Number of requirements
# - Number of prohibitions
# - Number of permissions
# - Number of exemptions
# - Number of recommendations
# - Number of standards
# - Number of codes
# - Number of specifications
# - Number of guidelines
# - n-grams
# - POS tags
# - Dependency relations
# - Named entities
# - Coreferences
# - Semantic roles
# - Discourse relations
# - Pragmatic relations
# - Speech acts
# - Intentions
# - Beliefs
# - Desires
# - Plans
# - Goals
# - Actions
# - Events
# - States
# - Properties
# - Relations
# - Concepts
# - Categories
# - Classes
# - Types
# - Instances
# - Examples
# - Counterexamples
# - Exceptions
# - Notes
# - Definitions
# - Requirements
# - Prohibitions
# - Permissions
# - Exemptions
# - Recommendations
# - Standards
# - Codes
# - Specifications
# - Guidelines
# - Requirements
# - Prohibitions
# - Permissions
# - Exemptions
# - Recommendations
# - Standards
# - Codes
# - Specifications
# - Guidelines


def compute_statistics(input_dir: str, output_file: str):
    input_path = Path(input_dir)
    if not input_path.exists():
        logging.error(f"Input directory {input_dir} does not exist.")
        return

    # Load spacy, but disable components we don't need for basic token/sentence stats
    logging.info("Loading NLP model...")
    try:
        nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer", "textcat"])
    except OSError:
        logging.info("Downloading en_core_web_sm...")
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm", disable=["ner", "lemmatizer", "textcat"])

    # Increase max length to allow processing large markdown files like SBC-201-2007 (1.7MB)
    nlp.max_length = 5000000

    total_stats = {
        "files_processed": 0,
        "total_characters": 0,
        "total_words": 0,
        "total_sentences": 0,
        "vocab_size": 0,
        "average_sentence_length": 0.0,
        "top_words": [],
    }

    vocabulary_counter = Counter()
    meaningful_words_counter = Counter()

    # Iterate over markdown files
    for file_path in input_path.glob("**/*.md"):
        logging.info(f"Processing: {file_path.name}")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        total_stats["files_processed"] += 1
        total_stats["total_characters"] += len(text)

        # Process the text using spacy
        doc = nlp(text)

        # Count sentences
        num_sentences = len(list(doc.sents))
        total_stats["total_sentences"] += num_sentences

        # Count words and update vocabulary (excluding punctuation and whitespace)
        for token in doc:
            if (
                not token.is_punct
                and not token.is_space
                and not token.text.strip() == "|"
            ):
                total_stats["total_words"] += 1
                vocabulary_counter[token.text.lower()] += 1

                # Further filter to provide useful top keywords (no stopwords, only alpha, length > 1)
                if not token.is_stop and token.is_alpha and len(token.text) > 1:
                    meaningful_words_counter[token.text.lower()] += 1

    total_stats["vocab_size"] = len(vocabulary_counter)

    if total_stats["total_sentences"] > 0:
        total_stats["average_sentence_length"] = round(
            total_stats["total_words"] / total_stats["total_sentences"], 2
        )

    total_stats["top_words"] = meaningful_words_counter.most_common(100)

    # Save to json file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(total_stats, f, indent=4)

    logging.info(f"Statistics generated and saved to {output_path}")

    # Print summary
    print("\n--- Corpus Statistics ---")
    for key, value in total_stats.items():
        if key == "top_words":
            # Just print the words for summary readability
            print(f"Top 20 words: {[w[0] for w in value]}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate statistics for raw text corpus."
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        default="data/01_raw",
        help="Directory containing raw markdown files.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="data/04_processed/corpus_statistics.json",
        help="Path to save the output JSON configuration.",
    )
    args = parser.parse_args()

    compute_statistics(args.input, args.output)
