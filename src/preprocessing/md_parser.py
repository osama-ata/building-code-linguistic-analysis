"""
Parser module for extracting structural elements from Markdown files.
"""

import re
from typing import List, Dict, Any, Optional

class MarkdownParser:
    def __init__(self):
        # Basic header regex: match 1 to 6 hash marks
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.*)')
        
    def parse_file(self, content: str) -> Dict[str, Any]:
        """
        Parses Markdown content into a structural tree.
        
        Args:
            content: Raw Markdown string.
            
        Returns:
            A dictionary representing the document structure consisting of headers and clauses.
        """
        lines = content.splitlines()
        structure = {"title": "", "sections": []}
        
        current_section = None
        current_clauses = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            header_match = self.header_pattern.match(line)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # Setup a new section
                current_section = {"level": level, "title": title, "clauses": []}
                structure["sections"].append(current_section)
                current_clauses = current_section["clauses"]
            else:
                if current_section is None:
                    # File without a header; add a default one or just capture content
                    current_section = {"level": 0, "title": "root", "clauses": []}
                    structure["sections"].append(current_section)
                    current_clauses = current_section["clauses"]
                    
                current_clauses.append(line)
                
        return structure
