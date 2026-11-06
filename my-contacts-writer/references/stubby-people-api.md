# Stubby People API Reference (`SocialGraphPeopleApiService`)

This reference documents the raw `/usr/bin/stubby` RPC calls, authentication proxy mechanics, and proto validation rules used by `my-contacts-writer`.

---

## 1. Local EUC Proxy (`gchat server`)

The pre-installed `gchat` binary (`/google/bin/releases/gemini-agents-gchat/gchat`) includes a local Unix-socket Stubby proxy (`gchat server`) defined in [`//depot/google3/learning/gemini/agents/clis/gchat/client.go`](file:///google/src/files/head/depot/google3/learning/gemini/agents/clis/gchat/client.go).

When started:
```bash
systemd-run --user --unit=run-daemon-gchat \
  /google/bin/releases/gemini-agents-gchat/gchat server --linger=30m
```
It listens on an abstract Unix socket matching `@michalminarik.<hash>-gchat.sock` (discoverable via `ss -xlp | grep -o '@[^ ]*gchat\.sock'`) and forwards all `social.graph.peopleapi.SocialGraphPeopleApiService` RPCs to `blade:compass-social-graph-people-api-server-staging` with Michal's Gaia Mint EUC (`prod` exchanger) and `ProjectContext` automatically attached.

---

## 2. Mandatory Backend Validation Rules

1. **`owner_gaia_id`**:
   - Must be set to Michal's raw Gaia ID: **`666772208510`**.
   - Do **not** use the obfuscated ID returned by `gcontacts get me` (`116466295811373376787`), which overflows signed `int64` and fails `FineGrainedCheckUsingGaiaIdMatchWithRequest`.
2. **`contact_id` (`CreateContactsRequest`)**:
   - Validated by [`IsValidNonLegacyContactId`](file:///google/src/files/head/depot/google3/focus/backend/public/id_generator.cc#L18-L21):
     - Must be a positive 63-bit integer (`> 0`).
     - Bits `0x78000000` must equal `0x08000000` (`RANDOM`) or `0x10000000` (`HASH`).
   - Python formula:
     ```python
     import secrets
     contact_id = 0x08000000 | (secrets.randbits(63) & 0x7FFFFFFF87FFFFFF)
     ```
3. **`organization` (`ValidateContactOrganization`)**:
   - Enforced in [`contact_field_validators.cc`](file:///google/src/files/head/depot/google3/social/graph/contacts/shared/validation/contact_field_validators.cc#L127-L147):
   - Every `organization` entry **must** include `field_type_info { category: STANDARD }` (and `string_type: "work"` when `type: WORK` is set):
     ```protobuf
     organization {
       name: "ACME Corp"
       title: "CTO"
       department: "Engineering"
       type: WORK
       string_type: "work"
       field_type_info { category: STANDARD }
     }
     ```
4. **`website` (`ValidateContactWebsite`)**:
   - `value` must be non-empty; `rel` must **not** be set (`type` can be `"profile"`, `"work"`, `"homePage"`, etc.).
5. **`UpdateContactsRequest` Concurrency & Identity**:
   - Enforced in [`request_converter.cc`](file:///google/src/files/head/depot/google3/social/graph/peopleapi/mixer/backends/contacts/request_converter.cc#L340-L409):
   - Requires `contact.person_id` (`"c<decimal_id>"`), `contact.fingerprint` (from `GetPeople`), and `contact.metadata.identity_info.source_ids` with `container_type: CONTACT` and `id: "<lowercase_hex_id>"` matching `<decimal_id>`.
   - `update_mask` paths must use `person.<field>` (e.g., `person.name`, `person.email`, `person.phone`, `person.organization`, `person.website`, `person.about`).

---

## 3. Raw `stubby` Recipes

### A. Get Full Contact (`GetPeople`)
```bash
SOCK=$(ss -xlp 2>/dev/null | grep -o '@[^ ]*gchat\.sock' | head -n 1)
stubby call --globaldb --ignore_serverstatus --remotedb=false --output_json \
  "unix:${SOCK}" \
  social.graph.peopleapi.SocialGraphPeopleApiService.GetPeople '
  person_id: "c3315153297446400605"
  request_mask {
    include_field {
      paths: "person.metadata"
      paths: "person.name"
      paths: "person.email"
      paths: "person.phone"
      paths: "person.organization"
      paths: "person.website"
      paths: "person.about"
    }
    include_container: CONTACT
  }
'
```

### B. Create Contact (`CreateContacts`)
```bash
SOCK=$(ss -xlp 2>/dev/null | grep -o '@[^ ]*gchat\.sock' | head -n 1)
CONTACT_ID=$(python3 -c 'import secrets; print(0x08000000 | (secrets.randbits(63) & 0x7FFFFFFF87FFFFFF))')

stubby call --globaldb --ignore_serverstatus --remotedb=false --output_json \
  "unix:${SOCK}" \
  social.graph.peopleapi.SocialGraphPeopleApiService.CreateContacts "
  owner_gaia_id: 666772208510
  contacts {
    contact {
      name {
        honorific_prefix: \"Ing.\"
        given_name: \"Jan\"
        family_name: \"Novák\"
      }
      email { value: \"jan.novak@example.com\" type: \"work\" }
      phone { value: \"+420 123 456 789\" type: \"mobile\" }
      organization {
        name: \"ACME Corp\"
        title: \"CTO\"
        type: WORK
        string_type: \"work\"
        field_type_info { category: STANDARD }
      }
      website { value: \"https://www.linkedin.com/in/jannovak/\" type: \"profile\" }
      about { value: \"Key stakeholder\" content_type: TEXT_PLAIN }
    }
    contact_id: ${CONTACT_ID}
  }
"
```

### C. Update Contact (`UpdateContacts`)
```bash
SOCK=$(ss -xlp 2>/dev/null | grep -o '@[^ ]*gchat\.sock' | head -n 1)

stubby call --globaldb --ignore_serverstatus --remotedb=false --output_json \
  "unix:${SOCK}" \
  social.graph.peopleapi.SocialGraphPeopleApiService.UpdateContacts '
  owner_gaia_id: 666772208510
  contacts {
    contact {
      person_id: "c3315153297446400605"
      fingerprint: "<fingerprint_from_GetPeople>"
      metadata {
        identity_info {
          source_ids {
            container_type: CONTACT
            id: "2e01ca5c0e41f25d"
          }
        }
      }
      website {
        value: "https://www.linkedin.com/in/jannovak/"
        type: "profile"
      }
    }
    update_mask {
      paths: "person.website"
    }
  }
'
```

### D. Delete Contact (`DeleteContacts`)
```bash
SOCK=$(ss -xlp 2>/dev/null | grep -o '@[^ ]*gchat\.sock' | head -n 1)

stubby call --globaldb --ignore_serverstatus --remotedb=false --output_json \
  "unix:${SOCK}" \
  social.graph.peopleapi.SocialGraphPeopleApiService.DeleteContacts '
  owner_gaia_id: 666772208510
  contact_id: "2e01ca5c0e41f25d"
  deletion_context {
    mutation_context {
      source: WEB_CONTACTS
    }
  }
'
```

### E. Dry-Run Extensions
Append any of the following to validate Spanner mutations without committing:
- `CreateContacts`: `[social.graph.peopleapi.create_contacts_dry_run_options] { dry_run_mode: DRY_RUN_MODE_SPANNER_MODS }`
- `UpdateContacts`: `[social.graph.peopleapi.update_contacts_dry_run_options] { dry_run_mode: DRY_RUN_MODE_SPANNER_MODS }`
- `DeleteContacts`: `[social.graph.peopleapi.delete_contacts_dry_run_options] { dry_run_mode: DRY_RUN_MODE_SPANNER_MODS }`
