---
name: my-contacts-writer
description: >-
  Create, update, inspect (including LinkedIn/websites and notes), and delete
  Google Contacts using Stubby RPCs to SocialGraphPeopleApiService via the
  local gchat EUC proxy. Use whenever creating a new contact, updating existing
  contact details (name, academic/honorific prefix/suffix, email, phone,
  organization, job title, LinkedIn URL, website, or notes), or deleting a
  contact in Google Contacts.
metadata:
  icon: ❤️
---

# My Contacts Writer Skill (my-contacts-writer)

The standard `gcontacts` CLI (`/google/bin/releases/gemini-agents-gcontacts/gcontacts`) is read-only and omits website/LinkedIn URLs and notes from `get`. This skill enables full **create**, **update**, **extended get**, and **delete** operations on Google Contacts via `/usr/bin/stubby` and the local `gchat server` Gaia Mint EUC proxy.

> [!CAUTION]
>
> Always ask for explicit user confirmation before running `delete` (or overwriting fields destructively). Use `--dry-run` whenever testing a mutation.

---

## Quick Start (Helper CLI)

Use the helper script [gcontacts_write.py](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-contacts-writer/scripts/gcontacts_write.py), which automatically starts the `gchat server` proxy socket if needed, generates valid Focus non-legacy contact IDs, fetches fingerprints, and merges existing fields on update:

```bash
~/.gemini/config/skills/my-contacts-writer/scripts/gcontacts_write.py --help
```

---

## Common Workflows

### 1. Inspect Full Contact Details (including LinkedIn URL & Notes)
Unlike the read-only `gcontacts get` binary (which only requests name, email, phone, and organization), `gcontacts_write.py get` fetches `person.website` (LinkedIn URLs), `person.about` (notes), and `honorific_prefix` / `honorific_suffix`:

```bash
~/.gemini/config/skills/my-contacts-writer/scripts/gcontacts_write.py get c3315153297446400605
~/.gemini/config/skills/my-contacts-writer/scripts/gcontacts_write.py get c3315153297446400605 --json
```

### 2. Create a New Contact
```bash
~/.gemini/config/skills/my-contacts-writer/scripts/gcontacts_write.py create \
  --prefix "Ing." \
  --given-name "Adam" \
  --family-name "Kučínský" \
  --email "adam.kucinsky@example.com" \
  --phone "+420 720 036 076" \
  --org "SIKO" \
  --title "Cloud & AI Delivery Lead" \
  --linkedin "https://www.linkedin.com/in/adam-kucinsky/" \
  --note "Key stakeholder for SIKO"
```
- Returns the created `personId` (`c<decimal_id>`) and hex container ID.
- Add `--dry-run` to validate against Spanner (`DRY_RUN_MODE_SPANNER_MODS`) without creating the contact.
- `--email`, `--phone`, `--website`, and `--linkedin` can be passed multiple times. Prefix with `type:value` (e.g., `home:user@gmail.com`, `work:+420123456789`) to override default types (`work` for email, `mobile` for phone, `profile` for website).

### 3. Update an Existing Contact (Safe Merge by Default)
By default, `update` fetches the contact's current `fingerprint` and **merges** your changes with existing subfields:
- Passing `--title "New Role"` preserves the existing `--org` company name.
- Passing `--phone "+420 111 222 333"` or `--linkedin "https://www.linkedin.com/in/..."` appends the new value (deduplicating automatically) without wiping existing phones or websites.

```bash
# Add a LinkedIn URL and phone number to an existing contact while keeping existing fields
~/.gemini/config/skills/my-contacts-writer/scripts/gcontacts_write.py update c3315153297446400605 \
  --phone "+420 777 888 999" \
  --linkedin "https://www.linkedin.com/in/johndoe/" \
  --title "VP of Engineering"
```

To **replace** or **clear** repeated fields instead of merging, use:
- `--replace-name` / `--replace-org`
- `--replace-emails` / `--clear-emails`
- `--replace-phones` / `--clear-phones`
- `--replace-websites` / `--clear-websites`

### 4. Delete (Trash) a Contact
Moves the contact to Google Contacts Trash (`WEB_CONTACTS` deletion context):
```bash
~/.gemini/config/skills/my-contacts-writer/scripts/gcontacts_write.py delete c3315153297446400605
```

---

## Raw Stubby Protocol & Validation Details

For raw `/usr/bin/stubby` textproto syntax, Focus `contact_id` bitmask rules, and `SocialGraphPeopleApiService` schema details, read [stubby-people-api.md](file:///usr/local/google/home/michalminarik/.gemini/config/skills/my-contacts-writer/references/stubby-people-api.md).
