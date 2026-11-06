#!/usr/bin/env bash
set -euo pipefail

echo "=== Pass & GPG CloudTop Health Check ==="

# 1. Check pass binary
if command -v pass >/dev/null 2>&1; then
    echo "[✓] pass is installed: $(which pass) ($(pass version | head -n 1))"
else
    echo "[✗] pass is NOT installed."
fi

# 2. Check gpg binary
if command -v gpg >/dev/null 2>&1; then
    echo "[✓] gpg is installed: $(which gpg) ($(gpg --version | head -n 1))"
else
    echo "[✗] gpg is NOT installed."
fi

# 3. Check clipboard utilities
CLIP_FOUND=0
for clip in xclip wl-copy xsel; do
    if command -v "$clip" >/dev/null 2>&1; then
        echo "[✓] Clipboard tool found: $clip ($(which "$clip"))"
        CLIP_FOUND=1
        break
    fi
done
if [ "$CLIP_FOUND" -eq 0 ]; then
    echo "[!] No clipboard tool found (xclip, wl-copy, or xsel). 'pass -c' will not work."
fi

# 4. Check GPG_TTY environment variable
if [ -n "${GPG_TTY:-}" ]; then
    echo "[✓] GPG_TTY is set to: $GPG_TTY"
else
    echo "[!] GPG_TTY is not set in current shell. Add 'export GPG_TTY=\$(tty)' to ~/.bashrc or ~/.zshrc."
fi

# 5. Check GPG secret keys
SECRET_KEYS=$(gpg --list-secret-keys --keyid-format LONG 2>/dev/null || true)
if [ -n "$SECRET_KEYS" ]; then
    echo "[✓] GPG secret keys found:"
    echo "$SECRET_KEYS" | grep -E '^(sec|uid)' | sed 's/^/    /'
else
    echo "[!] No GPG secret keys found. Run 'gpg --full-generate-key' to create one."
fi

# 6. Check ~/.password-store
STORE_DIR="${PASSWORD_STORE_DIR:-$HOME/.password-store}"
if [ -d "$STORE_DIR" ]; then
    echo "[✓] Password store directory exists: $STORE_DIR"
    if [ -f "$STORE_DIR/.gpg-id" ]; then
        echo "[✓] Password store is initialized with GPG ID:"
        sed 's/^/    /' "$STORE_DIR/.gpg-id"
    else
        echo "[!] Password store exists but is not initialized (.gpg-id missing). Run 'pass init <gpg-id>'."
    fi
    if [ -d "$STORE_DIR/.git" ]; then
        echo "[✓] Password store is versioned with Git."
    else
        echo "[i] Password store is not git-initialized. Run 'pass git init' if versioning is desired."
    fi
else
    echo "[!] Password store directory does not exist yet ($STORE_DIR). Run 'pass init <gpg-id>' to initialize."
fi

echo "========================================"
