"""
Utility module for splitting massive raw code markdown documents into semantic chapters.
"""
import re
from typing import List, Dict

class ChapterSplitter:
    def __init__(self):
        # Match lines like "## CHAPTER 1 DEFINITIONS" or "## CHAPTER 10: GYPSUM BOARD"
        self.chapter_header_pattern = re.compile(r'^##\s+CHAPTER\s+(\d+)\s*(:?)\s*(.*)', re.IGNORECASE)

    def split_into_chapters(self, content: str) -> List[Dict[str, str]]:
        """
        Splits a single markdown string containing an entire building code into a list of chapters.

        Args:
            content: Raw Markdown string.

        Returns:
            List of dicts: [{"id": "01", "title": "DEFINITIONS", "body": "..."}, ...]
        """
        lines = content.splitlines()
        chapters = []
        
        current_chapter_id = None
        current_title = None
        current_lines = []
        
        for line in lines:
            header_match = self.chapter_header_pattern.match(line)
            
            if header_match:
                # If we were capturing a chapter, finalize it
                if current_chapter_id is not None:
                    chapters.append({
                        "id": current_chapter_id,
                        "title": current_title,
                        "body": "\n".join(current_lines).strip()
                    })
                
                # Start new chapter
                num_str = header_match.group(1).zfill(2)
                title_str = header_match.group(3).strip()
                
                current_chapter_id = num_str
                current_title = title_str
                current_lines = [line]  # include header in the body
            else:
                if current_chapter_id is not None:
                    current_lines.append(line)
        
        # Don't forget the final chapter
        if current_chapter_id is not None:
            chapters.append({
                "id": current_chapter_id,
                "title": current_title,
                "body": "\n".join(current_lines).strip()
            })
            
        return chapters
