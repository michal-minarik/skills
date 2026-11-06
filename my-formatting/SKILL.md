---
name: my-formatting
description: >-
  Google Docs and Markdown formatting skill (/my-formatting), separated from
  my_voice. Enforces 4-level indentation, blue headers with black text, Q&A
  blocks, and short sentences (15-20 words max).
---

# My Formatting Skill (`my-formatting`)

* **Question:**
  * When should we use `my-formatting`, and how does it relate to `my_voice`?
* **Answer:**
  * Use `my-formatting` whenever creating, formatting, or importing any Google Doc or Markdown file:
    * **Strict Separation of Concerns:**
      * `my_voice` governs who speaks and how we frame arguments (persona, stance, and tone).
      * `my-formatting` governs how we structure, indent, and style text on the page.
    * **Final Layout Authority:**
      * `my-formatting` has final authority over sentence length, bullet depth, and color rules.
      * It overrides dense prose paragraphs and multi-color badges in default Google Docs skills.

---

## 1. First Principles: Human Readability in the Age of AI Slop

* **Question:**
  * Why do default AI-generated documents fail human readers?
* **Answer:**
  * Default LLM output floods the brain with walls of text across five failure modes:
    * **Working-Memory Overflow (The 80-Word Sentence Trap):**
      * LLMs pack 5 facts and 4 metrics into a single 80-word sentence.
      * Human working memory holds only 3 to 4 chunks at once.
      * By word 25, readers forget how the sentence started and skim blindly.
    * **Christmas-Tree Visual Noise:**
      * Agent tools wrap every number and price in Markdown backticks.
      * `gdocs mutate import-md` renders every backtick span in green `Roboto Mono` (`#188038`).
      * Adding red/green badges, grey text, and shaded boxes creates visual chaos.
      * When everything is colored, nothing stands out (use Blue headers and Black text).
    * **Flat Left-Margin Walls (Zero Spatial Hierarchy):**
      * Flushing headers, questions, and lists to 0pt hides how ideas relate.
      * Deep spatial indentation (3 to 4 levels) builds a visual tree for instant scanning.
    * **The ESL Translation Tax (99% Non-Native English Audience):**
      * Nearly all (99%) of our partner teams read English as a second language.
      * Ornate words and nested clauses force readers to decode grammar before business meaning.
      * Simple English and active voice remove that translation friction immediately.
    * **Missing Cognitive Shortcuts (Prose Without a Question):**
      * Opening with a dense declarative paragraph hides the problem being solved.
      * Putting a short Question first gives the reader an instant mental index.

---

## 2. The 8 Hard Formatting Laws

### Law 1: Deep, Relevant Indentation (3 to 4+ Levels)

* **Question:**
  * How should we indent headings, questions, answers, and bullets in Google Docs?
* **Answer:**
  * Indent every parent-child layer by 36pt (0.5 inch per level):
    * **Level 0 (0pt — Left Margin):**
      * Document and section headings (`HEADING_1`, `HEADING_2`, `HEADING_3`).
      * Top-level metadata or summary labels on their own line (such as `**Executive Snapshot:**`).
    * **Level 1 (36pt — 1st Indent):**
      * Standalone `**Question:**` and `**Answer:**` labels under a heading (bold black).
      * Metadata values placed on lines beneath a Level-0 metadata label.
      * Top-level black bullet points (`•`) under `**Executive Snapshot:**` or a header.
    * **Level 2 (72pt — 2nd Indent):**
      * The Question sentence (placed on the line below `**Question:**`).
      * The Answer lead sentence (placed on the line below `**Answer:**`).
      * Second-level sub-bullets (`◦`) breaking down a Level-1 bullet.
      * Standalone `**Details:**` label when deep technical evidence follows an Answer.
    * **Level 3 (108pt — 3rd Indent):**
      * Black bullet points (`•` / `▪`) inside an Answer listing causes or steps.
      * Technical content, telemetry, and tables inside a `**Details:**` block.
    * **Level 4 (144pt — 4th Indent):**
      * Child sub-bullets (`◦`) under a Level-3 Answer bullet (metrics, links, or proofs).

```text
### #1 Topic Header (Level 0: 0pt, HEADING_3 Blue #4A86E8)
    Question: (Level 1: 36pt, Bold Black)
        How do we fix the license gap and row-security bypass? (Level 2: 72pt)
    Answer: (Level 1: 36pt, Bold Black)
        Broad SAML groups gave 3,500 users full developer rights. (Level 2: 72pt)
        New Direct contract caps seats at 2,940 total: (Level 2: 72pt)
            • 450 Developer seats ($37.50/mo) (Level 3: 108pt)
            • 1,780 Standard seats ($6.00/mo) (Level 3: 108pt)
            • 710 Viewer seats ($6.00/mo) (Level 3: 108pt)
        We fix compliance and security in three steps: (Level 2: 72pt)
            • Remove 1,500 inactive SAML accounts (60-90d idle) (Level 3: 108pt)
            • Revoke SQL Runner from general analysts (Level 3: 108pt)
                ◦ Closes the country filter bypass (case #123456) (Level 4: 144pt)
            • Roll out a Standard "CI Debugger" role (Level 3: 108pt)
```

---

### Law 2: Single Color (Blue) for Headers — Everything Else ONLY Black

* **Question:**
  * Which colors are allowed in Google Docs and Markdown deliverables?
* **Answer:**
  * Reserve color strictly for headers and keep all body text pure black:
    * **Headers = Blue Only:**
      * Use `#1155CC` for `HEADING_1` and `#4A86E8` for `HEADING_2` and `HEADING_3`.
      * Standard clickable links also use underlined `#1155CC` blue.
    * **Body Text, Bullets, Numbers & IDs = Pure Black (`#000000`):**
      * Keep all paragraphs, bullets, bold labels, numbers, and prices pure black (`#000000`).
      * Always use a clean white background (`backgroundColor: none`).
    * **Banish Green `#188038` Backtick Splatter:**
      * `gdocs mutate import-md` colors every Markdown code span in green `Roboto Mono` (`#188038`).
      * Never wrap numbers, prices ($400k), percentages (100%), or seat counts (~3,500) in backticks.
      * Always run `scripts/apply_my_formatting.py` after import to reset inline code to black (`#000000`).
      * Never use colored status words, shaded callout boxes, or grey body text.

---

### Law 3: Black Bullet Lists Over Inline Enumerations

* **Question:**
  * How should we present two or more related data points or ideas?
* **Answer:**
  * Break any sentence with 2 or more items into an indented black bullet list:
    * **Bad (Inline Enumeration):**
      * *"Cymbal signed a 2-year contract ($400k ACV) serving ~2,000 WAU and ~1.6M queries."*
    * **Good (Nested Black Bullet List):**
      * **Newly signed 2-year Direct Looker contract:**
        * $400k ACV ($800k TCV)
        * 2026-09-01 to 2028-08-31
      * **Serving ~2,000 weekly active users:**
        * 6,387 database users
        * ~3,500 enabled seats
        * ~1.6M weekly queries (10M+/mo)

---

### Law 4: Concise Question / Answer Format (Question First)

* **Question:**
  * How do we structure sections so executives can scan them in seconds?
* **Answer:**
  * Put a short Question first, followed immediately by an indented Answer:
    * **Why Question First:**
      * A question tells the reader in 3 seconds what problem we are solving.
      * Readers can read the Answer below or jump straight to the next header.
    * **Exact 5-Line Layout:**
      * **Topic Header (`HEADING_3`, 0pt, Blue `#4A86E8`):** Short numbered topic title.
      * **`**Question:**` (36pt, Bold Black):** Placed on its own standalone line.
      * **Question Sentence (72pt, Black):** One crisp question (15 to 20 words max).
      * **`**Answer:**` (36pt, Bold Black):** Placed on its own standalone line.
      * **Answer Content (72pt lead + 108pt/144pt bullets):** One short lead sentence plus black bullets.

---

### Law 5: Simple English (For 99% Non-Native English Speakers)

* **Question:**
  * What vocabulary and grammar rules keep documents effortless to read globally?
* **Answer:**
  * Write in simple, direct international English using active voice:
    * **Active Voice Only (`Subject -> Verb -> Object`):**
      * Write *"SQL Runner bypasses country filters"* (never passive voice).
    * **Simple Words Over Corporate Jargon:**
      * Write `use` (instead of `utilize` or `leverage`).
      * Write `fix` or `close` (instead of `remediate` or `mitigate`).
      * Write `split` or `separate` (instead of `federate` or `decouple`).
      * Write `remove` (instead of `de-provision`).
      * Write `because` (never `due to the fact`).
    * **Zero Contrastive Negations:**
      * Never write *"This is not X, it is Y"*; state what is true directly.

---

### Law 6: Short Sentences Only (15–20 Words Max; >20 Words Banished)

* **Question:**
  * What is the maximum allowed word count for any sentence or bullet?
* **Answer:**
  * Enforce a hard ceiling of 15 to 20 words per sentence:
    * **Target Word Counts:**
      * Bullet points: 3 to 12 words.
      * Lead sentences and Questions: 10 to 18 words.
      * Hard maximum: 20 words (anything above 20 words is banished).
    * **How to Fix Any Sentence Over 20 Words:**
      * Delete throat-clearing intros (*"Crucially, following the recent transition..."*).
      * Split compound sentences (`and`, `while`, `which`) into two short sentences.
      * Convert the second half of the sentence into indented child bullets (+36pt).

---

### Law 7: Parentheses for Quick Details (Strict Max 6 Words Inside)

* **Question:**
  * How should we share micro-details like dates, IDs, or quick metrics?
* **Answer:**
  * Tuck micro-details inside parentheses `(...)` with at most 6 words inside:
    * **Good Examples (6 Words or Fewer):**
      * `(10M+ queries/mo)` — 2 words.
      * `(dedicated GCP in europe-west3)` — 4 words.
      * `(15 of 19 support cases)` — 5 words.
      * `(closed unresolved after 3 weeks)` — 5 words.
    * **Rule for Longer Details (Over 6 Words):**
      * Never put more than 6 words inside `(...)`.
      * Promote any detail over 6 words to a child bullet (+36pt).

---

### Law 8: Always Check & Apply Default Google Docs Paragraph Styles

* **Question:**
  * Which Google Docs paragraph styles (`namedStyles`) must every document use?
* **Answer:**
  * Always inspect and enforce the saved Google Docs default styles:
    * **`NORMAL_TEXT`:**
      * Font: `Google Sans`, 10pt, weight 400.
      * Color: Pure Black (`#000000`).
      * Spacing: 100 line spacing (1.0 single), `NEVER_COLLAPSE`, 0pt above and below.
    * **`HEADING_1`:**
      * Font: `Google Sans`, 14pt, Bold, Blue `#1155CC`.
      * Spacing: 100 line spacing, `keepLinesTogether`, `keepWithNext`, `NEVER_COLLAPSE`.
    * **`HEADING_2`:**
      * Font: `Google Sans`, 12pt, Bold, Cornflower Blue `#4A86E8`.
      * Spacing: 100 line spacing, `keepLinesTogether`, `keepWithNext`, `NEVER_COLLAPSE`.
    * **`HEADING_3`:**
      * Font: `Google Sans`, 10pt, Bold, Cornflower Blue `#4A86E8`.
      * Spacing: 100 line spacing, `keepLinesTogether`, `keepWithNext`, `NEVER_COLLAPSE`.
    * **`HEADING_4` to `HEADING_6`, `TITLE`, and `SUBTITLE`:**
      * `HEADING_4`: `Google Sans`, 12pt, `#666666` (14pt above, 4pt below).
      * `HEADING_5`: `Google Sans`, 11pt, `#666666` (12pt above, 4pt below).
      * `HEADING_6`: `Google Sans`, 11pt Italic, `#666666` (12pt above, 4pt below).
      * `TITLE`: `Google Sans`, 26pt, Pure Black (`#000000`), 3pt below.
      * `SUBTITLE`: `Arial`, 15pt, `#666666`, 16pt below.

---

## 3. Mandatory 3-Step Execution Workflow

* **Question:**
  * How do we verify and apply `my-formatting` on every Markdown file and Google Doc?
* **Answer:**
  * Run this 3-step pipeline before sharing any deliverable:
    * **Step 1: Lint Markdown Locally (Zero Violations Allowed):**
      * Draft the file using all 8 laws above.
      * Run `apply_my_formatting.py --lint` and fix every reported error until 0 remain:

```bash
python3 ~/.gemini/config/skills/my-formatting/scripts/apply_my_formatting.py \
  --lint /path/to/draft.md
```

    * **Step 2: Import or Update the Google Doc:**
      * Import the lint-verified Markdown file using `gdocs mutate import-md`:

```bash
/google/bin/releases/gemini-agents-gdocs/gdocs mutate import-md /path/to/draft.md \
  --title "Document Title"
```

    * **Step 3: Enforce `namedStyles`, Pure Black Text & 4-Level Indentation:**
      * Run `apply_my_formatting.py --doc-id` right after import to overwrite `--polish-layout`:

```bash
python3 ~/.gemini/config/skills/my-formatting/scripts/apply_my_formatting.py \
  --doc-id <DOC_ID> \
  --tab <TAB_ID> \
  --apply
```

      * Restores saved default `namedStyles` (10pt `Google Sans` and blue headers).
      * Strips `#188038` green backtick text and table colors back to pure black (`#000000`).
      * Indents `Question:`/`Answer:` (36pt), prose (72pt), and Answer bullets (108pt and 144pt).

---

## 4. References

* **Before & After Examples:**
  * [before_after_examples.md](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-formatting/references/before_after_examples.md)
* **Automated Linter & Google Docs Style Enforcer:**
  * [apply_my_formatting.py](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-formatting/scripts/apply_my_formatting.py)
