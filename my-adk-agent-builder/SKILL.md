---
name: my-adk-agent-builder
description: >-
  ❤️ End-to-end blueprint and environment conventions for creating, testing, securing,
  documenting, and deploying ADK agents (`ag-adk-*`) in Michal's CloudTop and
  Google Cloud environment. Use whenever creating a new `ag-adk-*` project,
  migrating or anonymizing a customer demo to ACME Corp, preparing an ADK repo
  for GitHub (`cloud-gtm`), fixing CloudTop/Cloud Build `uv` or RAPT issues, or
  deploying to Gemini Enterprise Agent Platform (`europe-west3`).
metadata:
  icon: ❤️
---

# ❤️ My ADK Agent Builder Skill (my-adk-agent-builder)

Use this skill alongside the `google-agents-cli-*` skills whenever creating, refactoring, testing, deploying, or preparing an `ag-adk-*` agent repository in Michal's environment.

---

## 1. Naming, Branding & Terminology Guardrails (Non-Negotiable)

1. **Repository & Folder Naming**:
   - Prefix all ADK agent project directories and GitHub repositories (`cloud-gtm` org) with `ag-adk-<use-case>` (e.g., `ag-adk-doc-translation`, `ag-adk-finance-report`, `ag-adk-fraud-detection`, `ag-adk-it-helpdesk`, `ag-adk-travel-policy`).
2. **Enterprise Customer Anonymization (`ACME Corp`)**:
   - Always anonymize customer demos, sample datasets, BigQuery tables (`acme_*_demo`), Asana projects (`ACME - Tasks`), and personas to **ACME Corporation** (`ACME`, `acme.com` / `acmecorp.com`).
   - **NEVER** include real customer names (e.g., FTMO) in code, fixtures, commit messages, or documentation.
3. **Platform Terminology**:
   - **NEVER** use the phrase `"Vertex AI"` in user-facing documentation (`README.md`, `GEMINI.md`, `RUNBOOK.md`), comments, or UI descriptions.
   - **ALWAYS** use **"Gemini Enterprise Agent Platform"** for the platform and **"Agent Runtime"** for the serverless execution environment.
4. **Sanitization & Secret Hygiene**:
   - Never commit `.env`, `deployment_metadata.json`, `deployment/tofu/terraform.tfvars`, `deployment/tofu/backend.hcl`, real GCP Project IDs (such as `nodal-bison-485713-h2`), project numbers, GCS bucket names, or webhook URLs/tokens to Git-tracked documentation or config files. Use placeholders (`<your-project-id>`, `<your-bucket-name>`) in `.env.example`, `deployment/tofu/terraform.tfvars.example`, `README.md`, and `GEMINI.md`.

---

## 2. Project Scaffolding & Manifest Invariants

1. **Scaffold with `agents-cli`**:
   - Target `agent_runtime` in region **`europe-west3`** with `GEMINI.md` as the agent guidance file.
   - Standard `agents-cli-manifest.yaml` layout:
     ```yaml
     name: 'ag-adk-<use-case>'
     acli_version: '1.6.1'
     agent_directory: 'app'
     region: 'europe-west3'
     base_template: 'adk'
     language: 'python'
     create_params:
       root_agent_name: 'ag_adk_<use_case>'
       deployment_target: 'agent_runtime'
       session_type: 'in_memory'
       cicd_runner: 'skip'
       is_a2a: true
       agent_gateway: False
       agent_guidance_filename: 'GEMINI.md'
     ```
2. **Agent & App Name Synchronization Invariant**:
   - `root_agent.name` in `app/agent.py` (underscored, e.g., `ag_adk_doc_translation`) **MUST** match `create_params.root_agent_name` in `agents-cli-manifest.yaml`.
   - `app = App(root_agent=root_agent, name="app")` **MUST** keep `name="app"` (matching `agent_directory: 'app'`). Changing either breaks `agents-cli eval` trace correlation and session lookups.

---

## 3. Model Selection & Dual-Region Endpoint Bridging (`global` vs `europe-west3`)

- **Default Model**: `gemini-3.8-flash` (or `gemini-flash-latest`) with `retry_options=types.HttpRetryOptions(attempts=3)`. **Never** downgrade or change the model unless explicitly asked.
- **Why Bridging Is Required**:
  - At runtime, Agent Runtime (`europe-west3`) injects `GOOGLE_CLOUD_LOCATION=europe-west3` into the container.
  - However, `gemini-3.8-flash` and `gemini-flash-latest` are served on the `global` endpoint (regional endpoints return `404 Not Found`), while `VertexAiSessionService` and BigQuery require `europe-west3`.

### Pattern A: Environment Variable Preservation (Standard `app/agent.py` Header)
Place this at the top of `app/agent.py` before initializing the model or services:
```python
# Preserve runtime region for VertexAiSessionService before pinning Gemini model location to global
if (
    os.environ.get("GOOGLE_CLOUD_LOCATION")
    and os.environ.get("GOOGLE_CLOUD_LOCATION") != "global"
):
    os.environ.setdefault(
        "GOOGLE_CLOUD_AGENT_ENGINE_LOCATION",
        os.environ["GOOGLE_CLOUD_LOCATION"],
    )
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")
```

### Pattern B: `GlobalGemini` / `ResilientGemini` Model Subclass
When coexisting with regional clients or requiring automatic fallback to `gemini-2.5-flash`:
```python
from functools import cached_property
from google.adk.models import Gemini
from google.genai import Client, types


class GlobalGemini(Gemini):
    """Routes Gemini model inference to location='global' while preserving regional runtime env."""

    @cached_property
    def api_client(self) -> Client:
        return Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location="global",
            http_options=types.HttpOptions(
                headers=self._tracking_headers(),
                retry_options=self.retry_options,
            ),
        )
```

---

## 4. CloudTop Workstation & Cloud Build Specifics

1. **`uv` Public PyPI Configuration (`~/.config/uv/uv.toml`)**:
   - On Google CloudTop workstations, internal proxy settings can inject `http://airlock-proxy.uplink.goog:999/...` into `uv.lock` or cause HTTP 403 errors.
   - Ensure `~/.config/uv/uv.toml` contains:
     ```toml
     [[index]]
     name = "pypi"
     url = "https://pypi.org/simple"
     default = true
     ```
   - Before committing `uv.lock`, verify that `grep -c "airlock-proxy" uv.lock` is `0`.
2. **Cloud Build-Safe `Dockerfile`**:
   - Remote GCP Cloud Build workers cannot reach internal `airlock-proxy.uplink.goog` hosts.
   - In `Dockerfile`, **do NOT copy `uv.lock` or use `--frozen`**. Instead, resolve directly during build:
     ```dockerfile
     FROM python:3.12-slim
     COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /uvx /bin/
     WORKDIR /code
     COPY ./pyproject.toml ./README.md ./
     COPY ./app ./app
     RUN uv sync --no-dev
     EXPOSE 8080
     CMD ["uv", "run", "--no-sync", "uvicorn", "app.fast_api_app:app", "--host", "0.0.0.0", "--port", "8080"]
     ```
3. **Secrets & CloudTop RAPT Reauthentication**:
   - Store local tokens and credentials in `pass` (`~/.password-store/`) or GCP Secret Manager.
   - If `gcloud` or `google.auth.default()` raises `Reauthentication is needed (RAPT)` on CloudTop, refresh the `rapt_token` in `~/.config/gcloud/application_default_credentials.json` via `google.oauth2.reauth.get_rapt_token` using `pass show argolis/admin` (or run `gcloud auth application-default login`).

---

## 5. Agent Architecture, Tools & Hermetic Testing Patterns

1. **Deterministic Tool Execution (Zero LLM Arithmetic)**:
   - Perform all financial math, SQL aggregations, statutory rate lookups, and binary PDF operations deterministically in Python/SQL tools.
   - When generating executive prose over financial numbers, enforce a **SQL numeric whitelist** check (`tokens ⊆ whitelist`) so the LLM cannot hallucinate or round figures.
2. **Hermetic Offline Snapshot Fallbacks**:
   - Every external tool (BigQuery, Asana, Sentry) should include a graceful `try/except` fallback to deterministic snapshot constants (`SNAPSHOT_*`) or local JSON fixtures (`app/fixtures/*.json`) when cloud credentials are absent, ensuring unit tests and demos never crash offline.
3. **BigQuery Best Practices**:
   - Always use parameterized queries (`bigquery.ScalarQueryParameter`).
   - Never use streaming inserts (`insert_rows_json`) on demo tables that require subsequent `UPDATE` or `DELETE` statements (streaming creates a 90-minute buffer lock). Use SQL DML (`INSERT INTO ...`, `UPDATE ...`) or batch load jobs (`load_table_from_json`).
4. **Asana Comment Formatting (when integrating with Asana)**:
   - Asana `html_text` requires strict XML wrapped in `<body>...</body>`.
   - Allowed tags: `<strong>`, `<em>`, `<u>`, `<s>`, `<code>`, `<pre>`, `<ul>`, `<ol>`, `<li>`, `<blockquote>`, `<a href="...">`.
   - **Forbidden tags**: `<p>`, `<br>`, `<div>`, `<h1>`–`<h6>`, `<table>`. No whitespace is allowed between `<ul>`/`<ol>` and `<li>`.
   - Implement a 3-layer idempotency guard on webhook/polling listeners (in-flight lock set, tag inspection, and comment signature check) to prevent infinite loops.
5. **Agent Registry MCP & 3LO Auth (when integrating MCP servers)**:
   - Discover MCP servers via `AgentRegistry(project_id, location="europe-west3").get_mcp_toolset(...)`.
   - Use a 3-stage `AgentIdentityOAuthProvider(GcpAuthProvider)`:
     1. Check Gemini Enterprise injected 3LO token in `context.state["temp:<AUTH_ID>"]`.
     2. Delegate to native `GcpAuthProvider` (`Agent Identity Credentials Service`).
     3. Fall back to exchanging an OAuth refresh token from Secret Manager / local `pass` for headless execution.
6. **Offline Test Harness (`tests/conftest.py`)**:
   - In `pytest_configure` (or an `autouse=True` fixture), mock `google.auth.default = lambda *a, **kw: (MagicMock(), "test-project")`, `AgentRegistry.__init__`, `AgentRegistry.list_mcp_servers`, `AgentRegistry.get_mcp_toolset`, and `Gemini.generate_content_async` unless `LIVE_API_TEST=true`. This ensures `pytest` collection succeeds on GitHub Actions runners where no Application Default Credentials (ADC) are present.
   - Include an `autouse=True` teardown fixture that resets `root_agent.model.api_client._api_client._aiohttp_session = None` to prevent `pytest-asyncio` event loop mismatch errors.

---

## 6. Dependency Hygiene & Zero-CVE Lockfile Rules

When configuring `pyproject.toml` and `uv.lock` for GitHub (`cloud-gtm`):

1. **Avoid Vulnerable `nltk` via Evaluation Extras**:
   - Do **NOT** leave `google-adk[eval]` or `google-cloud-aiplatform[evaluation]` in locked dependencies once pushed to GitHub unless actively running local evaluations, because they pull in `nltk` (which triggers unpatched Dependabot CVE alerts).
2. **Minimum Security Version Floors**:
   - Ensure `uv.lock` resolves patched versions of common transitive dependencies:
     - `protobuf>=6.31.1,<7.0.0`
     - `pyjwt>=2.14.0`
     - `cryptography>=50.0.0`
     - `oauthlib>=4.0.0`
     - `anyio>=4.14.2`
     - `aiohttp>=3.13.4`
     - `pypdf>=6.16.1`
3. **Codespell & Ruff Configuration**:
   - In `[tool.codespell]`, always include `./artifacts/*` in `skip`:
     ```toml
     [tool.codespell]
     ignore-words-list = "rouge"
     skip = "./locust_env/*,uv.lock,.venv,./frontend,**/package-lock.json,./artifacts/*"
     ```
   - Verify quality before committing:
     ```bash
     agents-cli lint
     uv run pytest tests/unit tests/integration
     ```

---

## 7. GitHub Repository Hygiene & Documentation Triad

Every `ag-adk-*` repository pushed to `github.com/cloud-gtm/ag-adk-*` must include:

### A. `.gitignore` Essentials
Ensure the following are ignored (and untracked via `git rm --cached` if previously added):
```gitignore
.env
!.env.example
.venv/
.adk/
.google-agents-cli/
deployment_metadata.json
deployment/tofu/.terraform/
deployment/tofu/*.tfstate*
deployment/tofu/terraform.tfvars
deployment/tofu/*.auto.tfvars
deployment/tofu/backend.hcl
artifacts/
.ruff_cache/
*.pem
*-key.json
credentials*.json
```

### B. Standard GitHub Guardrails (`.github/`)
1. **`.github/workflows/cicd.yml`**:
   - Delete any placeholder `.github/workflows/ci.yml` and use the full CI/CD pipeline defined in **Section 8** (template available in `~/.gemini/config/skills/my-adk-agent-builder/templates/cicd.yml`).
2. **`.github/dependabot.yml`**:
   ```yaml
   version: 2
   updates:
     - package-ecosystem: "github-actions"
       directory: "/"
       schedule:
         interval: "weekly"
       open-pull-requests-limit: 3
       cooldown:
         default-days: 7
       groups:
         dependencies:
           patterns:
             - "*"
   ```

### C. The Documentation Triad
1. **`README.md` (Human & Presenter Guide)**:
   - Executive Summary & Problem Statement (`ACME Corp` context).
   - Architecture Diagram (ASCII/Mermaid) & Component Responsibility Matrix.
   - Multi-Act Customer Demo Script / Preset Scenarios with copy-paste prompts.
   - Quick Start (`uv sync`, `.env.example`, BigQuery seeder if applicable, `agents-cli playground`, `agents-cli run`).
   - Testing & Linting (`uv run pytest`, `agents-cli lint`).
   - CI/CD Pipeline & OpenTofu Setup + Revision Inspection/Rollback commands (with sanitized `<your-project-id>` placeholders).
2. **`GEMINI.md` (AI Coding Agent Guide)**:
   - System Architecture & Tech Stack table.
   - Directory & Codebase Component Map.
   - Critical Architectural Invariants (e.g., `global` endpoint routing, `root_agent.name` sync, zero LLM arithmetic, hermetic snapshots).
   - Data Models / BigQuery Schemas / Tool specifications.
   - Step-by-Step Extension Guide (how to add a new tool, scenario, or policy rule).
   - Development, Evaluation, and Deployment commands + Troubleshooting table.
   - Non-Negotiable Operational Commandments for Coding Agents.
3. **`RUNBOOK.md` (For Live Customer Workshops/Demos)**:
   - Presenter script structured into sequential Acts (Happy Path, Edge Cases, Guardrail/Fault Injection, Governance/Reset) with exact prompts, expected tool calls, and talking points.

---

## 8. Standard Single-Environment CI/CD Pipeline (OpenTofu + GitHub Actions WIF + Runtime Revisions)

All `ag-adk-*` agents must be deployed through the standardized single-environment **OpenTofu + GitHub Actions WIF** pipeline rather than manual deployments or default `agents-cli` multi-environment Terraform (`deployment/terraform/` must be removed if present). Reference templates are stored in `~/.gemini/config/skills/my-adk-agent-builder/templates/`.

### A. OpenTofu Infrastructure (`deployment/tofu/`)
1. **State Backend (`backend.hcl`, gitignored)**:
   - Store state in GCS bucket `gs://<project-id>-tfstate` (`europe-west3`, versioning enabled) with `prefix = "ag-adk-<use-case>"`.
2. **Workload Identity Federation (`wif.tf`)**:
   - Uses the shared project-level Workload Identity Pool `github-actions-pool` and OIDC Provider `github-oidc` conditioned on `attribute.repository_owner == 'cloud-gtm'` (`var.create_wif_pool = false` when the pool already exists in the project so it is referenced via `data` source, or `true` when bootstrapping a new project).
   - Creates a dedicated per-agent CI/CD Service Account (`ag-adk-<short-name>-cicd@<project-id>.iam.gserviceaccount.com`) with required roles (`roles/aiplatform.admin`, `roles/agentregistry.admin`, `roles/discoveryengine.admin`, `roles/secretmanager.secretAccessor`, `roles/secretmanager.viewer`, `roles/storage.admin`, `roles/cloudbuild.builds.editor`, `roles/artifactregistry.writer`, `roles/iam.serviceAccountUser`, `roles/resourcemanager.projectIamAdmin`, `roles/serviceusage.serviceUsageConsumer`, `roles/logging.viewer`).
   - Scopes `roles/iam.workloadIdentityUser` and `roles/iam.serviceAccountTokenCreator` strictly to `principalSet://iam.googleapis.com/projects/<project-number>/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/cloud-gtm/ag-adk-<use-case>`.
3. **GitHub Actions Secrets & Variables (`github.tf`)**:
   - Uses `integrations/github` (`owner = "cloud-gtm"`) to populate repository secrets (`WIF_PROVIDER`, `GCP_SERVICE_ACCOUNT`) and variables (`GCP_PROJECT_ID`, `GCP_PROJECT_NUMBER`, `GCP_REGION`, `AGENT_NAME`, `AGENT_DISPLAY_NAME`, `GEMINI_ENTERPRISE_APP_ID`, plus agent-specific config variables).
4. **Running OpenTofu on CloudTop**:
   - Go's `oauth2/google` client does not read `rapt_token` from `application_default_credentials.json`. Mint an access token via Python before running `tofu`:
     ```bash
     export GOOGLE_OAUTH_ACCESS_TOKEN="$(uv run python -c 'import google.auth, google.auth.transport.requests; c, _ = google.auth.default(); c.refresh(google.auth.transport.requests.Request()); print(c.token)')"
     export GITHUB_TOKEN="$(pass show tokens/github/pat | head -n 1)"
     tofu -chdir=deployment/tofu init -backend-config=backend.hcl
     tofu -chdir=deployment/tofu apply
     ```

### B. Agent Runtime Revision Manager (`deployment/manage_revisions.py`)
Include `deployment/manage_revisions.py` (template at `~/.gemini/config/skills/my-adk-agent-builder/templates/manage_revisions.py`) in every repository to manage the full lifecycle of Agent Runtime `runtimeRevisions` and Agent Identity bindings:
1. **`prepare-identity` (runs BEFORE `agents-cli deploy`)**:
   - Finds or creates the ReasoningEngine shell (`displayName = AGENT_NAME`, `spec.identityType = "AGENT_IDENTITY"`).
   - Grants required IAM roles (`roles/aiplatform.user`, `roles/secretmanager.secretAccessor`, `roles/agentregistry.viewer`, `roles/serviceusage.serviceUsageConsumer`, `roles/cloudapiregistry.viewer`, `roles/logging.logWriter`, `roles/monitoring.metricWriter`) to `principal://<effectiveIdentity>` and waits 15s if bindings changed so container startup can mount Secret Manager secrets and query Agent Registry on first deploy.
   - If the agent uses an Agent Registry 3LO OAuth Binding, binds `source.identifier` to `urn:agent:projects-<project-number>:projects:<project-number>:locations:europe-west3:aiplatform:reasoningEngines:<engine-id>`. Because `source` is immutable on Agent Registry Bindings, if `source.identifier` changed, delete the old binding (awaiting LRO) and recreate it (`POST`), or no-op if already matching.
2. **`verify-and-promote` (runs AFTER `agents-cli deploy`)**:
   - Writes `deployment_metadata.json` for downstream `agents-cli publish`.
   - Discovers the newest `runtimeRevision` (`projects/.../reasoningEngines/<id>/runtimeRevisions/<rev_id>`), verifies `state == "ACTIVE"`, and smoke-tests it via `:streamQuery`.
   - Shifts **100% of live traffic** to the new revision using `trafficConfig.trafficSplitManual` while retaining previous revisions for rollback.
3. **`rollback` & `list`**:
   - `rollback --revision-id <previous|ID>` shifts 100% of live traffic back to the prior or specified revision via `trafficSplitManual` without rebuilding.
   - `list` prints the active `trafficConfig` and all `runtimeRevisions`.

### C. GitHub Actions Workflow (`.github/workflows/cicd.yml`) & `cloud-gtm` Compliance
1. **`zizmor` Security Scanner Requirements (Mandatory in `cloud-gtm`)**:
   - Always set top-level `permissions: contents: read` and explicit job-level `permissions:`.
   - Pin **every** `uses:` action to its full 40-character commit SHA (with `# vX` comment) and pass `persist-credentials: false` to `actions/checkout`:
     - `actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4`
     - `actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5`
     - `astral-sh/setup-uv@d4b2f3b6ecc6e67c4457f6d3e41ec42d3d0fcb86 # v5`
     - `opentofu/setup-opentofu@592200bd4b9bbf4772ace78f887668b1aee8f716 # v1.0.5`
     - `google-github-actions/auth@c200f3691d83b41bf9bbd8638997a462592937ed # v2`
   - **Never** interpolate `${{ vars.* }}`, `${{ inputs.* }}`, or `${{ github.sha }}` directly inside `run:` scripts; bind them in `env:` and reference `$VAR_NAME` in bash.
   - Verify locally before pushing: `uvx zizmor .github/workflows/cicd.yml`.
2. **Workflow Structure**:
   - **`test` job** (on `pull_request` and `push` to `main`): Runs `ruff check .`, `codespell`, hermetic `pytest`, `tofu fmt -check`, and `tofu validate`.
   - **`deploy` job** (on `push` to `main` or `workflow_dispatch` with `action=deploy`): WIF auth -> `manage_revisions.py prepare-identity` -> `uvx google-agents-cli==1.6.1 deploy --agent-identity ...` -> `manage_revisions.py verify-and-promote` -> `uvx google-agents-cli==1.6.1 publish gemini-enterprise ...` -> `manage_revisions.py list`.
   - **`rollback` job** (on `workflow_dispatch` with `action=rollback`): WIF auth -> `manage_revisions.py rollback --revision-id "${TARGET_REVISION_ID}"` -> `manage_revisions.py list`.
3. **Pushing Workflows & Merging to `main` on `cloud-gtm`**:
   - If `tokens/github/pat` lacks `workflow` OAuth scope, register `~/.ssh/id_ed25519.pub` as a write-enabled repository deploy key (`POST /repos/cloud-gtm/<repo>/keys`) and set `origin` to `ssh://github.com/cloud-gtm/<repo>.git` (which uses `Host github.com` in `~/.ssh/config` without triggering the `git@github.com:` HTTPS rewrite).
   - Because `cloud-gtm` requires pull requests for `main`, push to a feature branch, open a PR via the GitHub REST API, wait for `CI/CD Pipeline` and `GitHub Actions Scan` (`zizmor`) to pass, and merge via `PUT /repos/cloud-gtm/<repo>/pulls/<number>/merge` to trigger the `main` deployment pipeline.
