---
name: my-secrets
description: >-
  Manage secrets, API keys, credentials, and passwords on CloudTop using the standard unix password manager (pass).
  Use when initializing password-store (pass), checking GPG keys, generating passwords, inserting, reading, editing,
  searching, organizing secrets, or integrating pass with automation scripts.
metadata:
  icon: ❤️
---

# My Secrets Skill (my-secrets)

This skill guides the agent and user in managing secrets, API keys, credentials, and configuration tokens on Google CloudTop workstations using [`pass`](https://www.passwordstore.org/) (the standard unix password manager).

`pass` stores secrets as individual GPG-encrypted files within a hierarchical directory tree at `~/.password-store/` and provides automatic Git versioning.

---

## 1. Quick Diagnostic & Setup Status

Always verify the workstation environment before performing secret operations:

Run the health check helper:
```bash
~/.gemini/config/skills/my-secrets/scripts/check-setup.sh
```

Helper script details: [check-setup.sh](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-secrets/scripts/check-setup.sh)

### Prerequisites Checklist
- [x] **`pass` binary**: Installed at `/usr/bin/pass`.
- [x] **Clipboard integration**: `xclip` and `wl-copy` installed.
- [ ] **Terminal Pinentry**: Ensure `export GPG_TTY=$(tty)` is present in `~/.bashrc`.
- [ ] **GPG Key**: A secret key must exist (`gpg --list-secret-keys`).
- [ ] **Store Initialization**: `pass init <gpg-id>` executed.

For complete step-by-step instructions on GPG key generation, `gpg-agent.conf` caching, and store initialization, see [setup-and-gpg.md](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-secrets/references/setup-and-gpg.md).

---

## 2. Core Operational Procedures

Detailed command syntax and patterns are documented in [workflows.md](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-secrets/references/workflows.md).

### A. Secret Organization Convention ("Line 1 Rule")
Always structure secret files as follows:
- **Line 1**: Secret value alone (password, API token, bearer token, etc.).
- **Line 2+**: Metadata in `Key: Value` format (username, email, expiration, target service).

```text
my-secret-token-12345
Username: michalminarik
Service: GCP Cloud Function
Expires: 2026-12-31
```
*Rationale*: `pass show -c` copies only line 1 to the clipboard, preventing metadata leakage.

### B. Standard Commands

#### 1. Inserting Secrets
- **Interactive single-line** (prompts for masked password twice):
  ```bash
  pass insert tokens/service-token
  ```
- **Multiline entry** (password + metadata; finish with `Enter` then `Ctrl+D`):
  ```bash
  pass insert -m database/postgres-prod
  ```
- **Piping into pass** (for automation or script-generated keys):
  ```bash
  echo -n "$SECRET_VALUE" | pass insert -m tokens/api-token
  ```

#### 2. Generating Secrets
- **Generate random password** (e.g. 32 chars):
  ```bash
  pass generate cloud/db-root 32
  ```
- **Generate alphanumeric only (no symbols)**:
  ```bash
  pass generate -n tokens/api-key 24
  ```

#### 3. Reading & Retrieving Secrets
- **Display full secret & metadata**:
  ```bash
  pass show tokens/service-token
  ```
- **Copy password to clipboard** (auto-clears after 45 seconds):
  ```bash
  pass show -c tokens/service-token
  ```
- **Extract secret value only for scripts/variables**:
  ```bash
  SECRET=$(pass show tokens/service-token | head -n 1)
  ```

#### 4. Listing & Searching
- **Tree listing**:
  ```bash
  pass
  # or list a subfolder:
  pass cloud/
  ```
- **Search secret paths**:
  ```bash
  pass find github
  ```
- **Grep inside decrypted secrets**:
  ```bash
  pass grep "user@domain.com"
  ```

#### 5. Editing & Deletion
- **Edit in terminal `$EDITOR`**:
  ```bash
  pass edit tokens/service-token
  ```
- **Remove an entry**:
  ```bash
  pass rm tokens/service-token
  ```

---

## 3. Automation & Programmatic Access

### Bash Script Integration
```bash
#!/usr/bin/env bash
export API_TOKEN=$(pass show tokens/github/pat | head -n 1)
curl -H "Authorization: Bearer $API_TOKEN" https://api.github.com/user
```

### Python Script Integration
```python
import subprocess

def get_secret(path: str) -> str:
    res = subprocess.run(["pass", "show", path], capture_output=True, text=True, check=True)
    return res.stdout.splitlines()[0]

token = get_secret("tokens/github/pat")
```

---

## 4. Git Versioning & Remote Sync

`pass` automatically tracks additions, modifications, and deletions in Git once initialized:
- **Initialize Git**: `pass git init`
- **Check Status / Log**:
  ```bash
  pass git status
  pass git log --oneline
  ```
- **Syncing to Remote**:
  ```bash
  pass git remote add origin <remote-url>
  pass git push -u origin master
  ```

---

## 5. CloudTop Troubleshooting

1. **`Inappropriate ioctl for device` or pinentry hanging**:
   - Verify `export GPG_TTY=$(tty)` is set in the active terminal.
   - Verify `pinentry-program /usr/bin/pinentry-curses` is set in `~/.gnupg/gpg-agent.conf`.
   - Reload agent: `gpg-connect-agent reloadagent /bye`.
2. **`gpg: decryption failed: No secret key`**:
   - Check `gpg --list-secret-keys --keyid-format LONG`.
   - Verify the ID in `~/.password-store/.gpg-id` matches your secret key ID.
3. **Locking store / clearing cached passphrase**:
   - Flush agent memory: `gpg-connect-agent reloadagent /bye`.
