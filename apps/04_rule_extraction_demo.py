"""
Streamlit App: Rule Extraction Demo (Phase D)

Demonstrates the full Phase D pipeline: parsing conditions from regulatory
sentences and exporting structured rules as JSON Lines.
"""

import sys
import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="Rule Extraction Demo", layout="wide")
st.title("Rule Extraction Demo (Phase D)")
st.markdown(
    "Run the complete extraction pipeline on regulatory text to produce "
    "structured JSON rule objects (SVO + conditions + deontic operator)."
)


# --- Load pipeline components ---
@st.cache_resource(show_spinner="Loading pipeline components…")
def load_pipeline():
    from src.nlp_pipeline.tokenizer import Tokenizer
    from src.nlp_pipeline.ner import ConstructionNER
    from src.nlp_pipeline.dependency_parser import DependencyParser
    from src.classification.deontic_detector import DeonticDetector
    from src.classification.provision_type import ProvisionClassifier

    pattern_path = ROOT / "domain" / "entity_types.yaml"
    deontic_path = ROOT / "domain" / "deontic_patterns.yaml"

    return {
        "tokenizer": Tokenizer(),
        "ner": ConstructionNER(patterns_path=str(pattern_path)),
        "svo": DependencyParser(),
        "deontic": DeonticDetector(patterns_path=str(deontic_path)),
        "provision": ProvisionClassifier(),
    }


try:
    pipe = load_pipeline()
    pipeline_ok = True
except Exception as exc:
    st.error(
        f"Could not load pipeline components: {exc}\n\n"
        "Ensure `pip install -e .` has been run and `en_core_web_sm` is installed."
    )
    pipeline_ok = False

# --- Input ---
st.sidebar.header("Input")
input_mode = st.sidebar.radio("Mode", ["Text input", "Load from processed data"])

default_text = (
    "Exit doors shall be at least 900 mm wide.\n"
    "Handrails shall be provided on both sides of a stairway.\n"
    "The roof may be constructed of lightweight materials where the area does not exceed 500 m2.\n"
    "Stairways shall not have open risers in high-rise buildings."
)

if input_mode == "Text input":
    raw_text = st.text_area(
        "Regulatory text (one sentence per line)", value=default_text, height=180
    )
    sentences_input = [s.strip() for s in raw_text.splitlines() if s.strip()]
else:
    rules_path = ROOT / "data" / "04_processed" / "rules.jsonl"
    if rules_path.exists() and rules_path.stat().st_size > 0:
        with open(rules_path, encoding="utf-8") as f:
            existing_rules = [json.loads(line) for line in f if line.strip()]
        st.info(
            f"Loaded {len(existing_rules)} existing rules from `data/04_processed/rules.jsonl`."
        )
        st.json(existing_rules[:10])
        st.stop()
    else:
        st.warning(
            "`data/04_processed/rules.jsonl` is empty or missing. Switching to text input."
        )
        raw_text = st.text_area(
            "Regulatory text (one sentence per line)", value=default_text, height=180
        )
        sentences_input = [s.strip() for s in raw_text.splitlines() if s.strip()]

if not pipeline_ok or not sentences_input:
    st.stop()


# --- Extract rules ---
def extract_rule(sentence: str) -> dict:
    sentences = pipe["tokenizer"].get_sentences(sentence)
    entities = pipe["ner"].extract_entities(sentence)
    svo_triplets = pipe["svo"].extract_svo(sentence)
    deontic_op = pipe["deontic"].extract_operator(sentence)
    prov_type = pipe["provision"].classify(sentence, entities)

    return {
        "text": sentence,
        "sentences": sentences,
        "deontic_operator": deontic_op or "NONE",
        "provision_type": prov_type,
        "entities": entities,
        "svo": svo_triplets,
    }


if st.button("Extract Rules", type="primary"):
    rules = []
    progress = st.progress(0, text="Extracting…")
    for i, sent in enumerate(sentences_input):
        try:
            rules.append(extract_rule(sent))
        except Exception as exc:
            rules.append({"text": sent, "error": str(exc)})
        progress.progress(
            (i + 1) / len(sentences_input),
            text=f"Processed {i + 1}/{len(sentences_input)}",
        )
    progress.empty()

    st.header("Extracted Rules")
    st.metric("Rules extracted", len(rules))

    for i, rule in enumerate(rules, 1):
        with st.expander(
            f"Rule {i}: {rule['text'][:80]}…"
            if len(rule["text"]) > 80
            else f"Rule {i}: {rule['text']}"
        ):
            if "error" in rule:
                st.error(f"Extraction error: {rule['error']}")
            else:
                c1, c2 = st.columns(2)
                c1.metric("Deontic Operator", rule["deontic_operator"])
                c2.metric("Provision Type", rule["provision_type"])

                if rule["svo"]:
                    st.subheader("SVO Triplets")
                    st.dataframe(rule["svo"], use_container_width=True)

                if rule["entities"]:
                    st.subheader("Entities")
                    st.dataframe(rule["entities"], use_container_width=True)

    # --- Export ---
    st.header("Export")
    jsonl_output = "\n".join(json.dumps(r, ensure_ascii=False) for r in rules)
    st.download_button(
        label="Download as JSON Lines (.jsonl)",
        data=jsonl_output,
        file_name="extracted_rules.jsonl",
        mime="application/x-ndjson",
    )

    st.subheader("Raw JSON Preview")
    st.json(rules)
