"""
Streamlit App: Markdown Exploration (Phase A)

Explores the raw markdown structure of the Saudi Building Code and validates
the Phase A structural parsers (ChapterSplitter and MarkdownParser).
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on the path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.preprocessing.section_splitter import ChapterSplitter
from src.preprocessing.md_parser import MarkdownParser

st.set_page_config(page_title="Markdown Exploration", layout="wide")
st.title("Markdown Exploration")
st.markdown(
    "Explores the raw markdown structure of `SBC-201-2007.md` and validates "
    "the Phase A structural parsers."
)

# --- Sidebar: file picker ---
st.sidebar.header("Input")
default_path = ROOT / "data" / "01_raw" / "SBC-201-2007.md"
uploaded = st.sidebar.file_uploader("Upload a Markdown file", type=["md"])


@st.cache_data(show_spinner="Loading file…")
def load_content(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


if uploaded is not None:
    content = uploaded.read().decode("utf-8")
    source_label = uploaded.name
elif default_path.exists():
    content = load_content(str(default_path))
    source_label = str(default_path)
else:
    st.warning("No file found. Please upload a Markdown file via the sidebar.")
    st.stop()

st.sidebar.success(f"Loaded: {source_label}")
st.sidebar.metric("Characters", f"{len(content):,}")

# --- 1. Raw Snippet ---
st.header("1. Raw File Snippet")
snippet_start = st.slider(
    "Start character offset", 0, max(0, len(content) - 200), 2400, step=100
)
st.code(content[snippet_start : snippet_start + 200], language="markdown")

# --- 2. Chapter Splitting ---
st.header("2. Chapter Splitting")


@st.cache_data(show_spinner="Splitting chapters…")
def split_chapters(text: str):
    splitter = ChapterSplitter()
    return splitter.split_into_chapters(text)


chapters = split_chapters(content)
meaningful = [ch for ch in chapters if len(ch["body"].split()) > 10]

st.metric("Total chapter blocks extracted", len(chapters))
st.metric("Meaningful chapters (>10 words)", len(meaningful))

chapter_rows = [
    {
        "Chapter ID": ch["id"],
        "Title": ch["title"],
        "Body Length (chars)": len(ch["body"]),
        "Word Count": len(ch["body"].split()),
    }
    for ch in meaningful
]
st.dataframe(chapter_rows, use_container_width=True)

# --- 3. Deep Clause Parsing ---
st.header("3. Deep Clause Parsing")

chapter_ids = [ch["id"] for ch in meaningful]
if not chapter_ids:
    st.info("No meaningful chapters available for parsing.")
else:
    selected_id = st.selectbox("Select chapter to parse", chapter_ids)
    sample_chapter = next(ch for ch in chapters if ch["id"] == selected_id)

    @st.cache_data(show_spinner="Parsing sections…")
    def parse_chapter(body: str):
        parser = MarkdownParser()
        return parser.parse_file(body)

    structure = parse_chapter(sample_chapter["body"])
    sections = structure.get("sections", [])

    st.metric("Subsections found", len(sections))

    rows = [
        {
            "Level": sec["level"],
            "Title": sec["title"],
            "Clause Count": len(sec.get("clauses", [])),
        }
        for sec in sections[:50]
    ]
    st.dataframe(rows, use_container_width=True)

    if sections:
        st.subheader("Section Body Preview")
        sec_titles = [sec["title"] for sec in sections[:50]]
        chosen_title = st.selectbox("Select a section", sec_titles)
        chosen_sec = next((s for s in sections if s["title"] == chosen_title), None)
        if chosen_sec:
            for clause in chosen_sec.get("clauses", [])[:10]:
                st.markdown(f"> {clause}")
