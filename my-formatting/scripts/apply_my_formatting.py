#!/usr/bin/env python3
"""Linter and Google Docs style/indentation enforcer for `my_formatting` skill.

Modes:
  1. Markdown Linter (pre-import gate):
       python3 apply_my_formatting.py --lint /path/to/draft.md

  2. Google Docs Style, Color & 4-Level Indentation Enforcer (post-import):
       python3 apply_my_formatting.py --doc-id <DOC_ID> [--tab <TAB_ID>] [--apply]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

GDOCS_BIN = "/google/bin/releases/gemini-agents-gdocs/gdocs"

# saved Google Docs default colors
BLUE_H1 = {"red": 0.06666667, "green": 0.33333334, "blue": 0.8}          # #1155CC
BLUE_H2_H3 = {"red": 0.2901961, "green": 0.5254902, "blue": 0.9098039}   # #4A86E8
GREY_H4_H6 = {"red": 0.4, "green": 0.4, "blue": 0.4}                     # #666666
PURE_BLACK = {"red": 0.0, "green": 0.0, "blue": 0.0}                     # #000000

METADATA_LABELS = {
    "prepared for:",
    "vector account:",
    "primary instance:",
    "as-of date:",
    "scope:",
    "customer:",
    "account:",
    "status:",
    "author:",
    "authors:",
}


def count_words(text: str) -> int:
    """Count words in a string after stripping Markdown formatting tokens."""
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    cleaned = re.sub(r"[*_`~#>]+", " ", cleaned)
    cleaned = re.sub(r"^[-*+]\s+", "", cleaned.strip())
    cleaned = re.sub(r"^\d+[.)]\s+", "", cleaned.strip())
    tokens = [t for t in cleaned.split() if any(c.isalnum() for c in t)]
    return len(tokens)


def lint_markdown(path: str, max_words: int = 20, warn_words: int = 15, max_paren_words: int = 6) -> int:
    """Lint a Markdown file against `my_formatting` laws."""
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        return 2

    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    errors: List[str] = []
    warnings: List[str] = []
    in_fence = False

    backtick_num_re = re.compile(r"`[~<>=$€£]*\d[\d,._/%+-]*[kKmMbB%]*`")
    paren_re = re.compile(r"(?<!\])\(([^()]+)\)")

    for lineno, raw_line in enumerate(lines, 1):
        stripped = raw_line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        if stripped.startswith("|") or stripped.startswith("---"):
            continue

        # 1. Check for Christmas-tree backticks around numbers/metrics
        for match in backtick_num_re.finditer(raw_line):
            errors.append(
                f"{path}:{lineno}: [BACKTICK_NUMBER_CHRISTMAS_TREE] "
                f"Do not wrap numbers/metrics in backticks ({match.group(0)} turns green #188038 in Google Docs)."
            )

        # 2. Check for inline Question: / Answer: labels (must be on their own line)
        qa_inline = re.match(r"^(?:[-*+]\s+)?\*\*(Question|Answer|Details):\*\*\s+\S+", stripped)
        if qa_inline:
            errors.append(
                f"{path}:{lineno}: [INLINE_QA_LABEL] "
                f"Put '**{qa_inline.group(1)}:**' on its own standalone line and indent the content on the next line."
            )

        # 3. Check parenthetical word counts (max 6 words inside (...))
        line_without_links = re.sub(r"\]\([^)]+\)", "]", raw_line)
        for pmatch in paren_re.finditer(line_without_links):
            inner = pmatch.group(1).strip()
            pwords = count_words(inner)
            if pwords > max_paren_words:
                errors.append(
                    f"{path}:{lineno}: [PAREN_OVER_{max_paren_words}_WORDS] "
                    f"Parenthetical has {pwords} words (max {max_paren_words}): '({inner})'. "
                    f"Shorten to <={max_paren_words} words or promote to a child bullet."
                )

        # 4. Check sentence / bullet word count (hard ceiling: 20 words, warning: >15 words)
        if stripped.startswith("#"):
            continue
        # Remove parentheticals <=6 words when checking core sentence length, or check both
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", stripped) if s.strip()]
        for sent in sentences:
            wcount = count_words(sent)
            if wcount > max_words:
                errors.append(
                    f"{path}:{lineno}: [SENTENCE_OVER_{max_words}_WORDS] "
                    f"Sentence/bullet has {wcount} words (max {max_words}): \"{sent[:90]}...\""
                )
            elif wcount > warn_words:
                warnings.append(
                    f"{path}:{lineno}: [WARN_SENTENCE_{warn_words}_TO_{max_words}_WORDS] "
                    f"Sentence/bullet has {wcount} words (prefer <={warn_words}): \"{sent[:80]}...\""
                )

    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    if errors:
        print(
            f"\nFAILED `my_formatting` lint: {len(errors)} error(s), {len(warnings)} warning(s).",
            file=sys.stderr,
        )
        return 1

    print(f"PASSED `my_formatting` lint: 0 errors, {len(warnings)} warning(s).")
    return 0


def build_named_style_requests(tab_id: Optional[str]) -> List[Dict[str, Any]]:
    """Build Docs API updateNamedStyle requests for default Google Docs styles."""
    specs = [
        {
            "type": "NORMAL_TEXT",
            "font": "Google Sans",
            "size": 10,
            "bold": False,
            "italic": False,
            "color": PURE_BLACK,
            "lineSpacing": 100,
            "spacingMode": "NEVER_COLLAPSE",
            "spaceAbove": 0,
            "spaceBelow": 0,
        },
        {
            "type": "HEADING_1",
            "font": "Google Sans",
            "size": 14,
            "bold": True,
            "italic": False,
            "color": BLUE_H1,
            "lineSpacing": 100,
            "spacingMode": "NEVER_COLLAPSE",
            "keepLinesTogether": True,
            "keepWithNext": True,
        },
        {
            "type": "HEADING_2",
            "font": "Google Sans",
            "size": 12,
            "bold": True,
            "italic": False,
            "color": BLUE_H2_H3,
            "lineSpacing": 100,
            "spacingMode": "NEVER_COLLAPSE",
            "keepLinesTogether": True,
            "keepWithNext": True,
        },
        {
            "type": "HEADING_3",
            "font": "Google Sans",
            "size": 10,
            "bold": True,
            "italic": False,
            "color": BLUE_H2_H3,
            "lineSpacing": 100,
            "spacingMode": "NEVER_COLLAPSE",
            "keepLinesTogether": True,
            "keepWithNext": True,
        },
        {
            "type": "HEADING_4",
            "font": "Google Sans",
            "size": 12,
            "bold": False,
            "italic": False,
            "color": GREY_H4_H6,
            "spaceAbove": 14,
            "spaceBelow": 4,
            "keepLinesTogether": True,
            "keepWithNext": True,
        },
        {
            "type": "TITLE",
            "font": "Google Sans",
            "size": 26,
            "bold": False,
            "italic": False,
            "color": PURE_BLACK,
            "spaceBelow": 3,
            "keepLinesTogether": True,
            "keepWithNext": True,
        },
    ]

    ops: List[Dict[str, Any]] = []
    for s in specs:
        text_style: Dict[str, Any] = {
            "weightedFontFamily": {"fontFamily": s["font"], "weight": 700 if s["bold"] else 400},
            "fontSize": {"magnitude": s["size"], "unit": "PT"},
            "bold": s["bold"],
            "italic": s["italic"],
            "foregroundColor": {"color": {"rgbColor": s["color"]}},
        }
        para_style: Dict[str, Any] = {
            "namedStyleType": s["type"],
        }
        p_fields = []
        if "lineSpacing" in s:
            para_style["lineSpacing"] = s["lineSpacing"]
            p_fields.append("lineSpacing")
        if "spacingMode" in s:
            para_style["spacingMode"] = s["spacingMode"]
            p_fields.append("spacingMode")
        if "spaceAbove" in s:
            para_style["spaceAbove"] = {"magnitude": s["spaceAbove"], "unit": "PT"}
            p_fields.append("spaceAbove")
        if "spaceBelow" in s:
            para_style["spaceBelow"] = {"magnitude": s["spaceBelow"], "unit": "PT"}
            p_fields.append("spaceBelow")
        if "keepLinesTogether" in s:
            para_style["keepLinesTogether"] = s["keepLinesTogether"]
            p_fields.append("keepLinesTogether")
        if "keepWithNext" in s:
            para_style["keepWithNext"] = s["keepWithNext"]
            p_fields.append("keepWithNext")

        req: Dict[str, Any] = {
            "namedStyle": {
                "namedStyleType": s["type"],
                "textStyle": text_style,
                "paragraphStyle": para_style,
            },
            "fields": (
                "namedStyleType,"
                "textStyle(weightedFontFamily,fontSize,bold,italic,foregroundColor),"
                f"paragraphStyle({','.join(p_fields)})"
            ),
        }
        if tab_id:
            req["tabId"] = tab_id
        ops.append({"op": "raw", "raw_request": {"updateNamedStyle": req}})
    return ops


def build_body_cleanup_and_indent_requests(
    body_json: Dict[str, Any], tab_id: Optional[str]
) -> List[Dict[str, Any]]:
    """Walk document body to strip Christmas-tree colors and enforce 3-4 level 36pt indentation."""
    ops: List[Dict[str, Any]] = []
    content = body_json.get("content", [])

    context = "NONE"  # NONE | METADATA | EXECUTIVE_SNAPSHOT | QUESTION | ANSWER | DETAILS
    base_bullet_indent: Optional[float] = None

    def make_range(start: int, end: int) -> Dict[str, Any]:
        r: Dict[str, Any] = {"startIndex": start, "endIndex": end}
        if tab_id:
            r["tabId"] = tab_id
        return r

    def strip_para_colors(para_obj: Dict[str, Any]) -> None:
        for pe in para_obj.get("elements", []):
            tr = pe.get("textRun")
            if not tr:
                continue
            r_start = pe.get("startIndex", 0)
            r_end = pe.get("endIndex", 0)
            if r_end <= r_start:
                continue
            ts = tr.get("textStyle", {})
            has_link = "link" in ts and bool(ts["link"].get("url"))
            if has_link:
                continue

            fg_rgb = ts.get("foregroundColor", {}).get("color", {}).get("rgbColor", {})
            bg_color = ts.get("backgroundColor", {})
            f_size = ts.get("fontSize", {}).get("magnitude")
            is_non_black = any(fg_rgb.get(c, 0.0) > 0.01 for c in ("red", "green", "blue"))
            if is_non_black or bg_color or (f_size is not None and f_size != 10):
                ops.append(
                    {
                        "op": "raw",
                        "raw_request": {
                            "updateTextStyle": {
                                "range": make_range(r_start, r_end),
                                "textStyle": {
                                    "foregroundColor": {"color": {"rgbColor": PURE_BLACK}},
                                    "backgroundColor": {},
                                    "fontSize": {"magnitude": 10, "unit": "PT"},
                                },
                                "fields": "foregroundColor,backgroundColor,fontSize",
                            }
                        },
                    }
                )

    for elem in content:
        tbl = elem.get("table")
        if tbl:
            for row in tbl.get("tableRows", []):
                for cell in row.get("tableCells", []):
                    for celem in cell.get("content", []):
                        cpara = celem.get("paragraph")
                        if cpara:
                            strip_para_colors(cpara)
            continue

        para = elem.get("paragraph")
        if not para:
            continue

        p_start = elem.get("startIndex", 0)
        p_end = elem.get("endIndex", 0)
        if p_end <= p_start:
            continue

        p_style = para.get("paragraphStyle", {})
        named_type = p_style.get("namedStyleType", "NORMAL_TEXT")
        bullet = para.get("bullet")
        is_bullet = bullet is not None
        if is_bullet:
            raw_indent = float(p_style.get("indentStart", {}).get("magnitude", 36.0))
            if base_bullet_indent is None or raw_indent < base_bullet_indent:
                base_bullet_indent = raw_indent
            inferred_nesting = max(0, int(round((raw_indent - base_bullet_indent) / 36.0)))
            nesting = max(int(bullet.get("nestingLevel", 0)), inferred_nesting)
        else:
            nesting = 0

        full_text = "".join(
            e.get("textRun", {}).get("content", "") for e in para.get("elements", [])
        ).strip()
        lower_text = full_text.lower()

        # 1. Heading paragraphs: enforce exact Blue & size, reset context
        if named_type in ("HEADING_1", "HEADING_2", "HEADING_3", "HEADING_4", "TITLE"):
            context = "NONE"
            base_bullet_indent = None
            h_color = (
                BLUE_H1
                if named_type == "HEADING_1"
                else BLUE_H2_H3
                if named_type in ("HEADING_2", "HEADING_3")
                else GREY_H4_H6
                if named_type == "HEADING_4"
                else PURE_BLACK
            )
            h_size = (
                14
                if named_type == "HEADING_1"
                else 12
                if named_type in ("HEADING_2", "HEADING_4")
                else 10
                if named_type == "HEADING_3"
                else 26
            )
            h_bold = named_type in ("HEADING_1", "HEADING_2", "HEADING_3")
            if p_end - 1 > p_start:
                ops.append(
                    {
                        "op": "raw",
                        "raw_request": {
                            "updateTextStyle": {
                                "range": make_range(p_start, p_end - 1),
                                "textStyle": {
                                    "weightedFontFamily": {"fontFamily": "Google Sans", "weight": 700 if h_bold else 400},
                                    "fontSize": {"magnitude": h_size, "unit": "PT"},
                                    "bold": h_bold,
                                    "foregroundColor": {"color": {"rgbColor": h_color}},
                                    "backgroundColor": {},
                                },
                                "fields": "weightedFontFamily,fontSize,bold,foregroundColor,backgroundColor",
                            }
                        },
                    }
                )
            continue

        # 2. Strip Christmas-tree colors (#188038 green backticks, grey, red, amber) on body runs
        strip_para_colors(para)

        if not full_text:
            continue

        # 3. Determine target indentation level (in 36pt increments)
        target_indent_start: Optional[float] = None
        target_indent_first: Optional[float] = None

        if lower_text in ("question:", "question"):
            context = "QUESTION"
            base_bullet_indent = None
            target_indent_start = 36.0
            target_indent_first = 36.0
        elif lower_text in ("answer:", "answer"):
            context = "ANSWER"
            base_bullet_indent = None
            target_indent_start = 36.0
            target_indent_first = 36.0
        elif lower_text in ("details:", "details"):
            context = "DETAILS"
            base_bullet_indent = None
            target_indent_start = 36.0
            target_indent_first = 36.0
        elif lower_text in ("executive snapshot:", "executive snapshot"):
            context = "EXECUTIVE_SNAPSHOT"
            base_bullet_indent = None
            target_indent_start = 0.0
            target_indent_first = 0.0
        elif lower_text in METADATA_LABELS:
            context = "METADATA"
            base_bullet_indent = None
            target_indent_start = 0.0
            target_indent_first = 0.0
        elif context == "METADATA" and not is_bullet:
            target_indent_start = 36.0
            target_indent_first = 36.0
        elif context == "QUESTION":
            if is_bullet:
                lvl = 3 + nesting
                target_indent_start = 36.0 * lvl
                target_indent_first = target_indent_start - 18.0
            else:
                target_indent_start = 72.0
                target_indent_first = 72.0
        elif context in ("ANSWER", "DETAILS"):
            if is_bullet:
                lvl = 3 + nesting
                target_indent_start = 36.0 * lvl
                target_indent_first = target_indent_start - 18.0
            else:
                target_indent_start = 72.0
                target_indent_first = 72.0
        elif context == "EXECUTIVE_SNAPSHOT" and is_bullet:
            lvl = 1 + nesting
            target_indent_start = 36.0 * lvl
            target_indent_first = target_indent_start - 18.0
        elif is_bullet:
            lvl = 1 + nesting
            target_indent_start = 36.0 * lvl
            target_indent_first = target_indent_start - 18.0

        if target_indent_start is not None and target_indent_first is not None:
            ops.append(
                {
                    "op": "raw",
                    "raw_request": {
                        "updateParagraphStyle": {
                            "range": make_range(p_start, p_end),
                            "paragraphStyle": {
                                "indentStart": {"magnitude": target_indent_start, "unit": "PT"},
                                "indentFirstLine": {"magnitude": target_indent_first, "unit": "PT"},
                                "lineSpacing": 100,
                                "spacingMode": "NEVER_COLLAPSE",
                            },
                            "fields": "indentStart,indentFirstLine,lineSpacing,spacingMode",
                        }
                    },
                }
            )

    return ops


def enforce_gdoc_formatting(doc_id: str, tab_id: Optional[str], apply_changes: bool) -> int:
    """Inspect a Google Doc tab and enforce default namedStyles, black text, and 4-level indentation."""
    cmd = [GDOCS_BIN, "readonly", "dump-body", doc_id]
    if tab_id:
        cmd.extend(["--tab", tab_id])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR reading doc body: {res.stderr}", file=sys.stderr)
        return 2

    body_json = json.loads(res.stdout)
    ops = build_named_style_requests(tab_id) + build_body_cleanup_and_indent_requests(body_json, tab_id)

    print(f"Compiled {len(ops)} Docs API formatting operations for doc={doc_id} tab={tab_id or 'default'}.")
    if not apply_changes:
        print("Dry-run complete (pass --apply to execute batch update).")
        return 0

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
        json.dump(ops, tf, indent=2)
        ops_path = tf.name

    try:
        bcmd = [GDOCS_BIN, "mutate", "batch", doc_id, "--direct", "-f", ops_path]
        if tab_id:
            bcmd.extend(["--tab", tab_id])
        bres = subprocess.run(bcmd, capture_output=True, text=True)
        if bres.returncode != 0:
            print(f"ERROR applying formatting batch: {bres.stderr}", file=sys.stderr)
            return 1
        print(bres.stdout.strip())
        print("Successfully applied `my_formatting` styles, black text, and 4-level indentation.")
        return 0
    finally:
        if os.path.exists(ops_path):
            os.remove(ops_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="`my_formatting` linter and Google Docs style enforcer.")
    parser.add_argument("--lint", metavar="MARKDOWN_FILE", help="Lint a Markdown file against `my_formatting` rules.")
    parser.add_argument("--max-words", type=int, default=20, help="Hard maximum words per sentence (default: 20).")
    parser.add_argument("--warn-words", type=int, default=15, help="Warning threshold words per sentence (default: 15).")
    parser.add_argument("--max-paren-words", type=int, default=6, help="Hard maximum words inside (...) (default: 6).")
    parser.add_argument("--doc-id", metavar="DOC_ID", help="Google Doc ID to apply `my_formatting` styles and indentation.")
    parser.add_argument("--tab", metavar="TAB_ID", help="Optional target tab ID (e.g. t.0).")
    parser.add_argument("--apply", action="store_true", help="Execute the compiled batch update on the Google Doc.")

    args = parser.parse_args()
    if not args.lint and not args.doc_id:
        parser.print_help()
        return 2

    rc = 0
    if args.lint:
        rc = lint_markdown(args.lint, args.max_words, args.warn_words, args.max_paren_words)
        if rc != 0:
            return rc

    if args.doc_id:
        rc = enforce_gdoc_formatting(args.doc_id, args.tab, args.apply)

    return rc


if __name__ == "__main__":
    sys.exit(main())
