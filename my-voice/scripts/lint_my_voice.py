#!/usr/bin/env python3
"""Deterministic linter for `my-voice` skill (Michal Minařík).

Checks Markdown or text drafts against Michal's `my-voice` rules:
  1. EXCLAMATION_MARK_BANNED: Bans '!' in prose (calm, matter-of-fact tone).
  2. LONG_DASH_BANNED: Bans em-dashes (—) and en-dashes (–) -> use short '-'.
  3. OUTDATED_GCP_TERMINOLOGY: Bans 'Vertex AI', 'Agentspace', 'Vertex AI Search',
     'Reasoning Engine', 'Gen App Builder', 'Duet AI' -> enforces current names
     ('Gemini Enterprise Agent Platform', 'Agent Studio', 'Agent Runtime',
     'Gemini Enterprise').
  4. FILLER_OR_HYPE_PHRASE: Bans English and Czech filler/hype pleasantries
     ('I hope this email finds you well', 'thrilled', 'excited', 'seamlessly',
     'game-changing', 'Doufám, že se máte skvěle', 'S velkým nadšením', etc.).
  5. UNSOLICITED_CALL_OFFER: Flags automatic call/meeting offers ('hop on a call',
     'jump on a call', 'quick call to discuss', 'zavoláme si') unless --allow-call.
  6. CUSTOMER_LABEL_USED: Flags 'customer' / 'customers' / 'client' / 'clients'
     in English prose -> prompts replacing with 'team' / 'teams'.
  7. POSSESSIVE_PEOPLE_LABEL: Bans 'your engineers', 'your people',
     'your developers', 'your staff' -> never imply possession of people.
  8. UNFORCED_DEADLINE_PROMISE: Flags 'by the end of today', 'by EOD today',
     'right away' -> push urgency without handing out free deadlines.
  9. INTERNAL_PLUMBING_EXPOSURE: Flags 'loop in our ... engineering team',
     'assigned Support engineer', 'pull the backend ... trace' -> use
     'review internally' or 'to expedite the diagnostic process'.
  10. POSSESSIVE_ENGINE_ARTICLE: Flags 'our <region/product> engine' -> use
      neutral 'the <region/product> engine'.
  11. STIFF_AI_TRANSITION: Flags 'Looking at the details you included',
      'data points stand out', 'two data points'.
  12. CONTRASTIVE_NEGATION_SLOP: Flags AI-slop contrastive negations such as
      'is not X, it is Y', 'not only X, but Y', 'not about X, it's about Y'.
  13. AI_SLOP_BUZZWORD: Flags ornate/AI-slop words ('delve', 'tapestry',
      'testament', 'underscore', 'symphony', 'utilize', 'leverage', 'remediate',
      'mitigate', 'federate', 'de-provision', 'due to the fact that').
  14. PASSIVE_DELAY_PHRASE: Flags slow/passive timeline phrases ('at your
      earliest convenience', 'when you get a chance', 'in due course',
      'whenever possible') -> prompts Now > Today > Tomorrow > Next Week.

Usage:
  python3 lint_my_voice.py --lint /path/to/draft.md [--allow-call]
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


OUTDATED_GCP_TERMS = re.compile(
    r"\b(?:Vertex\s+AI\s+Agent\s+Builder|Vertex\s+AI\s+Agent\s+Engine|"
    r"Vertex\s+AI\s+Search|Vertex\s+AI\s+Platform|Vertex\s+AI|"
    r"Gen\s+App\s+Builder|Reasoning\s+Engine|Agentspace|Duet\s+AI)\b",
    re.IGNORECASE,
)

FILLER_HYPE_PHRASES = re.compile(
    r"\b(?:hope\s+this\s+email\s+finds\s+you\s+well|"
    r"hope\s+you(?:'re|\s+are)\s+having\s+a\s+great\s+week|"
    r"thrilled\s+to|excited\s+to\s+share|delighted\s+to\s+share|"
    r"we\s+would\s+love\s+to|great\s+question|spot\s+on|"
    r"incredibly|seamlessly|game-changing|"
    r"doufám,\s*že\s+se\s+máte\s+skvěle|s\s+velkým\s+nadšením|"
    r"skvělá\s+otázka|naprosto\s+úžasné)\b",
    re.IGNORECASE,
)

UNSOLICITED_CALL_OFFERS = re.compile(
    r"\b(?:hop\s+on\s+a\s+(?:quick\s+)?call|jump\s+on\s+a\s+(?:quick\s+|15-minute\s+)?call|"
    r"rád\s+si\s+s\s+vámi\s+zavolám|hodil\s+by\s+se\s+vám\s+krátký\s+telefonát)\b",
    re.IGNORECASE,
)

CUSTOMER_WORDS = re.compile(
    r"\b(?:customer|customers|client|clients)\b",
    re.IGNORECASE,
)

POSSESSIVE_PEOPLE_LABELS = re.compile(
    r"\byour\s+(?:engineers|engineer|people|developers|developer|staff|folks|architects|analysts)\b",
    re.IGNORECASE,
)

UNFORCED_DEADLINE_PROMISES = re.compile(
    r"\b(?:by\s+the\s+end\s+of\s+today|by\s+end\s+of\s+day\s+today|by\s+EOD\s+today|right\s+away)\b",
    re.IGNORECASE,
)

INTERNAL_PLUMBING_EXPOSURE = re.compile(
    r"\b(?:loop\s+in\s+our\s+[^.,;:\n]{1,35}\s+(?:engineering\s+)?team|"
    r"assigned\s+support\s+engineer|pull\s+the\s+backend\s+[^.,;:\n]{1,25}\s*trace)\b",
    re.IGNORECASE,
)

POSSESSIVE_ENGINE_ARTICLES = re.compile(
    r"\bour\s+(?:EU|US|multi-region|regional|BigQuery|Lakehouse|federated|cross-cloud)\s+engine\b",
    re.IGNORECASE,
)

STIFF_AI_TRANSITIONS = re.compile(
    r"\b(?:looking\s+at\s+the\s+details\s+you\s+included|data\s+points\s+stand\s+out|"
    r"two\s+data\s+points|three\s+data\s+points|several\s+data\s+points)\b",
    re.IGNORECASE,
)

CONTRASTIVE_NEGATIONS = re.compile(
    r"\b(?:is\s+not\s+[^.,;:\n]{2,45},\s*it\s+is|"
    r"isn't\s+[^.,;:\n]{2,45},\s*it's|"
    r"are\s+not\s+[^.,;:\n]{2,45},\s*they\s+are|"
    r"not\s+about\s+[^.,;:\n]{2,45},\s*(?:it\s+is|it's|but)\s+about|"
    r"not\s+only\s+[^.,;:\n]{2,45},\s*but\s+also)\b",
    re.IGNORECASE,
)

AI_SLOP_BUZZWORDS = re.compile(
    r"\b(?:delve|delves|delving|tapestry|testament|symphony|underscores|"
    r"utilize|utilizes|utilizing|utilization|leverage|leverages|leveraging|"
    r"remediate|remediation|mitigate|federate|de-provision|due\s+to\s+the\s+fact\s+that)\b",
    re.IGNORECASE,
)

PASSIVE_DELAY_PHRASES = re.compile(
    r"\b(?:at\s+your\s+earliest\s+convenience|when\s+you\s+get\s+a\s+chance|"
    r"in\s+due\s+course|whenever\s+possible|if\s+and\s+when\s+you\s+have\s+time)\b",
    re.IGNORECASE,
)


def lint_file(path: pathlib.Path, allow_call: bool = False) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    errors: list[tuple[int, str, str]] = []
    in_code_block = False
    in_frontmatter = False

    for idx, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        if idx == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not stripped:
            continue

        # Skip Markdown table rows (which document mappings like Outdated -> Current)
        if stripped.startswith("|"):
            continue

        # Strip URLs and quoted negative examples when linting documentation about bans
        clean_line = re.sub(r"https?://\S+", "", raw_line)
        clean_unquoted = re.sub(r'"[^"]*"', "", clean_line)
        clean_unquoted = re.sub(r"“[^”]*”", "", clean_unquoted)

        # 1. Check for exclamation marks (!)
        if "!" in clean_unquoted:
            errors.append((
                idx,
                "EXCLAMATION_MARK_BANNED",
                "Found '!' - keep tone calm and matter-of-fact without exclamation marks.",
            ))

        # 2. Check for long dashes (em-dash / en-dash)
        if "\u2014" in clean_unquoted or "\u2013" in clean_unquoted:
            errors.append((
                idx,
                "LONG_DASH_BANNED",
                "Found em-dash or en-dash - always use standard ASCII short hyphen '-'.",
            ))

        # 3. Check for outdated GCP terminology (ignore 'Never use Vertex AI' rule explanation)
        if "never use **vertex ai**" not in clean_unquoted.lower():
            for m in OUTDATED_GCP_TERMS.finditer(clean_unquoted):
                errors.append((
                    idx,
                    "OUTDATED_GCP_TERMINOLOGY",
                    f'Found outdated term "{m.group(0)}" - use Gemini Enterprise Agent Platform / Agent Studio / Agent Runtime / Gemini Enterprise.',
                ))

        for m in FILLER_HYPE_PHRASES.finditer(clean_unquoted):
            errors.append((
                idx,
                "FILLER_OR_HYPE_PHRASE",
                f'Found filler/hype phrase "{m.group(0)}" - use direct, matter-of-fact prose.',
            ))

        if not allow_call:
            for m in UNSOLICITED_CALL_OFFERS.finditer(clean_unquoted):
                errors.append((
                    idx,
                    "UNSOLICITED_CALL_OFFER",
                    f'Found call offer "{m.group(0)}" - default to async communication unless Michal explicitly asks to propose a call.',
                ))

        # Ignore "Customer Support" or "Customer Engineer" role titles when checking customer label
        clean_no_titles = re.sub(
            r"\bCustomer\s+(?:Engineer|Support)\b", "", clean_unquoted, flags=re.IGNORECASE
        )
        for m in CUSTOMER_WORDS.finditer(clean_no_titles):
            errors.append((
                idx,
                "CUSTOMER_LABEL_USED",
                f'Found "{m.group(0)}" - refer to external counterparts as "team" / "teams".',
            ))

        for m in POSSESSIVE_PEOPLE_LABELS.finditer(clean_unquoted):
            errors.append((
                idx,
                "POSSESSIVE_PEOPLE_LABEL",
                f'Found "{m.group(0)}" - never imply possession of people; use "the engineers" / "the team".',
            ))

        for m in UNFORCED_DEADLINE_PROMISES.finditer(clean_unquoted):
            errors.append((
                idx,
                "UNFORCED_DEADLINE_PROMISE",
                f'Found "{m.group(0)}" - push urgency naturally without giving out free deadlines.',
            ))

        for m in INTERNAL_PLUMBING_EXPOSURE.finditer(clean_unquoted):
            errors.append((
                idx,
                "INTERNAL_PLUMBING_EXPOSURE",
                f'Found "{m.group(0)}" - abstract internal escalations/support into "review internally" or "to expedite the diagnostic process".',
            ))

        for m in POSSESSIVE_ENGINE_ARTICLES.finditer(clean_unquoted):
            errors.append((
                idx,
                "POSSESSIVE_ENGINE_ARTICLE",
                f'Found "{m.group(0)}" - use neutral "the" instead of "our" for engines/infrastructure.',
            ))

        for m in STIFF_AI_TRANSITIONS.finditer(clean_unquoted):
            errors.append((
                idx,
                "STIFF_AI_TRANSITION",
                f'Found "{m.group(0)}" - replace stiff AI transitions with natural phrasing.',
            ))

        for m in CONTRASTIVE_NEGATIONS.finditer(clean_unquoted):
            errors.append((
                idx,
                "CONTRASTIVE_NEGATION_SLOP",
                f'Found "{m.group(0)}" - write direct, affirmative prose.',
            ))

        for m in AI_SLOP_BUZZWORDS.finditer(clean_unquoted):
            errors.append((
                idx,
                "AI_SLOP_BUZZWORD",
                f'Found "{m.group(0)}" - replace with simple, direct English.',
            ))

        for m in PASSIVE_DELAY_PHRASES.finditer(clean_unquoted):
            errors.append((
                idx,
                "PASSIVE_DELAY_PHRASE",
                f'Found "{m.group(0)}" - push for Now > Today > Tomorrow > Next Week.',
            ))

    if errors:
        print(f"[my-voice LINT FAILED] {len(errors)} issue(s) in {path}:")
        for line_no, code, detail in errors:
            loc = f"Line {line_no}" if line_no > 0 else "Document"
            print(f"  - {loc} [{code}]: {detail}")
        return 1

    print(f"[my-voice LINT PASSED] 0 violations in {path}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint drafts against my-voice rules.")
    parser.add_argument("--lint", required=True, type=pathlib.Path, help="Path to Markdown/text file.")
    parser.add_argument(
        "--allow-call",
        action="store_true",
        help="Allow meeting/call proposals when explicitly requested by Michal.",
    )
    args = parser.parse_args()
    return lint_file(args.lint, args.allow_call)


if __name__ == "__main__":
    sys.exit(main())
