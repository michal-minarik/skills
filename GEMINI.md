# GEMINI.md — Personal Skills Repository Guidelines

This repository (`/usr/local/google/home/michalminarik/projects/skills`) is Michal Minařík's personal Git repository for custom **Jetski / Gemini agent skills** (`git@github.com:michal-minarik/skills.git`).

When operating inside this workspace, follow these architectural and operational rules.

---

## 1. Architecture & Encapsulation Rules

1. **One Folder per Skill**: Every skill must be encapsulated in its own top-level directory `<skill-name>/` directly under the repository root (`/usr/local/google/home/michalminarik/projects/skills/<skill-name>/`).
2. **Standard Skill Layout**:
   ```text
   <skill-name>/
   ├── SKILL.md          # Required: YAML frontmatter (name, description) + concise workflow instructions
   ├── scripts/          # Optional: Executable helper scripts (chmod +x)
   ├── references/       # Optional: Deep-dive documentation read on-demand
   ├── resources/        # Optional: Static assets or templates
   └── examples/         # Optional: Example configurations or code snippets
   ```
3. **Frontmatter Invariants**:
   - `name` in `SKILL.md` frontmatter **must** match the folder name `<skill-name>` (lowercase, hyphenated).
   - `description` must clearly specify both **what** the skill does and **when** the agent should use it.
4. **Progressive Disclosure**:
   - Keep `SKILL.md` focused and concise.
   - Offload detailed setup guides, long tables, and reference manuals into `<skill-name>/references/*.md` and link to them from `SKILL.md`.
   - Encapsulate multi-step diagnostics or automation in `<skill-name>/scripts/*`.

---

## 2. Symlink Integration with Jetski Configuration

Skills in this repository are loaded into Jetski via symbolic links in `/usr/local/google/home/michalminarik/.gemini/config/skills/`.

- **Symlink Target Convention**:
  ```text
  /usr/local/google/home/michalminarik/.gemini/config/skills/<skill-name>
    -> /usr/local/google/home/michalminarik/projects/skills/<skill-name>
  ```
- **When Creating or Moving a Skill**:
  1. Create or move the skill folder into `/usr/local/google/home/michalminarik/projects/skills/<skill-name>`.
  2. Create or update the symlink in `/usr/local/google/home/michalminarik/.gemini/config/skills/<skill-name>`:
     ```bash
     ln -sfn "/usr/local/google/home/michalminarik/projects/skills/<skill-name>" \
             "/usr/local/google/home/michalminarik/.gemini/config/skills/<skill-name>"
     ```
  3. Verify the symlink resolves properly and `SKILL.md` is readable through `~/.gemini/config/skills/<skill-name>/SKILL.md`.
- **Path References Inside Skills**:
  - Because `~/.gemini/config/skills/<skill-name>` symlinks directly to this repository, references using `~/.gemini/config/skills/<skill-name>/...` or `/usr/local/google/home/michalminarik/.gemini/config/skills/<skill-name>/...` remain valid across all workspaces.

---

## 3. Security & Hygiene (GitHub Remote)

Because this repository is backed by a GitHub remote (`git@github.com:michal-minarik/skills.git`):
- **Never commit secrets**: Do not include plaintext API keys, passwords, tokens, private keys, or sensitive internal customer data in any `SKILL.md`, script, or reference file.
- **Keep `git secrets` hooks passing**: Ensure all commits pass pre-commit secret scanning.

---

## 4. Current Skills Inventory

- **`password-store`** (`password-store/SKILL.md`): Manages secrets, API keys, credentials, and passwords on CloudTop using `pass` (the standard Unix password manager) and GPG.
  - Symlink: `~/.gemini/config/skills/password-store -> /usr/local/google/home/michalminarik/projects/skills/password-store`

> **Maintenance Rule**: Whenever you add, rename, or remove a skill in this repository, update the skill tables in both `README.md` and `GEMINI.md`.
