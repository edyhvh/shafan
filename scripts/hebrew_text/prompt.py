"""Prompt building from YAML configuration."""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def load_yaml(path: Path) -> Dict[str, Any]:
    """
    Load YAML file using PyYAML.

    Args:
        path: Path to YAML file

    Returns:
        Dictionary containing YAML data

    Raises:
        FileNotFoundError: If YAML file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError(f"YAML file is empty: {path}")

    return data


def get_yaml_version(yaml_data: Dict[str, Any]) -> str:
    """
    Extract version from YAML metadata.

    Args:
        yaml_data: YAML data dictionary

    Returns:
        Version string
    """
    metadata = yaml_data.get('metadata', {})
    return metadata.get('version', 'unknown')


def calculate_yaml_hash(yaml_content: str) -> str:
    """
    Generate SHA256 hash for versioning.

    Args:
        yaml_content: YAML file content as string

    Returns:
        SHA256 hash hex string
    """
    import hashlib
    return hashlib.sha256(yaml_content.encode('utf-8')).hexdigest()


def build_prompt(yaml_data: Dict[str, Any]) -> str:
    """
    Construct full prompt from YAML rules.

    Args:
        yaml_data: YAML data dictionary

    Returns:
        Complete prompt string
    """
    # Get base template
    vision_template = yaml_data.get('vision_prompt_template', {})
    role = vision_template.get('role', 'Expert Paleographer')
    task = vision_template.get('task', '')

    # Start building prompt
    prompt_parts = [f"You are {role}.\n\n{task}\n"]

    # Add CRITICAL rules at the very beginning
    prompt_parts.append("## ⚠️ CRITICAL TRANSCRIPTION RULES - READ FIRST\n")
    prompt_parts.append("🔴 WORD SPACING: Every word MUST be separated by a space. NEVER concatenate words.")
    prompt_parts.append("🔴 CORRECT: 'וְנַצְרוּ אֶת־נַפְשׁוֹתֵיכֶם בְּאַהֲבַת אֱלֹהִים'")
    prompt_parts.append("🔴 WRONG: 'וְנַצְרוּאֶת־נַפְשׁוֹתֵיכֶםבְּאַהֲבַתאֱלֹהִים'")
    prompt_parts.append("🔴 NEVER include ׃ (Sof Pasuq) in 'text_nikud' - EXCLUDE COMPLETELY")
    prompt_parts.append("🔴 NEVER include \\n or line breaks in 'text_nikud' - ONE CONTINUOUS STRING ONLY")
    prompt_parts.append("🔴 COLUMN ISOLATION: ONLY transcribe the CENTRAL Hebrew column. Ignore Latin, Greek, German.")
    prompt_parts.append("🔴 If you violate these rules, the transcription is INVALID\n")

    # Add CRITICAL word spacing rule first
    word_spacing = yaml_data.get('text_layout_rules', {}).get('word_spacing', {})
    if word_spacing.get('rule'):
        prompt_parts.append(f"\n## ⚠️ WORD SPACING RULE (MANDATORY)\n{word_spacing.get('rule')}")
        if word_spacing.get('description'):
            prompt_parts.append(f"\n{word_spacing.get('description')}")

    # Add Hutter typography rule
    hutter_typo = yaml_data.get('text_layout_rules', {}).get('hutter_typography', {})
    if hutter_typo.get('rule'):
        prompt_parts.append(f"\n## Hutter's Typography System\n{hutter_typo.get('rule')}")
        if hutter_typo.get('description'):
            prompt_parts.append(f"\n{hutter_typo.get('description')}")

    # Add column isolation rule
    column_iso = yaml_data.get('text_layout_rules', {}).get('column_isolation', {})
    if column_iso.get('rule'):
        prompt_parts.append(f"\n## Column Isolation Rule\n{column_iso.get('rule')}")
        if column_iso.get('description'):
            prompt_parts.append(f"\n{column_iso.get('description')}")

    # Add character confusion prevention rule
    char_confusion = yaml_data.get('text_layout_rules', {}).get('character_confusion', {})
    if char_confusion.get('rule'):
        prompt_parts.append(f"\n## Character Confusion Prevention\n{char_confusion.get('rule')}")
        if char_confusion.get('description'):
            prompt_parts.append(f"\n{char_confusion.get('description')}")

    # Add paleographic priority rule
    paleographic = yaml_data.get('text_layout_rules', {}).get('paleographic_priority', {})
    if paleographic.get('rule'):
        prompt_parts.append(f"\n## Paleographic Priority Rule\n{paleographic.get('rule')}")
        if paleographic.get('description'):
            prompt_parts.append(f"\n{paleographic.get('description')}")

    # Add lexical fidelity rule
    lexical = yaml_data.get('text_layout_rules', {}).get('lexical_fidelity', {})
    if lexical.get('rule'):
        prompt_parts.append(f"\n## Lexical Fidelity Rule\n{lexical.get('rule')}")
        if lexical.get('description'):
            prompt_parts.append(f"\n{lexical.get('description')}")

    # Add advanced vocalization rules
    advanced_voc = yaml_data.get('text_layout_rules', {}).get('advanced_vocalization', {})
    if advanced_voc:
        prompt_parts.append("\n## Advanced Vocalization Rules")

        # Hataf vowels
        hataf = advanced_voc.get('hataf_vowels', {})
        if hataf.get('rule'):
            prompt_parts.append(f"\n### Hataf Vowels\n{hataf.get('rule')}")

        # Vav distinction
        vav = advanced_voc.get('vav_distinction', {})
        if vav.get('rule'):
            prompt_parts.append(f"\n### Vav Distinction\n{vav.get('rule')}")

        # Dagesh verification
        dagesh = advanced_voc.get('dagesh_verification', {})
        if dagesh.get('rule'):
            prompt_parts.append(f"\n### Dagesh Verification\n{dagesh.get('rule')}")
            if dagesh.get('warning'):
                prompt_parts.append(f"\n⚠️ Warning: {dagesh.get('warning')}")

        # Composite marks
        composite = advanced_voc.get('composite_marks', {})
        if composite.get('rule'):
            prompt_parts.append(f"\n### Composite Marks\n{composite.get('rule')}")

    # Add ornamented initials rule
    ornamented = yaml_data.get('text_layout_rules', {}).get('ornamented_initials', {})
    if ornamented.get('rule'):
        prompt_parts.append(f"\n## Ornamented Initial Letters")
        prompt_parts.append(f"{ornamented.get('rule')}")
        prompt_parts.append("Note: Enlarged/ornamented letters are part of the word - include them")

    # Add auxiliary Hebrew text to ignore
    auxiliary = yaml_data.get('text_layout_rules', {}).get('auxiliary_hebrew_text_to_ignore', {})
    root_markers = auxiliary.get('root_markers', {})
    if root_markers.get('rule'):
        prompt_parts.append(f"\n## Auxiliary Hebrew Text to Ignore\n{root_markers.get('rule')}")

    # Add CRITICAL normalization rules
    normalization = yaml_data.get('text_layout_rules', {}).get('normalization_rules', {})
    if normalization:
        prompt_parts.append("\n## ⚠️ CRITICAL NORMALIZATION RULES - FOLLOW EXACTLY")

        makaf = normalization.get('makaf', {})
        if makaf.get('rule'):
            prompt_parts.append(f"\n### Makaf\n{makaf.get('rule')}")

        # CRITICAL: Sof Pasuq exclusion - make it extremely clear
        sof_pasuq = normalization.get('sof_pasuq', {})
        if sof_pasuq.get('rule'):
            prompt_parts.append(f"\n### 🚫 SOF PASUQ (׃) - ABSOLUTE FORBIDDEN RULE")
            prompt_parts.append(f"{sof_pasuq.get('rule')}")
            prompt_parts.append("🔴 CRITICAL: NEVER, EVER include ׃ (Sof Pasuq) in 'text_nikud'")
            prompt_parts.append("🔴 CRITICAL: Sof Pasuq is ONLY a visual marker - COMPLETELY EXCLUDE from transcription")
            prompt_parts.append("🔴 CRITICAL: If verse ends with ׃, STOP transcription BEFORE the ׃")
            prompt_parts.append("🔴 CRITICAL: Remove ׃ from the end of every verse")
            prompt_parts.append("✅ CORRECT: 'דָּבָר' (without ׃)")
            prompt_parts.append("❌ WRONG: 'דָּבָר׃' (with ׃)")

        # CRITICAL: No line breaks - make it extremely clear
        prompt_parts.append("\n### 🚫 LINE BREAKS - ABSOLUTE FORBIDDEN RULE")
        prompt_parts.append("🔴 CRITICAL: NEVER include \\n, \\r, or any line breaks in 'text_nikud'")
        prompt_parts.append("🔴 CRITICAL: 'text_nikud' MUST be one continuous string")
        prompt_parts.append("🔴 CRITICAL: If verse spans multiple lines, join them without spaces or breaks")
        prompt_parts.append("🔴 CRITICAL: Remove ALL line separators and newlines")
        prompt_parts.append("✅ CORRECT: 'שָׁלוֹם לְךָ אָחִי הַיָּקָר'")
        prompt_parts.append("❌ WRONG: 'שָׁלוֹם לְךָ\\nאָחִי הַיָּקָר'")
        prompt_parts.append("❌ WRONG: 'שָׁלוֹם לְךָ אָחִי הַיָּקָר\\n'")

        parentheses = normalization.get('parentheses', {})
        if parentheses.get('rule'):
            prompt_parts.append(f"\n### Parentheses\n{parentheses.get('rule')}")

    # Add special instructions
    prompt_parts.append("\n## Special Instructions")
    prompt_parts.append(
        "- The first verse of the first chapter uses an ornamented letter (no number marker)."
    )
    prompt_parts.append(
        "- This ornamented letter is the FIRST LETTER of the first word and must be transcribed as part of the word."
    )
    prompt_parts.append(
        "- Include the ornamented letter - it is essential for the word."
    )
    prompt_parts.append(
        "- Verses are marked with Arabic numerals (1, 2, 3...) in the right margin (RTL)."
    )
    prompt_parts.append(
        "- Chapters are marked with large centered Hebrew letters."
    )

    # Add critical isolation instructions
    prompt_parts.append("\n## CRITICAL ISOLATION RULES")
    prompt_parts.append(
        "⚠️ IMPORTANT: This is a COMPLETELY INDEPENDENT request. "
        "DO NOT remember or reference any previous images or verses."
    )
    prompt_parts.append(
        "- Treat this image as the ONLY source material. Ignore any context from previous requests."
    )
    prompt_parts.append(
        "- Start verse numbering from 1 for each new image, regardless of previous requests."
    )
    prompt_parts.append(
        "- Extract ONLY the Hebrew text visible in THIS SPECIFIC IMAGE."
    )
    prompt_parts.append(
        "- Do not continue verse sequences from previous images."
    )
    prompt_parts.append(
        "- If this appears to be a continuation page, still number verses starting from 1."
    )

    # Add output format specification
    output_spec = yaml_data.get('output_specification', {})
    if output_spec:
        prompt_parts.append("\n## Output Format")
        prompt_parts.append(
            "You must return a JSON object matching this exact structure:\n"
        )
        prompt_parts.append("""{
  "chapters": [
    {
      "hebrew_letter": "א",
      "number": 1,
      "verses": [
        {
          "number": 1,
          "text_nikud": "בְּרֵאשִׁית בָּרָא...",
          "source_files": ["000002.png"],
          "visual_uncertainty": []
        }
      ]
    }
  ]
}""")
        prompt_parts.append(
            "\n- Each verse must have: number (int), text_nikud (string with nikud), "
            "source_files (array with image filename), visual_uncertainty (array of strings, empty if none)."
        )
        prompt_parts.append(
            "- Chapters must have: hebrew_letter (string), number (int), verses (array)."
        )
        prompt_parts.append(
            "- Extract ONLY verses visible in this image. Do not include verses from other images."
        )
        prompt_parts.append(
            "- If a verse spans multiple images, include it only once per image with the visible portion."
        )

    # Add user sovereignty rule
    user_rule = yaml_data.get('user_sovereignty_rule', {})
    if user_rule.get('description'):
        prompt_parts.append(f"\n## User Sovereignty Rule\n{user_rule.get('description')}")

    # Join all parts
    full_prompt = "\n".join(prompt_parts)

    return full_prompt


