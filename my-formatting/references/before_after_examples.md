# my-formatting Before-and-After Examples

* **Question:**
  * How does **my-formatting** transform verbose AI output into readable documents?
* **Answer:**
  * Compare the **BAD** and **GOOD** examples below (Cymbal Corp scenario).

---

## Example 1: Executive Snapshot & Metadata Block

### BAD - Default Agent Output (Wall of Text & Backtick Splatter)

```markdown
**Prepared For:** Alex, Joe & Anne (Cloud Data Team) | **Vector Account:** `0014M00001EXAMPLE01` (`Cymbal Corp` / `cymbal.example.com`) | **Primary Instance:** `https://cymbal.cloud.looker.com` (`looker-prod-gcp-eu-west3-cymbal` dedicated single-tenant GCP)

**Executive Snapshot —** Cymbal Corp operates under an `$80M` / 3-year multi-cloud infrastructure commitment alongside `$3.88M` YTD26 net RVP on Google Cloud and a newly signed 2-year Direct Looker contract (`006Kf00000EXAMPLE1`, `$400k` ACV / `$800k` TCV, `2026-09-01` to `2028-08-31`), serving `~2,000` weekly active users (`6,387` DB users, `~3,500` enabled seats) and `~1.6M` weekly analytical queries (`10M+` monthly) across `23` Git-backed LookML projects (`363 GB` Filestore Enterprise SSD) on `8` pods × `30` vCPU / `128 GB` RAM, where rekindling alignment with Alex, Joe, and Anne (`15` of `19` support cases) centers on converting the September 1 seat-tier transition and painful support backlog into an opinionated two-track architecture engagement.
```

* **Question:**
  * Why does the **BAD** example above fail human readers?
* **Answer:**
  * It violates four core readability laws:
    * **Working-Memory Overflow:**
      * Packs 85 words into one single sentence.
    * **Christmas-Tree Visual Noise & Backtick Clutter:**
      * Uses 16 inline backticks that clutter text and turn bright green (#188038) in Google Docs.
    * **Long Em-Dash Usage:**
      * Uses an em-dash instead of a standard ASCII short hyphen (-).
    * **Flat Left-Margin Wall:**
      * Jams metadata and metrics into horizontal pipe-separated lines.

---

### GOOD - my-formatting Style (4-Level Indentation & Short Lines)

```text
Prepared For:                                           [Level 0: 0pt, Bold Black]
    Alex, Joe & Anne (Cloud Data Team)                  [Level 1: 36pt, Black]
Vector Account:                                         [Level 0: 0pt, Bold Black]
    0014M00001EXAMPLE01                                 [Level 1: 36pt, Black]
    Cymbal Corp (cymbal.example.com)                    [Level 1: 36pt, Black]
Primary Instance:                                       [Level 0: 0pt, Bold Black]
    https://cymbal.cloud.looker.com                     [Level 1: 36pt, Black]
    looker-prod-gcp-eu-west3-cymbal (dedicated GCP)     [Level 1: 36pt, Black]
    00000000-0000-0000-0000-000000000001                [Level 1: 36pt, Black]

Executive Snapshot:                                     [Level 0: 0pt, Bold Black]
    • $80M multi-cloud commitment (3-year contract)     [Level 1: 36pt, Bullet]
    • $3.88M YTD26 net RVP on Google Cloud              [Level 1: 36pt, Bullet]
    • Newly signed 2-year Direct Looker contract        [Level 1: 36pt, Bullet, Bold]
        ◦ 006Kf00000EXAMPLE1                            [Level 2: 72pt, Sub-bullet]
        ◦ $400k ACV ($800k TCV)                         [Level 2: 72pt, Sub-bullet]
        ◦ 2026-09-01 to 2028-08-31                      [Level 2: 72pt, Sub-bullet]
    • Serving ~2,000 weekly active users                [Level 1: 36pt, Bullet, Bold]
        ◦ 6,387 database users                          [Level 2: 72pt, Sub-bullet]
        ◦ ~3,500 enabled seats                          [Level 2: 72pt, Sub-bullet]
        ◦ ~1.6M weekly queries (10M+/mo)                [Level 2: 72pt, Sub-bullet]
        ◦ 23 Git LookML projects (363 GB SSD)           [Level 2: 72pt, Sub-bullet]
        ◦ 8 pods (30 vCPU / 128 GB RAM)                 [Level 2: 72pt, Sub-bullet]
    • Goal: align with Alex, Joe, and Anne on a two-track architecture plan. [Level 1: 36pt, Bullet]
```

* **Question:**
  * Why does the **GOOD** example work immediately?
* **Answer:**
  * It applies all 8 formatting laws:
    * Every line is 3 to 14 words long.
    * Every parenthesis holds 2 to 4 words (6 words max).
    * Zero inline backticks appear; all body text is pure black (#000000).
    * Child bullets (72pt) nest cleanly under bold parent bullets (36pt).

---

## Example 2: Question / Answer Block

### BAD - Default Agent Output (92-Word Sentence & Long Parenthetical)

```markdown
### Question #1 — Permissions, Role Architecture & Seat Governance

**Question:** How should Cymbal Corp restructure Looker permissions and SAML groups across `~3,500` enabled seats (`6,387` `cymbal.user` DB rows) to satisfy the September 1, 2026 tiered contract and close the SQL Runner row-security bypass?

**Answer:** From September 2021 through August 2026, Cymbal's `100%`-Developer legacy pool (`2,434` seats at `$11.875/mo`) meant granting `develop` and `use_sql_runner` via broad SAML groups carried zero license cost, leaving `~3,500` enabled accounts (`~1,500` weekly inactive) against the new Direct contract (`006Kf00000EXAMPLE1`: `450` Developer at `$37.50/mo`, `1,780` Standard at `$6.00/mo`, `710` Viewer at `$6.00/mo` = `2,940` seats); crucially, a December 2025 support ticket raised by Alex and Anne (which proved across multiple tests that `use_sql_runner` completely bypasses Explore-level country user attributes) shows that reclaiming `~1,500` dormant SAML accounts, revoking `use_sql_runner`, and deploying a Standard-tier `"CI Debugger"` role with Joe resolves both license compliance and multi-country security.
```

---

### GOOD - my-formatting Style (Question First & Short Sentences)

```text
### #1 Permissions, Role Architecture & Seat Governance     [Level 0: 0pt, H3 Blue #4A86E8]

    Question:                                               [Level 1: 36pt, Bold Black]
        How should Cymbal align 3,500 enabled seats with its new contract and fix SQL Runner security? [Level 2: 72pt, 16 words]

    Answer:                                                 [Level 1: 36pt, Bold Black]
        Under the legacy pool, broad SAML groups gave everyone Developer rights (2,434 seats). [Level 2: 72pt, 13 words]
        This left 3,500 enabled accounts (1,500 inactive) against the new 2,940-seat Direct contract: [Level 2: 72pt, 13 words]
            • 450 Developer seats ($37.50/mo)               [Level 3: 108pt, Bullet]
            • 1,780 Standard seats ($6.00/mo)               [Level 3: 108pt, Bullet]
            • 710 Viewer seats ($6.00/mo)                   [Level 3: 108pt, Bullet]
        SQL Runner also bypasses country security filters and consumes a Developer seat (case #123456). [Level 2: 72pt, 14 words]
        Alex, Joe, and Anne can fix compliance and security in three steps: [Level 2: 72pt, 12 words]
            • Remove 1,500 dormant SAML accounts (60-90d inactive) [Level 3: 108pt, Bullet]
            • Revoke use_sql_runner from general analyst roles [Level 3: 108pt, Bullet]
            • Add a Standard "CI Debugger" role (see_lookml only) [Level 3: 108pt, Bullet]
```

* **Question:**
  * How is the visual hierarchy structured in Example 2?
* **Answer:**
  * Each layer steps right by 36pt:
    * **Level 0 (0pt):** Blue H3 header (#4A86E8, 10pt Bold **Google Sans**).
    * **Level 1 (36pt):** Standalone **Question:** and **Answer:** labels in bold black.
    * **Level 2 (72pt):** Short Question and Answer sentences (9 to 16 words each).
    * **Level 3 (108pt):** Vertical black bullet points for contract tiers and action steps.
