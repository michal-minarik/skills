# Personal Agent Skills Repository

A personal collection of reusable AI agent skills for **Jetski** / **Gemini CLI**. Each skill is encapsulated in its own top-level directory and loaded into the local Jetski configuration (`~/.gemini/config/skills/`) via symbolic links.

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
| **`my-formatting`** | [`my-formatting/`](./my-formatting/) | Google Docs and Markdown formatting skill enforcing 4-level indentation, blue headers with pure black text, Question/Answer blocks, and short sentences (15–20 words max). |
| **`password-store`** | [`password-store/`](./password-store/) | Manage secrets, API keys, credentials, and passwords on CloudTop using [`pass`](https://www.passwordstore.org/) (the standard Unix password manager) and GPG. |

---

## Loading Skills into Jetski (Symlink Workflow)

Jetski discovers machine-local skills from `~/.gemini/config/skills/<skill-name>/SKILL.md`. To keep all personal skills version-controlled in this repository while making them active across all workspaces, symlink each skill folder into `~/.gemini/config/skills/`.

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
2. Add a `SKILL.md` file with required YAML frontmatter:
   ```markdown
   ---
   name: <skill-name>
   description: >-
     Clear description of what the skill does and when the agent should activate it.
   ---
   ```
3. Place bulky reference documentation in `<skill-name>/references/` and helper scripts in `<skill-name>/scripts/` to preserve token efficiency via progressive disclosure.
4. Create a symlink in `~/.gemini/config/skills/<skill-name>` pointing to `/usr/local/google/home/michalminarik/projects/skills/<skill-name>`.
5. Register the new skill in the **Available Skills** table in `README.md` and `GEMINI.md`.
