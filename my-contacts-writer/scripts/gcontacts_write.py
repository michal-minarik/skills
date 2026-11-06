#!/usr/bin/env python3
"""CLI helper to get, create, update, and delete Google Contacts via Stubby.

Uses the local gchat server Unix socket proxy, which attaches the user's
Gaia Mint EUC (prod exchanger) to SocialGraphPeopleApiService RPCs on
blade:compass-social-graph-people-api-server-staging.
"""

import argparse
import json
import re
import secrets
import subprocess
import sys
import time
from typing import Any

DEFAULT_OWNER_GAIA_ID = 666772208510
GCHAT_BIN = "/google/bin/releases/gemini-agents-gchat/gchat"
STUBBY_BIN = "/usr/bin/stubby"
SERVICE_NAME = "social.graph.peopleapi.SocialGraphPeopleApiService"


def find_gchat_socket() -> str | None:
  res = subprocess.run(
      ["ss", "-xlp"], capture_output=True, text=True, check=False
  )
  matches = re.findall(r"@[^\s]*gchat\.sock", res.stdout)
  return matches[0] if matches else None


def ensure_proxy_socket(timeout_sec: float = 10.0) -> str:
  sock = find_gchat_socket()
  if sock:
    return sock

  unit_name = f"run-daemon-gchat-{ int(time.time()) }"
  subprocess.run(
      [
          "systemd-run",
          "--user",
          f"--unit={unit_name}",
          GCHAT_BIN,
          "server",
          "--linger=30m",
      ],
      capture_output=True,
      text=True,
      check=False,
  )

  deadline = time.time() + timeout_sec
  while time.time() < deadline:
    sock = find_gchat_socket()
    if sock:
      return sock
    time.sleep(0.25)

  raise RuntimeError(
      "Timed out waiting for gchat server Unix socket to appear in `ss -xlp`."
  )


def stubby_call(method: str, request_textproto: str) -> dict[str, Any]:
  sock = ensure_proxy_socket()
  cmd = [
      STUBBY_BIN,
      "call",
      "--globaldb",
      "--ignore_serverstatus",
      "--remotedb=false",
      "--output_json",
      f"unix:{sock}",
      f"{SERVICE_NAME}.{method}",
      request_textproto,
  ]
  res = subprocess.run(cmd, capture_output=True, text=True, check=False)
  if res.returncode != 0:
    raise RuntimeError(
        f"Stubby {method} failed (exit {res.returncode}):\n"
        f"{res.stderr.strip()}\n{res.stdout.strip()}"
    )
  out = res.stdout.strip()
  if not out:
    return {}
  return json.loads(out)


def escape_proto_str(val: str) -> str:
  return json.dumps(val, ensure_ascii=False)


def generate_contact_id() -> int:
  # Must satisfy focus::backend::id_generator::IsValidNonLegacyContactId:
  # positive 63-bit int where (id & 0x78000000) == 0x08000000 (RANDOM).
  return 0x08000000 | (secrets.randbits(63) & 0x7FFFFFFF87FFFFFF)


def normalize_person_id(raw_id: str) -> tuple[str, int, str]:
  """Returns (person_id 'c<dec>', decimal_id, hex_id) from 'c<dec>', '<dec>', or '<hex>'."""
  s = raw_id.strip()
  if s.startswith("c") and s[1:].isdigit():
    dec = int(s[1:])
    return f"c{dec}", dec, format(dec, "x")
  if s.isdigit():
    dec = int(s)
    return f"c{dec}", dec, format(dec, "x")
  # Try hex
  dec = int(s.removeprefix("0x"), 16)
  return f"c{dec}", dec, format(dec, "x")


def parse_typed_value(raw: str, default_type: str) -> tuple[str, str]:
  """Parses 'type:value' or 'value' (preserving URLs like https://...)."""
  if ":" in raw and not raw.startswith(("http://", "https://")):
    prefix, rest = raw.split(":", 1)
    if prefix.isalpha():
      return prefix.lower(), rest.strip()
  return default_type, raw.strip()


def fetch_person(person_id: str) -> dict[str, Any]:
  pid, _, _ = normalize_person_id(person_id)
  req = f"""
  person_id: {escape_proto_str(pid)}
  request_mask {{
    include_field {{
      paths: "person.metadata"
      paths: "person.name"
      paths: "person.email"
      paths: "person.phone"
      paths: "person.organization"
      paths: "person.website"
      paths: "person.about"
      paths: "person.address"
      paths: "person.birthday"
      paths: "person.user_defined"
    }}
    include_container: CONTACT
  }}
  """
  resp = stubby_call("GetPeople", req)
  responses = resp.get("person_response", [])
  if not responses:
    raise RuntimeError(f"No person_response returned for {pid}")
  pr = responses[0]
  status = pr.get("response_status", {})
  if status.get("code", 0) != 0:
    raise RuntimeError(f"GetPeople error for {pid}: {json.dumps(status)}")
  person = pr.get("person")
  if not person:
    raise RuntimeError(f"Contact {pid} not found.")
  return person


def format_person_summary(person: dict[str, Any]) -> dict[str, Any]:
  pid = person.get("person_id", "")
  names = person.get("name", [])
  name_obj = names[0] if names else {}
  orgs = person.get("organization", [])
  org_obj = orgs[0] if orgs else {}
  abouts = person.get("about", [])
  about_obj = abouts[0] if abouts else {}
  return {
      "personId": pid,
      "fingerprint": person.get("fingerprint", ""),
      "displayName": name_obj.get("display_name", ""),
      "givenName": name_obj.get("given_name", ""),
      "familyName": name_obj.get("family_name", ""),
      "middleName": name_obj.get("middle_name", ""),
      "honorificPrefix": name_obj.get("honorific_prefix", ""),
      "honorificSuffix": name_obj.get("honorific_suffix", ""),
      "emails": [
          {"value": e.get("value", ""), "type": e.get("type", "")}
          for e in person.get("email", [])
      ],
      "phones": [
          {"value": p.get("value", ""), "type": p.get("type", "")}
          for p in person.get("phone", [])
      ],
      "organization": {
          "name": org_obj.get("name", ""),
          "title": org_obj.get("title", ""),
          "department": org_obj.get("department", ""),
      }
      if org_obj
      else {},
      "websites": [
          {"value": w.get("value", ""), "type": w.get("type", "")}
          for w in person.get("website", [])
      ],
      "note": about_obj.get("value", ""),
  }


def build_person_blocks(
    name_fields: dict[str, str] | None,
    emails: list[tuple[str, str]] | None,
    phones: list[tuple[str, str]] | None,
    org_fields: dict[str, str] | None,
    websites: list[tuple[str, str]] | None,
    note: str | None,
) -> list[str]:
  blocks: list[str] = []

  if name_fields:
    lines = []
    for k in (
        "given_name",
        "family_name",
        "middle_name",
        "honorific_prefix",
        "honorific_suffix",
        "unstructured_name",
    ):
      v = name_fields.get(k)
      if v:
        lines.append(f"        {k}: {escape_proto_str(v)}")
    if lines:
      blocks.append("      name {\n" + "\n".join(lines) + "\n      }")

  if emails:
    for etype, eval_ in emails:
      blocks.append(
          "      email {\n"
          f"        value: {escape_proto_str(eval_)}\n"
          f"        type: {escape_proto_str(etype or 'work')}\n"
          "      }"
      )

  if phones:
    for ptype, pval in phones:
      blocks.append(
          "      phone {\n"
          f"        value: {escape_proto_str(pval)}\n"
          f"        type: {escape_proto_str(ptype or 'mobile')}\n"
          "      }"
      )

  if org_fields and any(org_fields.values()):
    lines = []
    for k in ("name", "title", "department"):
      v = org_fields.get(k)
      if v:
        lines.append(f"        {k}: {escape_proto_str(v)}")
    lines.append("        type: WORK")
    lines.append('        string_type: "work"')
    lines.append("        field_type_info { category: STANDARD }")
    blocks.append("      organization {\n" + "\n".join(lines) + "\n      }")

  if websites:
    for wtype, wval in websites:
      blocks.append(
          "      website {\n"
          f"        value: {escape_proto_str(wval)}\n"
          f"        type: {escape_proto_str(wtype or 'profile')}\n"
          "      }"
      )

  if note is not None and note != "":
    blocks.append(
        "      about {\n"
        f"        value: {escape_proto_str(note)}\n"
        "        content_type: TEXT_PLAIN\n"
        "      }"
    )

  return blocks


def cmd_get(args: argparse.Namespace) -> None:
  person = fetch_person(args.person_id)
  summary = format_person_summary(person)
  if args.json:
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return

  print(f"ID:           {summary['personId']}")
  print(f"Name:         {summary['displayName'] or '(none)'}")
  if summary["honorificPrefix"] or summary["honorificSuffix"]:
    print(
        f"Title/Degree: prefix={summary['honorificPrefix']!r} "
        f"suffix={summary['honorificSuffix']!r}"
    )
  for e in summary["emails"]:
    print(f"Email:        {e['value']} ({e['type'] or 'other'})")
  for p in summary["phones"]:
    print(f"Phone:        {p['value']} ({p['type'] or 'other'})")
  org = summary["organization"]
  if org and any(org.values()):
    print(
        f"Organization: {org.get('name', '')} — {org.get('title', '')}"
        + (f" [{org.get('department')}]" if org.get("department") else "")
    )
  for w in summary["websites"]:
    print(f"Website:      {w['value']} ({w['type'] or 'profile'})")
  if summary["note"]:
    print(f"Note:         {summary['note']}")


def cmd_create(args: argparse.Namespace) -> None:
  name_fields = {
      "given_name": args.given_name or "",
      "family_name": args.family_name or "",
      "middle_name": args.middle_name or "",
      "honorific_prefix": args.prefix or "",
      "honorific_suffix": args.suffix or "",
      "unstructured_name": args.full_name or "",
  }
  emails = [parse_typed_value(e, "work") for e in (args.email or [])]
  phones = [parse_typed_value(p, "mobile") for p in (args.phone or [])]
  org_fields = {
      "name": args.org or "",
      "title": args.title or "",
      "department": args.department or "",
  }
  websites = [parse_typed_value(w, "profile") for w in (args.website or [])]
  for li in args.linkedin or []:
    websites.append(("profile", li.strip()))

  blocks = build_person_blocks(
      name_fields=name_fields if any(name_fields.values()) else None,
      emails=emails,
      phones=phones,
      org_fields=org_fields if any(org_fields.values()) else None,
      websites=websites,
      note=args.note,
  )
  if not blocks:
    raise ValueError("At least one contact field must be provided to create.")

  contact_id = generate_contact_id()
  dry_run_block = ""
  if args.dry_run:
    dry_run_block = """
  [social.graph.peopleapi.create_contacts_dry_run_options] {
    dry_run_mode: DRY_RUN_MODE_SPANNER_MODS
  }"""

  contact_body = "\n".join(blocks)
  req = f"""
  owner_gaia_id: {args.owner_gaia_id}
  contacts {{
    contact {{
{contact_body}
    }}
    contact_id: {contact_id}
  }}
  get_people_request {{
    request_mask {{
      include_field {{
        paths: "person.name"
        paths: "person.email"
        paths: "person.phone"
        paths: "person.organization"
        paths: "person.website"
        paths: "person.about"
      }}
      include_container: CONTACT
    }}
  }}{dry_run_block}
  """
  resp = stubby_call("CreateContacts", req)
  person_id = f"c{contact_id}"
  if args.json:
    print(
        json.dumps(
            {
                "status": "DRY_RUN_OK" if args.dry_run else "CREATED",
                "personId": person_id,
                "contactId": str(contact_id),
                "hexId": format(contact_id, "x"),
                "response": resp,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
  else:
    mode_str = "[DRY-RUN] Validated" if args.dry_run else "Created"
    print(f"{mode_str} contact: {person_id} (hex: {format(contact_id, 'x')})")


def cmd_update(args: argparse.Namespace) -> None:
  person = fetch_person(args.person_id)
  pid, dec_id, hex_id = normalize_person_id(person.get("person_id", args.person_id))
  fingerprint = person.get("fingerprint", "")
  if not fingerprint:
    raise RuntimeError(f"Missing fingerprint on fetched contact {pid}")

  # Extract source_ids hex id if present
  source_ids = (
      person.get("metadata", {})
      .get("identity_info", {})
      .get("source_ids", [])
  )
  for sid in source_ids:
    if sid.get("container_type") in (2, "CONTACT") and sid.get("id"):
      hex_id = sid["id"]
      break

  update_paths: list[str] = []

  # 1. Name
  name_changed = any(
      v is not None
      for v in (
          args.given_name,
          args.family_name,
          args.middle_name,
          args.prefix,
          args.suffix,
          args.full_name,
      )
  )
  name_fields: dict[str, str] | None = None
  if name_changed:
    existing_name = (person.get("name") or [{}])[0] if not args.replace_name else {}
    name_fields = {
        "given_name": (
            args.given_name
            if args.given_name is not None
            else existing_name.get("given_name", "")
        ),
        "family_name": (
            args.family_name
            if args.family_name is not None
            else existing_name.get("family_name", "")
        ),
        "middle_name": (
            args.middle_name
            if args.middle_name is not None
            else existing_name.get("middle_name", "")
        ),
        "honorific_prefix": (
            args.prefix
            if args.prefix is not None
            else existing_name.get("honorific_prefix", "")
        ),
        "honorific_suffix": (
            args.suffix
            if args.suffix is not None
            else existing_name.get("honorific_suffix", "")
        ),
        "unstructured_name": args.full_name or "",
    }
    update_paths.append("person.name")

  # 2. Emails
  emails: list[tuple[str, str]] | None = None
  if args.email is not None or args.clear_emails:
    emails = []
    if not args.replace_emails and not args.clear_emails:
      for e in person.get("email", []):
        if e.get("value"):
          emails.append((e.get("type", "work"), e["value"]))
    if not args.clear_emails:
      seen = {v.lower() for _, v in emails}
      for raw_e in args.email or []:
        etype, eval_ = parse_typed_value(raw_e, "work")
        if eval_.lower() not in seen:
          emails.append((etype, eval_))
          seen.add(eval_.lower())
    update_paths.append("person.email")

  # 3. Phones
  phones: list[tuple[str, str]] | None = None
  if args.phone is not None or args.clear_phones:
    phones = []
    if not args.replace_phones and not args.clear_phones:
      for p in person.get("phone", []):
        if p.get("value"):
          phones.append((p.get("type", "mobile"), p["value"]))
    if not args.clear_phones:
      seen_p = {re.sub(r"\s+", "", v) for _, v in phones}
      for raw_p in args.phone or []:
        ptype, pval = parse_typed_value(raw_p, "mobile")
        norm_p = re.sub(r"\s+", "", pval)
        if norm_p not in seen_p:
          phones.append((ptype, pval))
          seen_p.add(norm_p)
    update_paths.append("person.phone")

  # 4. Organization
  org_changed = any(
      v is not None for v in (args.org, args.title, args.department)
  )
  org_fields: dict[str, str] | None = None
  if org_changed:
    existing_org = (
        (person.get("organization") or [{}])[0] if not args.replace_org else {}
    )
    org_fields = {
        "name": (
            args.org if args.org is not None else existing_org.get("name", "")
        ),
        "title": (
            args.title
            if args.title is not None
            else existing_org.get("title", "")
        ),
        "department": (
            args.department
            if args.department is not None
            else existing_org.get("department", "")
        ),
    }
    update_paths.append("person.organization")

  # 5. Websites / LinkedIn
  websites: list[tuple[str, str]] | None = None
  if args.website is not None or args.linkedin is not None or args.clear_websites:
    websites = []
    if not args.replace_websites and not args.clear_websites:
      for w in person.get("website", []):
        if w.get("value"):
          websites.append((w.get("type", "profile"), w["value"]))
    if not args.clear_websites:
      seen_w = {v.rstrip("/").lower() for _, v in websites}
      new_raw = [
          parse_typed_value(w, "profile") for w in (args.website or [])
      ] + [("profile", li.strip()) for li in (args.linkedin or [])]
      for wtype, wval in new_raw:
        norm_w = wval.rstrip("/").lower()
        if norm_w not in seen_w:
          websites.append((wtype, wval))
          seen_w.add(norm_w)
    update_paths.append("person.website")

  # 6. Note / About
  note: str | None = None
  if args.note is not None:
    note = args.note
    update_paths.append("person.about")

  if not update_paths:
    raise ValueError("No fields specified to update.")

  blocks = build_person_blocks(
      name_fields=name_fields,
      emails=emails,
      phones=phones,
      org_fields=org_fields,
      websites=websites,
      note=note,
  )

  dry_run_block = ""
  if args.dry_run:
    dry_run_block = """
  [social.graph.peopleapi.update_contacts_dry_run_options] {
    dry_run_mode: DRY_RUN_MODE_SPANNER_MODS
  }"""

  contact_body = "\n".join(blocks)
  mask_body = "\n".join(f"      paths: {escape_proto_str(p)}" for p in update_paths)
  req = f"""
  owner_gaia_id: {args.owner_gaia_id}
  contacts {{
    contact {{
      person_id: {escape_proto_str(pid)}
      fingerprint: {escape_proto_str(fingerprint)}
      metadata {{
        identity_info {{
          source_ids {{
            container_type: CONTACT
            id: {escape_proto_str(hex_id)}
          }}
        }}
      }}
{contact_body}
    }}
    update_mask {{
{mask_body}
    }}
  }}{dry_run_block}
  """
  resp = stubby_call("UpdateContacts", req)
  if args.json:
    print(
        json.dumps(
            {
                "status": "DRY_RUN_OK" if args.dry_run else "UPDATED",
                "personId": pid,
                "updatedMasks": update_paths,
                "response": resp,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
  else:
    mode_str = "[DRY-RUN] Validated update for" if args.dry_run else "Updated"
    print(f"{mode_str} {pid} (fields: {', '.join(update_paths)})")


def cmd_delete(args: argparse.Namespace) -> None:
  pid, _, hex_id = normalize_person_id(args.person_id)
  dry_run_block = ""
  if args.dry_run:
    dry_run_block = """
  [social.graph.peopleapi.delete_contacts_dry_run_options] {
    dry_run_mode: DRY_RUN_MODE_SPANNER_MODS
  }"""

  req = f"""
  owner_gaia_id: {args.owner_gaia_id}
  contact_id: {escape_proto_str(hex_id)}
  deletion_context {{
    mutation_context {{
      source: WEB_CONTACTS
    }}
  }}{dry_run_block}
  """
  resp = stubby_call("DeleteContacts", req)
  if args.json:
    print(
        json.dumps(
            {
                "status": "DRY_RUN_OK" if args.dry_run else "DELETED",
                "personId": pid,
                "hexId": hex_id,
                "response": resp,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
  else:
    mode_str = "[DRY-RUN] Validated deletion of" if args.dry_run else "Deleted"
    print(f"{mode_str} {pid} (hex: {hex_id})")


def build_parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
      description="Create, update, get, or delete Google Contacts via Stubby."
  )
  parser.add_argument(
      "--owner-gaia-id",
      type=int,
      default=DEFAULT_OWNER_GAIA_ID,
      help=f"Raw Gaia ID of the contact owner (default: {DEFAULT_OWNER_GAIA_ID})",
  )
  parser.add_argument(
      "--json", action="store_true", help="Output result in JSON format"
  )

  subparsers = parser.add_subparsers(dest="subcommand", required=True)

  # GET
  p_get = subparsers.add_parser(
      "get", help="Get full contact details (including website/LinkedIn and notes)"
  )
  p_get.add_argument("person_id", help="Contact ID (e.g. c123456789 or 123456789)")
  p_get.add_argument("--json", action="store_true", help="Output JSON")
  p_get.set_defaults(func=cmd_get)

  # Common contact field flags
  def add_contact_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--given-name", "--first-name", help="Given / first name")
    p.add_argument("--family-name", "--last-name", help="Family / last name")
    p.add_argument("--middle-name", help="Middle name")
    p.add_argument(
        "--prefix", help="Honorific prefix / title (e.g. 'Ing.', 'Mgr.')"
    )
    p.add_argument("--suffix", help="Honorific suffix (e.g. 'Ph.D.', 'MBA')")
    p.add_argument("--full-name", help="Unstructured full name")
    p.add_argument(
        "--email",
        action="append",
        help="Email address (repeatable; 'addr' or 'type:addr', default type: work)",
    )
    p.add_argument(
        "--phone",
        action="append",
        help="Phone number (repeatable; 'num' or 'type:num', default type: mobile)",
    )
    p.add_argument("--org", "--company", help="Organization / company name")
    p.add_argument("--title", "--role", help="Job title / role")
    p.add_argument("--department", help="Department name")
    p.add_argument(
        "--website",
        "--url",
        action="append",
        help="Website URL (repeatable; 'url' or 'type:url', default type: profile)",
    )
    p.add_argument(
        "--linkedin",
        action="append",
        help="LinkedIn profile URL (shorthand for --website profile:<url>)",
    )
    p.add_argument("--note", "--about", help="Contact note / biography")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate Spanner mutations without committing changes",
    )
    p.add_argument("--json", action="store_true", help="Output JSON")

  # CREATE
  p_create = subparsers.add_parser("create", help="Create a new Google Contact")
  add_contact_flags(p_create)
  p_create.set_defaults(func=cmd_create)

  # UPDATE
  p_update = subparsers.add_parser(
      "update",
      help="Update an existing Google Contact (merges with existing fields by default)",
  )
  p_update.add_argument(
      "person_id", help="Contact ID (e.g. c123456789 or 123456789)"
  )
  add_contact_flags(p_update)
  p_update.add_argument(
      "--replace-name",
      action="store_true",
      help="Replace all name subfields instead of merging with existing name",
  )
  p_update.add_argument(
      "--replace-emails",
      action="store_true",
      help="Replace existing emails instead of appending new ones",
  )
  p_update.add_argument(
      "--clear-emails", action="store_true", help="Remove all emails from contact"
  )
  p_update.add_argument(
      "--replace-phones",
      action="store_true",
      help="Replace existing phones instead of appending new ones",
  )
  p_update.add_argument(
      "--clear-phones", action="store_true", help="Remove all phones from contact"
  )
  p_update.add_argument(
      "--replace-org",
      action="store_true",
      help="Replace all organization subfields instead of merging",
  )
  p_update.add_argument(
      "--replace-websites",
      action="store_true",
      help="Replace existing websites/URLs instead of appending new ones",
  )
  p_update.add_argument(
      "--clear-websites",
      action="store_true",
      help="Remove all websites/URLs from contact",
  )
  p_update.set_defaults(func=cmd_update)

  # DELETE
  p_delete = subparsers.add_parser("delete", help="Delete (trash) a Google Contact")
  p_delete.add_argument(
      "person_id", help="Contact ID (e.g. c123456789, 123456789, or hex ID)"
  )
  p_delete.add_argument(
      "--dry-run",
      action="store_true",
      help="Validate Spanner mutations without committing deletion",
  )
  p_delete.add_argument("--json", action="store_true", help="Output JSON")
  p_delete.set_defaults(func=cmd_delete)

  return parser


def main() -> None:
  parser = build_parser()
  args = parser.parse_args()
  try:
    args.func(args)
  except Exception as exc:  # pylint: disable=broad-except
    print(f"Error: {exc}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
