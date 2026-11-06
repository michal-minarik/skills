# Real Sent Email Samples by Category (Anonymized)

* **Question:**
  * How does **my-voice** look across real Czech and English emails?
* **Answer:**
  * Review the four quadrants below (External/Internal x Czech/English).

---

## 1. External Czech (Zákazníci a partneři)

### Example 1: Multi-Point Technical Troubleshooting (ad 1 / ad 2 / ad 3)
```text
Dobry den,

ad 1) Muzete prosim mrknout ted, jestli tam to nastaveni porad nemate?

ad 2) Ano, odebrani roles/businessaicode.user zamezi pouzivani Antigravity pres GE licence.

ad 3) Ano, odebrani roles/agentplatform.user zamezi volani a konzumaci tokenu pres Agent Platformu.

Per user controls (kvoty, zapnuto/vypnuto...) primo v nastaveni GE developer settings jsou aktualne vedeny jako priority P0 feature, ktera je planovana na zari.

S pozdravem.

*Michal Minařík*
Customer Engineer I Google Cloud
michalminarik@google.com | m: +420 606 665 475
```

### Example 2: Proactive Prerequisite & Trial Credit Check
```text
Dobry den,

dekuji za update. Jeste nez zapnu recommendations engine, muzete pro me proverit, ze mate pripsane trial kredity pro Recommendation API, ja na to nemam opravneni:

*Steps to Check Your Credits:*
- Log in to the Google Cloud Console.
- Click the Navigation Menu (the three horizontal lines in the top-left corner).
- Scroll down and select Billing.
- If you have multiple billing accounts, choose the one associated with the project where you enabled the Recommendations AI / Retail API.
- In the left-hand navigation menu of the Billing page, click on Credits.

*What to Look For:*
- On the Credits page, you will see a table listing all active and expired credits.
- Look for a credit with an original amount of $600 and a description typically mentioning "Recommendations AI", "Retail API", or "Trial Credit".
- The table will also show you the Remaining Amount, Effective Date, and Expiration Date (credits typically expire after 6 months).

Ptam se na to, protoze pri zapnuti Recommendations se trenuje model specificky pro vase data. Tento trenink stoji penize (per hour), normalne je toto pokryto $600 kredity, ktere dostavate pripsane automaticky na prvnim GCP projektu, kde to zkousite. Mohlo se stat, ze uz byste treba v ramci organizace nekdy tyto kredity uplatnili a nemeli bychom je k dispozici (pripadne mohly expirovat...), chci predejit tomuto prekvapeni.

Dekuji za informaci.

*Michal Minařík*
Customer Engineer I Google Cloud
michalminarik@google.com | m: +420 606 665 475
```

### Example 3: Migration Roadmap to Gemini Enterprise Agent Platform
```text
Dobrý den,

navazuji na naši předchozí komunikaci ohledně přechodu vašich aplikací a promptů z Google AI Studio do podnikového prostředí Google Cloud Platform (Gemini Enterprise Agent Platform / Agent Studio).

Níže posílám souhrnný přehled postupu migrace, včetně vyjasnění technických možností ohledně přenosu historie verzí.

*Jak je to s historií verzí?*
Bohužel přímý automatický import kompletní historie verzí z Google AI Studio do Agent Studia není podporován. Do nového prostředí se standardně importuje aktuální stav definice promptu/aplikace.

Doporučené řešení pro zachování starších verzí:
- Záloha z Google Disku: Vaše prompty z Google AI Studio jsou uloženy na vašem Google Disku (ve složce AI_Studio), kde Google Drive uchovává historii revizí souborů. Odtud si můžete v případě potřeby stáhnout i starší verze.
- Verzování v Git: Do budoucna doporučujeme začlenit správu a verzování promptů do vašeho standardního Git repozitáře v rámci CI/CD pipeline, což je pro produkční nasazení osvědčená enterprise praktika.

*Krok za krokem: Postup migrace*
Krok 1: Export a příprava promptů
Krok 2: Import do Agent Studia na GCP
Krok 3: Úprava kódu a autentizace v aplikaci

Oficiální dokumentace Google Cloud: Migrate from Google AI Studio to Gemini Enterprise Agent Platform
https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate/migrate-google-ai

S pozdravem.

*Michal Minařík*
Customer Engineer I Google Cloud
michalminarik@google.com | m: +420 606 665 475
```

---

## 2. External English (International Teams & Partners)

### Example: Structured Information Gathering for Architecture Sizing
```text
Hi team,

Thank you for your time during our meeting yesterday. Following up on our conversation, we already have the details needed for the MySQL and PostgreSQL environments. To complete the Azure to GCP architecture mapping and sizing for the remaining components, could you please provide the following details?

*1. MSSQL Server Requirements*
- Database Edition & Version (e.g., Enterprise, Standard, Express)
- Machine / Instance Type (e.g., Azure VM size or managed instance tier)
- vCPU Count
- RAM (GB)
- Storage Capacity (GB/TB)
- High Availability (HA) & Disaster Recovery (DR) Configurations (e.g., Availability Zones, Always On, Read Replicas)
- Backup Size (feel free to share an estimate if readily available)

*2. Cosmos DB Requirements*
To help us select the optimal GCP target service (e.g., Firestore, Bigtable, or Managed Cassandra), please let us know:
- API / Endpoint Type (e.g., Core/NoSQL, MongoDB API, Cassandra API)
- Provisioned Throughput (RU/s) or Autoscale limits
- Storage Size (GB)

Once we have these final inputs, we will finalize the GCP target topology and cost estimates for review.

Please let me know if you have any questions or need clarification on any of the points above.

Best regards,

*Michal Minařík*
Customer Engineer I Google Cloud
michalminarik@google.com | m: +420 606 665 475
```

---

## 3. Internal Czech (Google Colleagues)

### Example 1: Technical Review & Delegation
```text
Cau,

myslim, ze je nespravna vstupni uvaha, ze je to non-stop 600k zprav za sekundu a chtelo by to zpresnit. Navrhuju do toho prizvat @Alex , treba ho k tomu neco napadne a zaroven jim bude schopen dorucit deep dive na securitu.

*Michal Minařík*
Customer Engineer I Google Cloud
michalminarik@google.com | m: +420 606 665 475
```

### Example 2: Event Attendance Coordination
```text
Ahoj,

ja bych se ucasti nebranil, ale 24. 9. 2026 jsem na konferenci AI Horizons pro public, takze se nemuzu schuzky zucastnit.

*Michal Minařík*
Customer Engineer I Google Cloud
michalminarik@google.com | m: +420 606 665 475
```

---

## 4. Internal English (Google Colleagues)

### Example: Quick Status / Coordination
```text
Hi Alex, Anne,

Thanks for sharing this proposal. The Now Assist for ITOM Agent integration between ServiceNow and Google Cloud Observability sounds like a very relevant and interesting use case for Cymbal Corp and a potential hackathon topic.

Let's align on next steps and how we want to position it for the team.

Best regards,
Michal
```
