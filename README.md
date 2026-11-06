# Personal Agent Skills Repository

A personal collection of reusable AI agent skills for **Antigravity** / **Antigravity CLI**. Each skill is encapsulated in its own top-level directory and loaded into the local Antigravity configuration (`~/.gemini/config/skills/`) via symbolic links.

---

## Repository Structure

Each skill lives in a dedicated top-level folder named after its skill identifier (`<skill-name>/`):

```text
skills/
├── README.md                  # Repository overview, skill catalog, and setup guide
├── GEMINI.md                  # Instructions and conventions for AI agents working in this repo
└── <skill-name>/              # Self-contained skill directory
    ├── SKILL.md               # Required: YAML frontmatter (name, description) + core instructions
    ├── scripts/               # Optional: Executable helper scripts and health checks
    ├── references/            # Optional: Detailed guides loaded on-demand (progressive disclosure)
    ├── resources/             # Optional: Templates, schemas, or static assets
    └── examples/              # Optional: Reference implementations and usage examples
```

---

## Available Skills

| Skill | Folder | Description |
| :--- | :--- | :--- |
| **`my-adk-agent-builder`** | [`my-adk-agent-builder/`](./my-adk-agent-builder/) | End-to-end blueprint and environment conventions for creating, testing, securing, documenting, and deploying ADK agents (`ag-adk-*`) in Michal's CloudTop and Google Cloud environment (OpenTofu, WIF, Agent Runtime revisions, `cloud-gtm`). |
| **`my-formatting`** | [`my-formatting/`](./my-formatting/) | Unified formatting, layout, and channel mechanics skill for Google Docs, Markdown, Gmail drafts, and Google Chat (4-level indentation, blue headers with pure black text, zero inline backticks, short `-` hyphens, Q&A blocks in Docs, `ad 1)` in emails, and mandatory Gmail HTML draft creation with signatures). |
| **`my-voice`** | [`my-voice/`](./my-voice/) | Personal communication, persona, and terminology skill for Michal Minařík (12 Meta-Voice rules, Czech/English x Internal/External matrix, Google Cloud terminology mapping, calm matter-of-fact tone with zero `!` or unsolicited call offers, and 5 Scenario Dials). |
| **`my-secrets`** | [`my-secrets/`](./my-secrets/) | Manage secrets, API keys, credentials, and passwords on CloudTop using [`pass`](https://www.passwordstore.org/) (the standard Unix password manager) and GPG. |
| **`my-contacts-writer`** | [`my-contacts-writer/`](./my-contacts-writer/) | Create, update, inspect (including LinkedIn/websites and notes), and delete Google Contacts using Stubby RPCs to SocialGraphPeopleApiService via the local gchat EUC proxy. |
| **`my-meal-planner`** | [`my-meal-planner/`](./my-meal-planner/) | Family weekly meal planner and shopping list assistant ("Melee Master") for Michal Minařík, his wife, and their two daughters. Use whenever planning weekly meals, querying/updating the meal catalog, checking history, or generating Czech supermarket shopping lists. |

---

## Loading Skills into Antigravity (Symlink Workflow)

Antigravity discovers machine-local skills from `~/.gemini/config/skills/<skill-name>/SKILL.md`. To keep all personal skills version-controlled in this repository while making them active across all workspaces, symlink each skill folder into `~/.gemini/config/skills/`.

### Symlink a Single Skill

```bash
ln -s "$HOME/projects/skills/<skill-name>" "$HOME/.gemini/config/skills/<skill-name>"
```

### Symlink All Skills in This Repository

```bash
mkdir -p "$HOME/.gemini/config/skills"
for skill_dir in "$HOME/projects/skills"/*/; do
  skill_name="$(basename "$skill_dir")"
  if [ -f "${skill_dir}SKILL.md" ]; then
    ln -sfn "${skill_dir%/}" "$HOME/.gemini/config/skills/$skill_name"
    echo "Linked: $skill_name -> ${skill_dir%/}"
  fi
done
```

### Verify Active Symlinks

```bash
ls -la "$HOME/.gemini/config/skills/"
```

---

## Creating a New Skill

1. Create a new directory `<skill-name>/` at the root of this repository (use lowercase, hyphenated names).
2. Add a `SKILL.md` file with required YAML frontmatter and H1 title starting with `❤️`:
   ```markdown
   ---
   name: <skill-name>
   description: >-
     Clear description of what the skill does and when the agent should activate it.
   metadata:
     icon: ❤️
   ---

   # <Skill Title>
   ```
3. Place bulky reference documentation in `<skill-name>/references/` and helper scripts in `<skill-name>/scripts/` to preserve token efficiency via progressive disclosure.
4. Create a symlink in `~/.gemini/config/skills/<skill-name>` pointing to `/usr/local/google/home/michalminarik/projects/skills/<skill-name>`.
5. Register the new skill in the **Available Skills** table in `README.md` and `GEMINI.md`.
