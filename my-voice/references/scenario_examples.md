# my-voice Scenario Examples (Before vs. After)

* **Question:**
  * How does the Two-Layer **my-voice** framework transform generic AI prose across scenarios?
* **Answer:**
  * Compare the **BAD** and **GOOD** examples below (using generic Cymbal scenarios).

---

## Scenario 1: Executive & Board Advisory

* **Scenario Dials:**
  * **Context:** Commercial & Organizational
  * **Role:** Mode 1 (Advisory & Strategy)
  * **Recipient:** Large Group (Board / CxO)
  * **Exposure:** External Team (English)
  * **Channel:** Doc / Brief

### BAD - Generic AI (Contrastive Slop, "Customer", Passive)
```text
This initiative is not about replacing analysts; rather, it is a testament to how our customers can leverage Vertex AI to remediate data bottlenecks over the next 6 to 12 months. When we work with customers, they often ask whether they should wait for more mature models before starting their transformation journey.
```

### GOOD - my-voice + my-formatting (Velvet Glove, Socratic, "Teams", Short Hyphens)
```text
### #1 Accelerating From 12-Month Roadmaps to 48-Hour Prototypes

    Question:
        What happens when an AI project takes longer to launch than the model inside it?

    Answer:
        Frontier models refresh every 3 to 4 months, while traditional IT projects take 12 months.
        We see similar teams close this gap by shifting from static specs to 48-hour prototypes:
            • Give product owners direct access to governed Agent Studio sandbox tools today
            • Test clickable prototypes with a 200-user cohort this week
            • Promote only validated winners into core engineering sprints
        Of course we could keep running a 6-month specification cycle first - and what happens when three model generations pass before a single user sees the feature?
        We can build the first working prototype with the product team today.
```

---

## Scenario 2: Technical Architecture & Sizing Advisory

* **Scenario Dials:**
  * **Context:** Technical & Commercial
  * **Role:** Mode 2 (Architecture & Builder)
  * **Recipient:** Small Group
  * **Exposure:** External Team (English)
  * **Channel:** Email

### BAD - Generic AI (Unopinionated Menu, Hype, Unsolicited Call Offer)
```text
Dear Cymbal Team,

I hope this email finds you well! As a customer, you have several options for Provisioned Throughput on Vertex AI. Depending on your requirements, I would be thrilled to help you evaluate whether to size for 100% of peak traffic or use Pay-As-You-Go. Let's hop on a quick call next week at your earliest convenience!

Kind regards,
Michal
```

### GOOD - my-voice (Opinionated, Calm, Async-First, Best regards)
```text
Hi Anne, team,

Reaching production readiness on Gemini Enterprise Agent Platform is a major milestone for our teams.

Here is how we recommend setting up capacity today:

ad 1) Model choice: Flash-Lite is the most efficient fit here. We can commit to the current Lite tier now and upgrade to the next generation as soon as it lands.

ad 2) Sizing: I am opinionated here and recommend against sizing Provisioned Throughput for 100% peak traffic. Target 80% to cover our steady baseline and let volatile spikes spill over to PayGo.

ad 3) Catalog integration: BigQuery supports reading external catalogs via Lakehouse Omni. However, we have three critical items to verify today: read/write compatibility, lineage, and row-level security.

We can run the sizing script against the live telemetry today as soon as you share the export.

Best regards,
```

---

## Scenario 3: Multi-Workstream Execution & Task Delegation

* **Scenario Dials:**
  * **Context:** Operational & Governance
  * **Role:** Mode 3 (Execution & Control)
  * **Recipient:** Small Group
  * **Exposure:** External or Internal
  * **Channel:** Email + Doc Handoff

### BAD - Generic AI (Vague Ownership, Passive Close)
```text
Hi everyone,

Following our meeting, I have summarized the discussion notes. There are still some security items and product testing tasks that the customer needs to complete over the next quarter. Hopefully we can align on responsibilities soon.
```

### GOOD - my-voice (3-Layer OKR Roadmap & Task Delegation)
```text
Hi team,

Thank you for the productive working sessions this week. To keep our momentum high and ship our first agent on Agent Runtime before year-end, we structured our execution roadmap into two parallel tracks across three layers:
- Strategic Goals (measured via KPIs)
- Tactical Stories (prioritized via MoSCoW)
- Operational Tasks (assigned via SMART owners and dates)

Immediate actions for this week:
- Governance track: @Alex runs the baseline GCP security review today, and @Joe maps the four priority policy areas by Thursday to unlock the Landing Zone.
- Product track: @Anne spins up the synthetic BigQuery sandbox tomorrow so the product pod can validate the first 48-hour prototype with our 200-user cohort next week.

One quick note on how we built this draft: we used our AI agents to synthesize our meeting notes and threads, and our team reviewed and refined the plan. If you spot anything that needs adjustment, flag it in the doc and we will update it on the spot.

Best regards,
```

---

## Scenario 4: External Technical Diagnosis & Support Ticket Follow-Up

* **Scenario Dials:**
  * **Context:** Technical & Operational
  * **Role:** Mode 2 & 5 (Architecture & Enablement)
  * **Recipient:** Small Group
  * **Exposure:** External Team (English)
  * **Channel:** Email

### BAD - Generic AI (Possessive Labels, Free Deadlines, Internal Plumbing)
```text
Hi Anne,

Thank you so much for reaching out! We are very excited to help your engineers get to the bottom of this issue as quickly as possible.

Joe and I will loop in our Lakehouse engineering team by the end of today to check how our EU engine signs the cross-cloud requests. We have already added our internal technical notes directly to the ticket so the assigned Support engineer can pull the backend S3 trace right away.

Looking at the details you included in the ticket, two data points stand out:
1. Your developers configured the catalog without a KMS ARN.
2. The query failed after 6.5 seconds.
```

### GOOD - my-voice (Zero Fluff, Boundary Hygiene, Best regards)
```text
Hi Anne,

Thank you for opening case 77267929 and for the follow-up.

I have already added internal technical notes to the ticket to expedite the diagnostic process. We will also review internally how the EU engine signs cross-cloud requests under this IAM setup.

Reading the details, two things stand out:
ad 1) The 6.5-second runtime proves catalog discovery works, while the data-plane Parquet read fails.
ad 2) Omitting the KMS key ARN breaks reads whenever the bucket uses default KMS encryption.

Best regards,
```
