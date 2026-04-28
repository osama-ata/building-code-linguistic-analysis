"""Quick diagnostic script to assess workflow output quality."""

import json
from pathlib import Path
from collections import Counter

rules = [
    json.loads(l)
    for l in Path("data/04_processed/rules.jsonl").read_text().splitlines()
    if l.strip()
]

print(f"Total rules: {len(rules)}")
print()

# --- Missing agent samples ---
missing_agent = [r for r in rules if "MISSING_AGENT" in r["flags"]]
print(f"=== MISSING_AGENT samples ({len(missing_agent)}) — first 5 ===")
for r in missing_agent[:5]:
    print("  sentence:", r["sentence"][:120])
    print("  action:  ", r["action"])
    print()

# --- Rules with agent successfully extracted ---
has_agent = [r for r in rules if r["agent"]]
print(f"=== Rules WITH agent ({len(has_agent)}/{len(rules)}) ===")
for r in has_agent[:8]:
    print(f"  agent={r['agent'][:50]}")
    print(f"  action={r['action'][:50]}")
    print(f"  sent: {r['sentence'][:100]}")
    print()

# --- PROHIBITION: why none? ---
print("=== DEONTIC distribution ===")
deontic = Counter(r["deontic_operator"] for r in rules)
for k, v in deontic.most_common():
    print(f"  {k}: {v}")
print()

# --- Sentences still containing artefacts post-normaliser ---
artefact_samples = [r for r in rules if r["sentence"].startswith(("- ", "* ", "#"))]
print(f"=== Sentences with residual artefacts: {len(artefact_samples)} ===")
for r in artefact_samples[:3]:
    print("  ", r["sentence"][:100])

# --- Numeric extraction quality ---
with_num = [r for r in rules if r["numeric_values"]]
print(f"\n=== Rules with numeric values: {len(with_num)} ===")
for r in with_num:
    print(f"  {r['numeric_values']} => {r['sentence'][:80]}")

# --- Cross refs ---
with_ref = [r for r in rules if r["cross_refs"]]
print(f"\n=== Rules with cross-refs: {len(with_ref)} ===")
for r in with_ref:
    print(f"  {r['cross_refs']} => {r['sentence'][:80]}")
