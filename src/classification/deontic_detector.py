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

    # Check negating/restrictive operators before permissive ones so that
    # "shall not" is never shadowed by the bare "shall" OBLIGATION pattern.
    _PRIORITY_ORDER = ["PROHIBITION", "EXEMPTION", "OBLIGATION", "PERMISSION"]

    def extract_operator(self, text: str) -> str:
        """
        Scans text in priority order (negating operators first) and returns the
        first matched deontic category.  Returns 'NONE' if nothing matched.
        """
        ordered_keys = sorted(
            self.deontic_map.keys(),
            key=lambda k: self._PRIORITY_ORDER.index(k)
            if k in self._PRIORITY_ORDER
            else len(self._PRIORITY_ORDER),
        )
        for category in ordered_keys:
            for pattern in self.deontic_map[category]:
                if pattern.search(text):
                    return category
        return "NONE"
