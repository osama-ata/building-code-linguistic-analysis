"""
Integration tests for the building code parsing pipeline.
"""
import pytest
from src.preprocessing.md_parser import MarkdownParser

def test_md_parser_basics():
    parser = MarkdownParser()
    sample_md = '''
# 3.2 Exit Routes
An exit route must be maintained free from obstruction.

## 3.2.1 Dimensions
The minimum width of an exit door shall be 900 mm.
    '''
    
    parsed = parser.parse_file(sample_md)
    sections = parsed.get("sections", [])
    
    assert len(sections) == 2
    assert sections[0]["title"] == "3.2 Exit Routes"
    assert sections[1]["title"] == "3.2.1 Dimensions"
    assert "An exit route must be maintained free from obstruction." in sections[0]["clauses"][0]
    assert "The minimum width of an exit door shall be 900 mm." in sections[1]["clauses"][0]
