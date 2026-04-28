"""
to_legalruleml.py — Serialises Constraint objects to LegalRuleML 1.0 XML.

LegalRuleML is an OASIS standard for encoding legal/normative rules in XML.
Reference: https://docs.oasis-open.org/legalruleml/legalruleml-core-spec/

Structure produced::

  <lrml:LegalRuleML>
    <lrml:Statements key="SBC201">
      <lrml:Statement key="SBC201.0903.0001">
        <lrml:Obligation>
          <lrml:Proposition>
            <atom>
              <op><rel>shall be provided</rel></op>
              <arg><ind>sprinkler system</ind></arg>
            </atom>
          </lrml:Proposition>
          <lrml:Bearer><lrml:Agent>...</lrml:Agent></lrml:Bearer>
        </lrml:Obligation>
      </lrml:Statement>
    </lrml:Statements>
  </lrml:LegalRuleML>

Usage::

    from src.export.to_legalruleml import LegalRuleMLExporter
    LegalRuleMLExporter().export(constraints, Path("data/05_rules/sbc201.xml"))
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Namespace map
_NS = {
    "lrml": "http://docs.oasis-open.org/legalruleml/ns/v1.0/legalruleml#",
    "ruleml": "http://ruleml.org/spec/RuleML/0.91/xsd/dr.xsd#",
}
# deontic_operator → LegalRuleML element name
_DEONTIC_TAG: dict[str, str] = {
    "OBLIGATION": "lrml:Obligation",
    "PERMISSION": "lrml:Permission",
    "PROHIBITION": "lrml:Prohibition",
    "EXEMPTION": "lrml:Exemption",
}


class LegalRuleMLExporter:
    """Converts a list of Constraint objects to LegalRuleML XML."""

    def export(
        self,
        constraints: list[Any],  # list[Constraint]
        output_path: Path,
        document_key: str = "SBC201",
    ) -> None:
        ET.register_namespace("lrml", _NS["lrml"])
        ET.register_namespace("ruleml", _NS["ruleml"])

        root = ET.Element(f"{{{_NS['lrml']}}}LegalRuleML")
        statements = ET.SubElement(root, f"{{{_NS['lrml']}}}Statements")
        statements.set("key", document_key)

        for c in constraints:
            stmt = ET.SubElement(statements, f"{{{_NS['lrml']}}}Statement")
            stmt.set("key", c.clause_id)

            comment = ET.Comment(f" {c.sentence} ")
            stmt.append(comment)

            # Deontic wrapper
            deontic_tag = _DEONTIC_TAG.get(c.deontic_operator, "lrml:Obligation")
            ns, local = deontic_tag.split(":")
            deontic_el = ET.SubElement(stmt, f"{{{_NS[ns]}}}{local}")

            # Condition (if/where clause)
            if c.condition and c.condition.get("trigger"):
                cond_el = ET.SubElement(deontic_el, f"{{{_NS['lrml']}}}Condition")
                cond_el.text = c.condition.get("condition_text", "")

            # Proposition (action + patient)
            prop = ET.SubElement(deontic_el, f"{{{_NS['lrml']}}}Proposition")
            atom = ET.SubElement(prop, "atom")
            op_el = ET.SubElement(atom, "op")
            rel = ET.SubElement(op_el, "rel")
            rel.text = c.action

            if c.patient:
                arg = ET.SubElement(atom, "arg")
                ind = ET.SubElement(arg, "ind")
                ind.text = c.patient

            # Bearer (agent)
            if c.agent:
                bearer = ET.SubElement(deontic_el, f"{{{_NS['lrml']}}}Bearer")
                agent_el = ET.SubElement(bearer, f"{{{_NS['lrml']}}}Agent")
                agent_el.text = c.agent

            # Cross-references
            for ref in c.cross_refs:
                ref_el = ET.SubElement(stmt, f"{{{_NS['lrml']}}}CrossReference")
                ref_el.text = ref

            # Numeric metadata
            for nv in c.numeric_values:
                meta = ET.SubElement(stmt, f"{{{_NS['lrml']}}}Metadata")
                meta.set("type", "numeric_value")
                meta.set("value", str(nv.get("value", "")))
                meta.set("unit", str(nv.get("unit") or ""))

            # Confidence
            conf_el = ET.SubElement(stmt, f"{{{_NS['lrml']}}}Metadata")
            conf_el.set("type", "confidence")
            conf_el.set("value", str(c.confidence))

            # Flags
            for flag in c.flags:
                flag_el = ET.SubElement(stmt, f"{{{_NS['lrml']}}}Metadata")
                flag_el.set("type", "flag")
                flag_el.text = flag

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        logger.info(
            "Written LegalRuleML \u2192 %s (%d statements)",
            output_path,
            len(constraints),
        )
