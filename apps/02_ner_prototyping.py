"""
Streamlit App: NER Prototyping (Phase B)

Demonstrates tokenization, custom Named Entity Recognition, and
Subject-Verb-Object (SVO) dependency parsing on regulatory text.
"""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

st.set_page_config(page_title="NER Prototyping", layout="wide")
st.title("Linguistic Prototyping (Phase B)")
st.markdown(
    "Tokenize regulatory text, extract custom construction-domain entities, "
    "and visualise Subject-Verb-Object dependency triplets."
)


# --- Load models (cached) ---
@st.cache_resource(show_spinner="Loading NLP models…")
def load_models():
    from src.nlp_pipeline.tokenizer import Tokenizer
    from src.nlp_pipeline.ner import ConstructionNER
    from src.nlp_pipeline.dependency_parser import DependencyParser

    pattern_path = ROOT / "domain" / "entity_types.yaml"
    tokenizer = Tokenizer()
    ner_model = ConstructionNER(patterns_path=str(pattern_path))
    svo_model = DependencyParser()
    return tokenizer, ner_model, svo_model


try:
    tokenizer, ner_model, svo_model = load_models()
    models_ok = True
except Exception as exc:
    st.error(
        f"Could not load NLP models: {exc}\n\n"
        "Run `pip install -e .` from the project root and ensure "
        "`en_core_web_sm` is installed (`python -m spacy download en_core_web_sm`)."
    )
    models_ok = False

# --- Input ---
st.sidebar.header("Input text")
default_text = (
    "The minimum width of an exit door shall be 900 mm. "
    "Such doors provide a safe exit route."
)
sample_text = st.sidebar.text_area(
    "Enter regulatory text", value=default_text, height=150
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Tip**: Try sentences with deontic verbs like *shall*, *must*, *may not*."
)

if not models_ok or not sample_text.strip():
    st.stop()

# --- 1. Tokenisation & Sentence Splitting ---
st.header("1. Tokenisation & Sentence Splitting")

sentences = tokenizer.get_sentences(sample_text)
st.metric("Sentences detected", len(sentences))
for i, sent in enumerate(sentences, 1):
    st.markdown(f"**{i}.** {sent}")

# --- 2. Named Entity Recognition ---
st.header("2. Named Entity Recognition")

entities = ner_model.extract_entities(sample_text)
domain_labels = {"BUILDING_ELEMENT", "MEASUREMENT", "SPATIAL"}

domain_ents = [e for e in entities if e.get("label") in domain_labels]
all_ents = entities

col1, col2 = st.columns(2)
col1.metric("Total entities detected", len(all_ents))
col2.metric("Domain-specific entities", len(domain_ents))

if all_ents:
    st.subheader("All Detected Entities")
    st.dataframe(all_ents, use_container_width=True)

if domain_ents:
    st.subheader("Domain Entities Only")
    st.dataframe(domain_ents, use_container_width=True)
else:
    st.info("No domain-specific entities found in the provided text.")

# --- 3. Dependency Parsing (SVO) ---
st.header("3. Dependency Parsing (SVO)")

try:
    svo_triplets = svo_model.extract_svo(sample_text)
    st.metric("SVO triplets extracted", len(svo_triplets))

    if svo_triplets:
        for i, trip in enumerate(svo_triplets, 1):
            with st.expander(f"Triplet {i}"):
                col_s, col_v, col_o = st.columns(3)
                col_s.metric("Subject", trip.get("subject", "—"))
                col_v.metric("Verb", trip.get("verb", "—"))
                col_o.metric("Object", trip.get("object", "—"))
    else:
        st.info(
            "No SVO triplets found. Try a sentence with a clear subject and object."
        )
except Exception as exc:
    st.warning(f"SVO extraction failed: {exc}")
