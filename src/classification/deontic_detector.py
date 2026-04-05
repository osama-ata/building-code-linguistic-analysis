"""
Detects explicit deontic operators (Must, Shall, May, etc.) in text sequences.
"""
import re
import yaml
from pathlib import Path

class DeonticDetector:
    def __init__(self, patterns_path: str):
        self.deontic_map = {}
        if Path(patterns_path).exists():
            self._load_patterns(patterns_path)
            
    def _load_patterns(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        for category, regex_list in data.get("patterns", {}).items():
            compiled_patterns = [re.compile(pattern) for pattern in regex_list]
            self.deontic_map[category] = compiled_patterns

    def extract_operator(self, text: str) -> str:
        """
        Scans text sequentially and returns the first mapped deontic category.
        Returns 'NONE' if no operator is matched.
        """
        for category, patterns in self.deontic_map.items():
            for pattern in patterns:
                if pattern.search(text):
                    return category
        return "NONE"
