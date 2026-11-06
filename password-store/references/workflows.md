# Password Store Workflows & Recipes

This guide provides daily operational workflows, conventions, and programmatic integration patterns for `pass` on CloudTop.

---

## 1. Secret Schema & Organization

### Path Hierarchy Best Practice
Group secrets logically using directories:
```text
~/.password-store/
├── cloud/
│   ├── gcp/
│   │   ├── service-accounts/
│   │   │   └── my-project-deployer.json.gpg
│   │   └── api-keys/
│   │       └── maps-dev.gpg
│   └── aws/
│       └── dev-credentials.gpg
├── tokens/
│   ├── github/
│   │   └── work-pat.gpg
│   └── slack/
│       └── bot-user-token.gpg
├── database/
│   ├── staging-postgres.gpg
│   └── local-mysql.gpg
└── personal/
    └── notes.gpg
```

### The "Line 1" Rule
`pass` tools (such as `pass show -c`, browser extensions, and dmenu/rofi integrations) assume that:
- **Line 1**: Contains **only** the secret value (password, token, or API key).
- **Line 2+**: Optional metadata formatted as `Key: Value`.

Example entry structure:
```text
sUp3r-S3cr3t-T0k3n-Value!
Username: michalminarik
Email: michalminarik@google.com
URL: https://github.com/settings/tokens
Expires: 2026-12-31
Scope: repo, workflow, read:org
Notes: Regenerated quarterly
```

---

## 2. Common CLI Commands

### Adding & Editing Secrets

| Action | Command | Notes |
| :--- | :--- | :--- |
| **Add single-line secret** | `pass insert tokens/github/pat` | Interactively prompts for secret twice with masked input. |
| **Add multi-line secret** | `pass insert -m database/postgres` | Paste text, press `Enter`, then `Ctrl+D` to finish. |
| **Overwrite without confirmation** | `pass insert -f tokens/github/pat` | Forces overwrite of existing secret. |
| **Generate strong password** | `pass generate cloud/db/admin 32` | Generates 32-character random string. |
| **Generate alphanumeric only** | `pass generate -n cloud/db/admin 24` | Omits special characters / symbols. |
| **Generate & copy to clipboard** | `pass generate -c tokens/test 20` | Generates and places on clipboard immediately. |
| **Edit in terminal editor** | `pass edit tokens/github/pat` | Opens decrypted file in `$EDITOR`; re-encrypts on save. |

### Reading & Searching Secrets

| Action | Command | Notes |
| :--- | :--- | :--- |
| **Tree view of all secrets** | `pass` or `pass ls` | Displays the folder tree without printing secret values. |
| **Show full entry (stdout)** | `pass show tokens/github/pat` | Decrypts and prints entire content to console. |
| **Copy secret to clipboard** | `pass show -c tokens/github/pat` | Copies line 1 to clipboard; auto-clears after 45 seconds. |
| **Extract secret only (line 1)** | `pass show tokens/github/pat \| head -n 1` | Safe for piping into variables or tools. |
| **Search by secret name/path** | `pass find github` | Searches path and file names. |
| **Search inside secret content** | `pass grep "username@example.com"` | Decrypts each entry and greps for search string. |

### Organizing & Deleting

| Action | Command | Notes |
| :--- | :--- | :--- |
| **Move / Rename secret** | `pass mv tokens/old-token tokens/new-token` | Automatically creates git commit. |
| **Copy secret** | `pass cp cloud/dev/db cloud/staging/db` | Creates copy under new path. |
| **Delete single secret** | `pass rm tokens/github/pat` | Prompts for confirmation. |
| **Delete entire folder** | `pass rm -rf test-folder/` | Recursively removes folder and files. |

---

## 3. Programmatic Integration

### A. Shell Scripts & Environment Variables

Directly populate environment variables without storing plaintext secrets in `.bashrc` or shell history:

```bash
# In your deployment or run script:
export GITHUB_TOKEN=$(pass show tokens/github/pat | head -n 1)
export DB_PASSWORD=$(pass show database/staging-postgres | head -n 1)
```

Extract a specific metadata field:
```bash
DB_USER=$(pass show database/staging-postgres | awk -F': ' '/^Username:/ {print $2}')
```

### B. Direnv Integration (`.envrc`)

If using `direnv` for project directories, configure your `.envrc`:
```bash
# .envrc
export API_KEY=$(pass show projects/analytics/api-key | head -n 1)
```
When you `cd` into the project directory, `direnv` automatically decrypts the secret into the environment.

### C. Python Integration

Fetch secrets dynamically in Python without third-party dependencies:

```python
import subprocess

def get_secret(secret_path: str, first_line_only: bool = True) -> str:
    """Retrieve secret from standard unix pass store."""
    result = subprocess.run(
        ["pass", "show", secret_path],
        capture_output=True,
        text=True,
        check=True
    )
    lines = result.stdout.splitlines()
    if first_line_only:
        return lines[0] if lines else ""
    return result.stdout

# Example usage:
token = get_secret("tokens/github/pat")
print(f"Token length: {len(token)}")
```

---

## 4. Git Synchronization & CloudTop Security

### Git Status & Commit History
Every time you add, modify, or remove an entry, `pass` automatically creates a git commit:
```bash
pass git log --oneline
```

### Pushing to a Remote Git Repository
If you maintain a private, encrypted backup repository (e.g. internal Git on Borg or private GitHub):
```bash
pass git remote add origin <repo-url>
pass git push -u origin master
```
> [!IMPORTANT]
> The repository only contains GPG-encrypted `.gpg` blobs. However, the directory paths and filenames are visible in Git plaintext. Avoid putting sensitive values (like actual API keys or plaintext passwords) in folder or file names.

### Clearing Cached Credentials in Memory
If you are stepping away or want to lock your password store immediately:
```bash
gpg-connect-agent reloadagent /bye
```
This flushes the cached passphrase from `gpg-agent`, requiring passphrase re-entry on the next `pass` invocation.
