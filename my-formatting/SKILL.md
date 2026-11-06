---
name: my-formatting
description: >-
  ❤️ Unified formatting, layout, and channel mechanics skill (/my-formatting) for
  Google Docs, Markdown, Gmail drafts, and Google Chat. Enforces 4-level
  indentation, blue headers with pure black text, zero inline backticks, short
  ASCII hyphens (-), Q&A blocks in Docs, ad 1)/2) in emails, and mandatory
  Gmail HTML draft creation with signatures. Pairs with my-voice.
metadata:
  icon: ❤️
---

# ❤️ My Formatting Skill (my-formatting)

* **Question:**
  * When should we use **my-formatting**, and how does it pair with **my-voice**?
* **Answer:**
  * Use **my-formatting** when creating or formatting any Doc, Markdown, Gmail draft, or Chat message:
    * **Strict Separation of Concerns:**
      * **my-voice** governs who speaks, persona, Czech/English tone matrix, and product terminology.
      * **my-formatting** governs how we structure, indent, style, and materialize text across channels.
    * **Final Layout Authority:**
      * **my-formatting** has final authority over sentence length, bullet depth, punctuation, and color rules.
      * It overrides dense prose paragraphs, inline backtick clutter, and multi-color badges.

---

## 1. First Principles: Human Readability in the Age of AI Slop

* **Question:**
  * Why do default AI-generated documents, emails, and chat messages fail human readers?
* **Answer:**
  * Default LLM output floods the brain with walls of text across five failure modes:
    * **Working-Memory Overflow (The 80-Word Sentence Trap):**
      * LLMs pack 5 facts and 4 metrics into a single 80-word sentence.
      * Human working memory holds only 3 to 4 chunks at once.
      * By word 25, readers forget how the sentence started and skim blindly.
    * **Christmas-Tree Visual Noise & Backtick Clutter:**
      * Agent tools wrap product names, filenames, and numbers in inline backticks.
      * In Google Chat and emails, inline backticks clutter the line and break flow.
      * In Google Docs, **gdocs mutate import-md** renders backticks in green **Roboto Mono** (#188038).
      * When everything is colored or monospaced, nothing stands out.
    * **Flat Left-Margin Walls (Zero Spatial Hierarchy):**
      * Flushing headers, questions, and lists to 0pt hides how ideas relate.
      * Deep spatial indentation (3 to 4 levels) builds a visual tree for instant scanning.
    * **The ESL Translation Tax (99% Non-Native English Audience):**
      * Nearly all (99%) of our partner teams read English as a second language.
      * Ornate words and nested clauses force readers to decode grammar before business meaning.
      * Simple English and active voice remove that translation friction immediately.
    * **Missing Cognitive Shortcuts (Prose Without Structure):**
      * Opening a document with a dense paragraph hides the problem being solved.
      * Starting with a Question or numbered **ad 1)** reply gives an instant mental index.

---

## 2. The 8 Hard Formatting Laws

### Law 1: Deep, Relevant Indentation in Docs & Markdown (3 to 4+ Levels)

* **Question:**
  * How should we indent headings, questions, answers, and bullets in Google Docs?
* **Answer:**
  * Indent every parent-child layer by 36pt (0.5 inch per level):
    * **Level 0 (0pt - Left Margin):**
      * Document and section headings (**HEADING_1**, **HEADING_2**, **HEADING_3**).
      * Top-level metadata or summary labels on their own line (such as **Executive Snapshot:**).
    * **Level 1 (36pt - 1st Indent):**
      * Standalone **Question:** and **Answer:** labels under a heading (bold black).
      * Metadata values placed on lines beneath a Level-0 metadata label.
      * Top-level black bullet points under **Executive Snapshot:** or a header.
    * **Level 2 (72pt - 2nd Indent):**
      * The Question sentence (placed on the line below **Question:**).
      * The Answer lead sentence (placed on the line below **Answer:**).
      * Second-level sub-bullets breaking down a Level-1 bullet.
      * Standalone **Details:** label when deep technical evidence follows an Answer.
    * **Level 3 (108pt - 3rd Indent):**
      * Black bullet points inside an Answer listing causes or steps.
      * Technical content, telemetry, and tables inside a **Details:** block.
    * **Level 4 (144pt - 4th Indent):**
      * Child sub-bullets under a Level-3 Answer bullet (metrics, links, or proofs).

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

### Law 2: Single Color (Blue) for Headers - Everything Else ONLY Black

* **Question:**
  * Which colors are allowed in Google Docs and Markdown deliverables?
* **Answer:**
  * Reserve color strictly for headers and keep all body text pure black:
    * **Headers = Blue Only:**
      * Use #1155CC for **HEADING_1** and #4A86E8 for **HEADING_2** and **HEADING_3**.
      * Standard clickable links also use underlined #1155CC blue.
    * **Body Text, Bullets, Numbers & IDs = Pure Black (#000000):**
      * Keep all paragraphs, bullets, bold labels, numbers, and prices pure black (#000000).
      * Always use a clean white background (no background highlight).
      * Never use colored status words, shaded callout boxes, or grey body text.

---

### Law 3: Zero Inline Backticks Across All Channels

* **Question:**
  * Can we use inline backtick formatting in Google Chat, Gmail, Google Docs, or normal messages?
* **Answer:**
  * Never use inline backticks in prose across any channel:
    * **Strictly Banned in Prose:**
      * Do not wrap product names, filenames, paths, status tags, dates, or numbers in inline backticks.
      * Inline backticks clutter Chat and Gmail and turn bright green (#188038) in Google Docs.
    * **Use Clean Typographic Emphasis Instead:**
      * Use **Bold** or *Italics* for product names (**BigQuery**, **Agent Studio**).
      * Use **Bold** for status tags (**DONE**, **BLOCKED**, **P1**) and key terms.
      * Use **Bold** or *Italics* for filenames (**config.yaml**), paths (*spaces/AAQA...*), and metrics (**10:00 - 11:00**, *500 g*).
    * **Fenced Multi-Line Code Blocks Only:**
      * Reserve triple-backtick code blocks strictly for multi-line scripts or CLI commands.

| Element / Context | Avoid (Inline Backticks) | Use Instead (Bold / Italics) |
| :--- | :--- | :--- |
| **Product, Tool & Service Names** | Backticked BigQuery or Agent Studio | **BigQuery**, **Agent Studio** |
| **Status Words, Labels & Tags** | Backticked DONE, BLOCKED, or P1 | **DONE**, **BLOCKED**, **P1** |
| **Dates, Times, Quantities & Prices** | Backticked 10:00 - 11:00, $400k, 100% | **10:00 - 11:00**, $400k, 100% |
| **Filenames, Paths & Identifiers** | Backticked config.yaml or spaces/AAQA... | **config.yaml**, *spaces/AAQA...* |
| **General Emphasis / Key Terms** | Backticked important term | **important term** or *important term* |

---

### Law 4: Channel-Specific Section Structure (Docs Q&A vs. Email ad 1)

* **Question:**
  * How should we structure sections in Google Docs versus Gmail and Google Chat?
* **Answer:**
  * Match the structural pattern to the target channel:
    * **Google Docs & Long-Form Markdown (Question / Answer Format):**
      * Put a short Question first, followed immediately by an indented Answer.
      * **Topic Header (HEADING_3, 0pt, Blue #4A86E8):** Short numbered topic title.
      * **Question: (36pt, Bold Black):** Placed on its own standalone line.
      * **Question Sentence (72pt, Black):** One crisp question (15 to 20 words max).
      * **Answer: (36pt, Bold Black):** Placed on its own standalone line.
      * **Answer Content (72pt lead + 108pt/144pt bullets):** One short lead sentence plus black bullets.
    * **Gmail & Google Chat (Numbered ad 1) Replies & Bold Headings):**
      * Number multi-question replies in email or chat as **ad 1)**, **ad 2)**, **ad 3)**.
      * Use bold headers (**1. Architecture Sizing**) with clean bullet lists for multi-topic emails.
      * Break any sentence with 2 or more data points into a vertical bullet list.

---

### Law 5: Short ASCII Hyphens Only (-) - Never Use Em-Dashes or En-Dashes

* **Question:**
  * Which dash character is allowed across Google Docs, Markdown, Gmail, and Chat?
* **Answer:**
  * Always use the standard ASCII short hyphen (-) and never use long dashes:
    * **Strictly Banned Characters:**
      * Never use em-dashes (Unicode U+2014) or en-dashes (Unicode U+2013) in any channel.
    * **Required Replacement (ASCII Hyphen U+002D):**
      * Clause separation: *...v produkčním prostředí - zejména při škálování...*
      * Time and number ranges: *9:00 - 11:00*, *10 - 15 minut*, *Pondělí - Pátek*.

---

### Law 6: Short Sentences Only (15-20 Words Max; >20 Words Banished)

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
      * Split compound sentences (*and*, *while*, *which*) into two short sentences.
      * Convert the second half of the sentence into indented child bullets (+36pt).

---

### Law 7: Parentheses for Quick Details (Strict Max 6 Words Inside)

* **Question:**
  * How should we share micro-details like dates, IDs, or quick metrics?
* **Answer:**
  * Tuck micro-details inside parentheses (...) with at most 6 words inside:
    * **Good Examples (6 Words or Fewer):**
      * *(10M+ queries/mo)* - 2 words.
      * *(dedicated GCP in europe-west3)* - 4 words.
      * *(15 of 19 support cases)* - 5 words.
      * *(closed unresolved after 3 weeks)* - 5 words.
    * **Rule for Longer Details (Over 6 Words):**
      * Never put more than 6 words inside (...).
      * Promote any detail over 6 words to a child bullet (+36pt).

---

### Law 8: Always Check & Apply Default Google Docs Paragraph Styles

* **Question:**
  * Which Google Docs paragraph styles (**namedStyles**) must every document use?
* **Answer:**
  * Always inspect and enforce the saved Google Docs default styles:
    * **NORMAL_TEXT:**
      * Font: **Google Sans**, 10pt, weight 400, Pure Black (#000000).
      * Spacing: 100 line spacing (1.0 single), **NEVER_COLLAPSE**, 0pt above and below.
    * **HEADING_1:**
      * Font: **Google Sans**, 14pt, Bold, Blue #1155CC.
      * Spacing: 100 line spacing, **keepLinesTogether**, **keepWithNext**, **NEVER_COLLAPSE**.
    * **HEADING_2:**
      * Font: **Google Sans**, 12pt, Bold, Cornflower Blue #4A86E8.
      * Spacing: 100 line spacing, **keepLinesTogether**, **keepWithNext**, **NEVER_COLLAPSE**.
    * **HEADING_3:**
      * Font: **Google Sans**, 10pt, Bold, Cornflower Blue #4A86E8.
      * Spacing: 100 line spacing, **keepLinesTogether**, **keepWithNext**, **NEVER_COLLAPSE**.
    * **HEADING_4 to HEADING_6, TITLE, and SUBTITLE:**
      * **HEADING_4:** **Google Sans**, 12pt, #666666 (14pt above, 4pt below).
      * **HEADING_5:** **Google Sans**, 11pt, #666666 (12pt above, 4pt below).
      * **HEADING_6:** **Google Sans**, 11pt Italic, #666666 (12pt above, 4pt below).
      * **TITLE:** **Google Sans**, 26pt, Pure Black (#000000), 3pt below.
      * **SUBTITLE:** **Arial**, 15pt, #666666, 16pt below.

---

## 3. Channel Mechanics: Mandatory Gmail Draft Workflow & Signatures

* **Question:**
  * How must we materialize, address, and sign emails in Gmail?
* **Answer:**
  * Follow these non-negotiable Gmail rules whenever drafting, replying, or editing emails:
    * **Rule 1: Always Create or Update a Draft Directly in Gmail:**
      * Always run **gmail mutate create-draft** (or **update-draft**) in addition to showing the preview in chat.
      * When replying to an existing thread, locate the message ID first and include thread history:

```bash
/google/bin/releases/gemini-agents-gmail/gmail mutate create-draft \
  --message "<MESSAGE_ID>" \
  --to "<RECIPIENTS_WITHOUT_MICHAL>" \
  --cc "<CC_RECIPIENTS_WITHOUT_MICHAL>" \
  --include-history \
  --html \
  --body "<HTML_BODY_WITH_SIGNATURE>"
```

      * For new emails, look up addresses via Gmail or Contacts and create an HTML draft:

```bash
/google/bin/releases/gemini-agents-gmail/gmail mutate create-draft \
  --to "<RECIPIENT_EMAIL>" \
  --subject "<SUBJECT>" \
  --html \
  --body "<HTML_BODY_WITH_SIGNATURE>"
```

    * **Rule 2: Never Put Michal in To or Cc:**
      * Never include **michalminarik@google.com** in **--to** or **--cc** when drafting or replying.
      * Always strip **michalminarik@google.com** from recipient lists when replying to all on a thread.
    * **Rule 3: Never Send Emails Without Explicit Confirmation:**
      * Never run **gmail mutate send**, **reply**, **forward**, or **send-draft** without explicit confirmation.
    * **Rule 4: Standard Signature Blocks:**
      * Use the Full HTML Signature with photo for external or formal emails:

```html
<table style="font-size:12.8px;border:none;border-collapse:collapse;">
  <tbody>
    <tr>
      <td style="border:none;vertical-align:middle;padding:4.32pt">
        <img src="https://lh3.googleusercontent.com/pw/AP1GczME15F5qVkhLuLGVdf-a_uo9-nQmcnIgq7BF_JRhnSLpLjLgtygN-zVkzhZsUBl0O1aL5Xs9-IMtJ2IDDgYhJBU3BQ-DT82wf71-Zm_XS29l4isIVRt_GQ7JklYHBeXcFwj7_85BEVFEKKSLASMPEcF=w500-h451-s-no-gm" width="96" height="86" style="border:none" alt="Michal Minařík">
      </td>
      <td style="border:none;vertical-align:middle;padding:4.32pt">
        <p style="line-height:1.38;margin:0"><b style="font-family:Arial;color:rgb(67,67,67)">Michal Minařík</b></p>
        <p style="line-height:1.38;margin:0"><span style="font-family:Arial;color:rgb(67,67,67)">Customer Engineer I Google Cloud</span></p>
        <p style="line-height:1.38;margin:0"><span style="font-family:Arial;color:rgb(67,67,67)"><a href="mailto:michalminarik@google.com" target="_blank">michalminarik@google.com</a> | m: +420 606 665 475</span></p>
      </td>
    </tr>
  </tbody>
</table>
```

      * Use the compact text signature (or simply **Michal** / **Díky, Michal**) for fast internal emails:

```text
*Michal Minařík*
Customer Engineer I Google Cloud
michalminarik@google.com | m: +420 606 665 475
```

---

## 4. Mandatory 3-Step Execution Workflow for Docs & Markdown

* **Question:**
  * How do we verify and apply **my-formatting** on every Markdown file and Google Doc?
* **Answer:**
  * Run this 3-step pipeline before sharing any deliverable:
    * **Step 1: Lint Markdown Locally (Zero Violations Allowed):**
      * Draft using all 8 laws above and run the linter until 0 errors remain:

```bash
python3 ~/.gemini/config/skills/my-formatting/scripts/apply_my_formatting.py \
  --lint /path/to/draft.md
```

    * **Step 2: Import or Update the Google Doc:**
      * Import the lint-verified Markdown file using **gdocs mutate import-md**:

```bash
/google/bin/releases/gemini-agents-gdocs/gdocs mutate import-md /path/to/draft.md \
  --title "Document Title"
```

    * **Step 3: Enforce namedStyles, Pure Black Text & 4-Level Indentation:**
      * Run **apply_my_formatting.py --doc-id** right after import:

```bash
python3 ~/.gemini/config/skills/my-formatting/scripts/apply_my_formatting.py \
  --doc-id <DOC_ID> \
  --tab <TAB_ID> \
  --apply
```

      * Restores saved default **namedStyles** (10pt **Google Sans** and blue headers).
      * Strips #188038 green text and table colors back to pure black (#000000).
      * Indents **Question:**/**Answer:** (36pt), prose (72pt), and Answer bullets (108pt and 144pt).

---

## 5. References

* **Before & After Examples:**
  * [before_after_examples.md](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-formatting/references/before_after_examples.md)
* **Automated Linter & Google Docs Style Enforcer:**
  * [apply_my_formatting.py](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-formatting/scripts/apply_my_formatting.py)
