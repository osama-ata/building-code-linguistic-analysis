"""
CLI script to bulk curate raw building code markdown into chapter-by-chapter splits.
"""
import argparse
from pathlib import Path

# Fix python path to allow imports from src
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.preprocessing.section_splitter import ChapterSplitter

def sanitize_filename(name: str) -> str:
    """Sanitize string for filename use."""
    return "".join([c if c.isalnum() else "_" for c in name]).strip("_").lower()

def main():
    parser = argparse.ArgumentParser(description="Segment a raw markdown code into chapters.")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to raw markdown file")
    parser.add_argument("--output", "-o", type=str, required=True, help="Path to output directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Could not find '{input_path}'")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    splitter = ChapterSplitter()
    chapters = splitter.split_into_chapters(content)
    
    # We may hit duplicates if there's a TOC. The later occurrence in a doc is usually longer.
    # So we'll track by ID and if an ID exists, we only overwrite if the new body is longer.
    best_chapters = {}
    for ch in chapters:
        cid = ch["id"]
        # Filter extremely short blocks (e.g. index entries)
        if len(ch["body"].split()) < 10:
            continue
            
        if cid not in best_chapters:
            best_chapters[cid] = ch
        else:
            if len(ch["body"]) > len(best_chapters[cid]["body"]):
                best_chapters[cid] = ch

    for cid, ch in best_chapters.items():
        doc_title = sanitize_filename(ch["title"])
        filename = f"chapter_{cid}_{doc_title}.md"
        out_filepath = output_dir / filename
        
        with open(out_filepath, 'w', encoding='utf-8') as f:
            f.write(ch["body"])
            
        print(f"Written {filename} (length: {len(ch['body'])} chars)")
        
    print(f"\nSuccessfully extracted {len(best_chapters)} meaningful chapters.")

if __name__ == "__main__":
    main()
