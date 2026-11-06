# GPG and Password Store Setup on CloudTop

This guide walks through initial setup and configuration of GPG and `pass` (the standard unix password manager) specifically tailored for Google CloudTop workstations.

---

## 1. GPG Environment Configuration

Because CloudTop is frequently accessed over SSH, MobaXterm, or remote terminals without a full X11/Wayland desktop session, GPG must know which terminal device to use for PIN/passphrase entry.

### Step 1: Set `GPG_TTY` in Shell Profile
Add the following line to `~/.bashrc` (and/or `~/.zshrc`):

```bash
export GPG_TTY=$(tty)
```

Apply it immediately to the current shell:
```bash
export GPG_TTY=$(tty)
```

### Step 2: Configure `gpg-agent.conf`
Create or edit `~/.gnupg/gpg-agent.conf` to configure terminal-friendly pinentry and sensible passphrase caching so you don't have to re-enter your passphrase for every secret operation:

```ini
# Use curses pinentry for reliable terminal operation over SSH/CloudTop
pinentry-program /usr/bin/pinentry-curses

# Cache unlocked passphrase for 8 hours (28800 seconds)
default-cache-ttl 28800
# Maximum cache duration: 24 hours (86400 seconds)
max-cache-ttl 86400
```

Apply agent configuration:
```bash
gpg-connect-agent reloadagent /bye
```

---

## 2. Generate a GPG Key

If you do not already have a personal GPG key on this CloudTop:

### Interactive Generation (Recommended)
```bash
gpg --full-generate-key
```
Options to select:
1. **Key type**: `(9) ECC (sign and encrypt)` or `(1) RSA and RSA` (default 3072 or 4096).
2. **Elliptic curve**: `Curve 25519` (default for ECC) or key size `4096` for RSA.
3. **Key validity**: Choose expiration period (e.g. `2y` or `0` for no expiration).
4. **Real name**: e.g., `Michal Minařík`
5. **Email address**: e.g., `michalminarik@google.com`
6. **Passphrase**: Choose a strong master passphrase.

### Verify Key Creation
List your secret keys:
```bash
gpg --list-secret-keys --keyid-format LONG
```
Example output:
```text
sec   ed25519/ABCD1234EF567890 2026-09-18 [SC]
      E28F...FULL_FINGERPRINT...
uid                 [ultimate] Michal Minařík <michalminarik@google.com>
ssb   cv25519/1234567890ABCDEF 2026-09-18 [E]
```
The GPG ID to use for `pass` can be your email (`michalminarik@google.com`) or your Key ID / fingerprint (`ABCD1234EF567890`).

---

## 3. Initialize Password Store

Initialize `pass` with your GPG ID:

```bash
pass init michalminarik@google.com
```

This creates the directory `~/.password-store/` and writes `.gpg-id` specifying which public key encrypts the secrets.

### Subfolder / Multi-Recipient Keys (Advanced)
`pass` supports subfolder-specific encryption keys. For instance, shared team secrets can be encrypted for multiple team members:
```bash
pass init -p work/team-project user1@google.com user2@google.com
```

---

## 4. Enable Git Version Control

`pass` natively integrates with Git. Every secret addition, update, or deletion is committed automatically with an informative message.

Initialize Git tracking:
```bash
pass git init
```

Check the git status:
```bash
pass git status
pass git log
```

> [!NOTE]
> All files inside `~/.password-store/` are GPG-encrypted binary files ending in `.gpg`. Git only tracks encrypted data and directory paths. Secrets are never stored in plaintext on disk or in Git history.

---

## 5. Verification Checklist

Run the helper script to verify your setup:
```bash
~/.gemini/config/skills/my-secrets/scripts/check-setup.sh
```
All checks should display `[✓]`.
