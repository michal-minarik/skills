#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Agent Runtime Revision Manager, Traffic Router, and Binding Helper.

Provides deterministic CLI subcommands used by the GitHub Actions CI/CD pipeline:
  1. `list`               - Lists all runtimeRevisions and active traffic routing.
  2. `verify-and-promote` - Smoke-tests the latest runtimeRevision, routes 100%
                            traffic to it via `traffic_split_manual`, and ensures
                            Agent Identity IAM + Agent Registry OAuth binding.
  3. `rollback`           - Shifts 100% traffic to a specific revision ID (or
                            `previous`) for instant zero-rebuild rollback.
  4. `cleanup-legacy`     - Removes a legacy agent registration from Gemini
                            Enterprise and deletes its Agent Runtime engine.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from typing import Any

import google.auth
import requests
from google.auth.transport.requests import Request

METADATA_FILE = pathlib.Path("deployment_metadata.json")


def get_access_token() -> str:
    """Obtains a valid Google Cloud OAuth2 access token from ADC / WIF."""
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not creds.valid:
        creds.refresh(Request())
    assert creds.token is not None, "Failed to obtain access token"
    return creds.token


def api_headers(project: str) -> dict[str, str]:
    """Returns standard headers for Google Cloud REST API calls."""
    return {
        "Authorization": f"Bearer {get_access_token()}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project,
    }


def wait_for_lro(
    operation_url: str,
    project: str,
    timeout_sec: int = 300,
    poll_sec: int = 5,
) -> dict[str, Any]:
    """Polls a Google Cloud Long-Running Operation (LRO) until completion."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        resp = requests.get(operation_url, headers=api_headers(project), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("done"):
            if "error" in data:
                raise RuntimeError(f"Operation failed: {json.dumps(data['error'])}")
            return data
        time.sleep(poll_sec)
    raise TimeoutError(f"Operation timed out after {timeout_sec}s: {operation_url}")


def find_reasoning_engine(
    project: str,
    location: str,
    agent_name: str,
    prefer_metadata: bool = True,
) -> dict[str, Any]:
    """Resolves the ReasoningEngine resource dict by metadata or displayName."""
    base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1"

    if prefer_metadata and METADATA_FILE.exists():
        meta = json.loads(METADATA_FILE.read_text(encoding="utf-8"))
        runtime_id = meta.get("remote_agent_runtime_id")
        if runtime_id:
            resp = requests.get(
                f"{base_url}/{runtime_id}",
                headers=api_headers(project),
                timeout=30,
            )
            if resp.status_code == 200:
                engine = resp.json()
                if engine.get("displayName") == agent_name:
                    return engine

    resp = requests.get(
        f"{base_url}/projects/{project}/locations/{location}/reasoningEngines",
        headers=api_headers(project),
        timeout=30,
    )
    resp.raise_for_status()
    engines = resp.json().get("reasoningEngines", [])
    matches = [e for e in engines if e.get("displayName") == agent_name]
    if not matches:
        raise RuntimeError(
            f"No ReasoningEngine with displayName='{agent_name}' found in {project}/{location}."
        )
    # Sort newest first if multiple exist
    matches.sort(key=lambda e: e.get("createTime", ""), reverse=True)
    full_name = matches[0]["name"]
    detail = requests.get(
        f"{base_url}/{full_name}", headers=api_headers(project), timeout=30
    )
    detail.raise_for_status()
    return detail.json()


def list_runtime_revisions(
    project: str,
    location: str,
    engine_name: str,
) -> list[dict[str, Any]]:
    """Lists all runtimeRevisions for a ReasoningEngine, sorted newest first."""
    base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1"
    revisions: list[dict[str, Any]] = []
    page_token = ""
    while True:
        params: dict[str, Any] = {"pageSize": 50}
        if page_token:
            params["pageToken"] = page_token
        resp = requests.get(
            f"{base_url}/{engine_name}/runtimeRevisions",
            headers=api_headers(project),
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        revisions.extend(body.get("reasoningEngineRuntimeRevisions", []))
        page_token = body.get("nextPageToken", "")
        if not page_token:
            break

    # Sort by createTime descending (fallback to revision resource name)
    revisions.sort(
        key=lambda r: (r.get("createTime", ""), r.get("name", "")),
        reverse=True,
    )
    return revisions


def smoke_test_revision(
    project: str,
    location: str,
    revision_name: str,
) -> None:
    """Executes a smoke test query against a specific runtimeRevision."""
    base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1"
    print(f"🧪 Smoke-testing runtime revision: {revision_name} ...")

    # Create a lightweight ADK session against the revision (or parent engine)
    query_url = f"{base_url}/{revision_name}:query"
    payload = {
        "classMethod": "async_create_session",
        "input": {"user_id": "cicd-smoke-test"},
    }
    resp = requests.post(
        query_url,
        headers=api_headers(project),
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"Smoke test failed on {revision_name} (HTTP {resp.status_code}): {resp.text}"
        )
    output = resp.json().get("output", {})
    session_id = output.get("id") if isinstance(output, dict) else None
    print(f"  ✅ Revision responded cleanly (created session_id={session_id}).")


def set_traffic_to_revision(
    project: str,
    location: str,
    engine_name: str,
    revision_name: str,
) -> None:
    """Shifts 100% of live traffic to the target runtimeRevision."""
    base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1"
    short_rev_id = revision_name.rsplit("/", 1)[-1]
    print(f"🔀 Routing 100% traffic on {engine_name} -> revision {short_rev_id} ...")

    patch_url = f"{base_url}/{engine_name}"
    body = {
        "trafficConfig": {
            "trafficSplitManual": {
                "targets": [
                    {
                        "runtimeRevisionName": revision_name,
                        "percent": 100,
                    }
                ]
            }
        }
    }
    resp = requests.patch(
        patch_url,
        headers=api_headers(project),
        params={"updateMask": "trafficConfig"},
        json=body,
        timeout=60,
    )
    if resp.status_code != 200:
        # Some API deployments accept the short revision ID in runtimeRevisionName
        body["trafficConfig"]["trafficSplitManual"]["targets"][0][
            "runtimeRevisionName"
        ] = short_rev_id
        resp = requests.patch(
            patch_url,
            headers=api_headers(project),
            params={"updateMask": "trafficConfig"},
            json=body,
            timeout=60,
        )
    resp.raise_for_status()
    op = resp.json()
    if op.get("name") and not op.get("done", False):
        op_url = f"{base_url}/{op['name']}"
        wait_for_lro(op_url, project)
    print(f"  ✅ 100% traffic is now served by revision {short_rev_id}.")


def ensure_agent_identity_and_binding(
    project: str,
    location: str,
    engine: dict[str, Any],
    mcp_service_name: str,
    auth_provider_id: str,
    binding_id: str,
) -> None:
    """Ensures the Agent Identity principal has required IAM roles and Agent Registry Binding."""
    spec = engine.get("spec", {})
    effective_identity = spec.get("effectiveIdentity", "")
    if not effective_identity:
        print(
            "[info] No effectiveIdentity found on engine spec; skipping identity binding."
        )
        return

    principal = (
        effective_identity
        if effective_identity.startswith("principal://")
        else f"principal://{effective_identity}"
    )
    print(f"🔐 Ensuring project IAM roles for Agent Identity: {principal}")

    crm_url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project}:getIamPolicy"
    set_url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project}:setIamPolicy"

    policy_resp = requests.post(
        crm_url, headers=api_headers(project), json={}, timeout=30
    )
    policy_resp.raise_for_status()
    policy = policy_resp.json()
    bindings = policy.get("bindings", [])

    required_roles = [
        "roles/aiplatform.user",
        "roles/agentregistry.viewer",
        "roles/secretmanager.secretAccessor",
        "roles/serviceusage.serviceUsageConsumer",
        "roles/cloudapiregistry.viewer",
        "roles/logging.logWriter",
        "roles/monitoring.metricWriter",
    ]
    changed = False
    for role in required_roles:
        role_binding = next((b for b in bindings if b.get("role") == role), None)
        if role_binding is None:
            bindings.append({"role": role, "members": [principal]})
            changed = True
        elif principal not in role_binding.get("members", []):
            role_binding.setdefault("members", []).append(principal)
            changed = True

    if changed:
        policy["bindings"] = bindings
        set_resp = requests.post(
            set_url,
            headers=api_headers(project),
            json={"policy": policy},
            timeout=30,
        )
        set_resp.raise_for_status()
        print(
            "  ✅ Updated project IAM bindings for Agent Identity (waiting 15s for IAM propagation)..."
        )
        time.sleep(15)
    else:
        print("  ✅ Project IAM bindings already up to date.")

    # Ensure Agent Registry AuthProvider Binding points to this ReasoningEngine's URN
    ar_base = f"https://agentregistry.googleapis.com/v1alpha/projects/{project}/locations/{location}"
    mcp_resp = requests.get(
        f"{ar_base}/mcpServers", headers=api_headers(project), timeout=30
    )
    if mcp_resp.status_code != 200:
        print(
            f"⚠️  Could not list MCP servers (HTTP {mcp_resp.status_code}); skipping binding update."
        )
        return

    servers = mcp_resp.json().get("mcpServers", [])
    target_urn = None
    for s in servers:
        if mcp_service_name in s.get("name", "") or mcp_service_name in s.get(
            "mcpServerId", ""
        ):
            target_urn = s.get("mcpServerId")
            break
    if not target_urn:
        print(
            f"⚠️  MCP Server '{mcp_service_name}' not found in Agent Registry; skipping binding update."
        )
        return

    # Construct Agent Registry URN from engine["name"]:
    # projects/{proj_num}/locations/{loc}/reasoningEngines/{eng_id}
    name_parts = engine["name"].split("/")
    proj_num = name_parts[1]
    eng_loc = name_parts[3]
    eng_id = name_parts[5]
    source_urn = (
        f"urn:agent:projects-{proj_num}:projects:{proj_num}:"
        f"locations:{eng_loc}:aiplatform:reasoningEngines:{eng_id}"
    )

    auth_provider_full = (
        f"projects/{project}/locations/{location}/authProviders/{auth_provider_id}"
    )
    binding_full = f"projects/{project}/locations/{location}/bindings/{binding_id}"
    binding_payload = {
        "displayName": "Asana MCP OAuth Binding",
        "description": f"Binds {engine.get('displayName', 'ADK Agent')} (ReasoningEngine {eng_id}) to Asana MCP Server with 3LO AuthProvider",
        "source": {"identifier": source_urn},
        "target": {"identifier": target_urn},
        "authProviderBinding": {"authProvider": auth_provider_full},
    }

    print(f"🔗 Ensuring Agent Registry Binding '{binding_id}' -> {source_urn} ...")
    get_b = requests.get(
        f"https://agentregistry.googleapis.com/v1alpha/{binding_full}",
        headers=api_headers(project),
        timeout=30,
    )
    if get_b.status_code == 200:
        existing_b = get_b.json()
        existing_src = existing_b.get("source", {}).get("identifier")
        existing_tgt = existing_b.get("target", {}).get("identifier")
        if existing_src == source_urn and existing_tgt == target_urn:
            print("  ✅ Agent Registry Binding already up to date.")
            return
        print(
            f"  ♻️  Binding source changed ({existing_src} -> {source_urn}); recreating binding..."
        )
        del_b = requests.delete(
            f"https://agentregistry.googleapis.com/v1alpha/{binding_full}",
            headers=api_headers(project),
            timeout=30,
        )
        del_b.raise_for_status()
        del_op = del_b.json()
        if del_op.get("name") and not del_op.get("done", False):
            wait_for_lro(
                f"https://agentregistry.googleapis.com/v1alpha/{del_op['name']}",
                project,
            )

    create_b = requests.post(
        f"{ar_base}/bindings",
        headers=api_headers(project),
        params={"bindingId": binding_id},
        json=binding_payload,
        timeout=30,
    )
    create_b.raise_for_status()
    create_op = create_b.json()
    if create_op.get("name") and not create_op.get("done", False):
        wait_for_lro(
            f"https://agentregistry.googleapis.com/v1alpha/{create_op['name']}",
            project,
        )
    print("  ✅ Configured Agent Registry Binding.")


def cmd_prepare_identity(args: argparse.Namespace) -> None:
    """Ensures ReasoningEngine shell, Agent Identity IAM roles, and Agent Registry Binding exist before deploy."""
    base_url = f"https://{args.location}-aiplatform.googleapis.com/v1beta1"
    parent = f"projects/{args.project}/locations/{args.location}"
    try:
        engine = find_reasoning_engine(args.project, args.location, args.agent_name)
        print(
            f"✅ Found existing ReasoningEngine: {engine['name']} (displayName={engine.get('displayName')})"
        )
    except RuntimeError:
        print(
            f"🔧 Creating ReasoningEngine shell with Agent Identity for '{args.agent_name}'..."
        )
        create_resp = requests.post(
            f"{base_url}/{parent}/reasoningEngines",
            headers=api_headers(args.project),
            json={
                "displayName": args.agent_name,
                "spec": {"identityType": "AGENT_IDENTITY"},
            },
            timeout=60,
        )
        create_resp.raise_for_status()
        op = create_resp.json()
        if op.get("name") and not op.get("done", False):
            wait_for_lro(f"{base_url}/{op['name']}", args.project)
        engine = find_reasoning_engine(args.project, args.location, args.agent_name)
        print(f"  ✅ Created ReasoningEngine shell: {engine['name']}")

    ensure_agent_identity_and_binding(
        project=args.project,
        location=args.location,
        engine=engine,
        mcp_service_name=args.mcp_service_name,
        auth_provider_id=args.auth_provider_id,
        binding_id=args.binding_id,
    )


def cmd_list(args: argparse.Namespace) -> None:
    """Lists all runtimeRevisions and traffic routing for the agent."""
    engine = find_reasoning_engine(args.project, args.location, args.agent_name)
    engine_name = engine["name"]
    revisions = list_runtime_revisions(args.project, args.location, engine_name)
    traffic = engine.get("trafficConfig", {})

    print(f"Agent Runtime: {engine_name} (displayName={engine.get('displayName')})")
    print(f"Traffic Config: {json.dumps(traffic)}")
    print(f"\nFound {len(revisions)} runtime revision(s):")
    for idx, rev in enumerate(revisions, start=1):
        rev_id = rev["name"].rsplit("/", 1)[-1]
        state = rev.get("state", "UNKNOWN")
        created = rev.get("createTime", "")
        print(f"  [{idx}] {rev_id} | state={state} | created={created}")


def cmd_verify_and_promote(args: argparse.Namespace) -> None:
    """Smoke-tests the newest revision, shifts 100% traffic to it, and updates bindings."""
    engine = find_reasoning_engine(args.project, args.location, args.agent_name)
    engine_name = engine["name"]

    # Persist deployment_metadata.json for downstream `agents-cli publish`
    metadata = {
        "remote_agent_runtime_id": engine_name,
        "deployment_target": "agent_runtime",
        "is_a2a": True,
        "language": "python",
        "agent_directory": "app",
    }
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    # 1. Ensure Agent Identity IAM and Agent Registry OAuth binding first so the
    #    revision has all permissions during smoke testing.
    ensure_agent_identity_and_binding(
        project=args.project,
        location=args.location,
        engine=engine,
        mcp_service_name=args.mcp_service_name,
        auth_provider_id=args.auth_provider_id,
        binding_id=args.binding_id,
    )

    # 2. Discover the newest runtimeRevision
    revisions = list_runtime_revisions(args.project, args.location, engine_name)
    if not revisions:
        raise RuntimeError(f"No runtimeRevisions found under {engine_name}")

    latest_rev = revisions[0]
    latest_rev_name = latest_rev["name"]
    latest_rev_id = latest_rev_name.rsplit("/", 1)[-1]
    print(
        f"📦 Latest runtimeRevision: {latest_rev_id} "
        f"(state={latest_rev.get('state')}, created={latest_rev.get('createTime')})"
    )

    # 3. Smoke-test the new revision
    smoke_test_revision(args.project, args.location, latest_rev_name)

    # 4. Route 100% traffic to the verified revision
    set_traffic_to_revision(args.project, args.location, engine_name, latest_rev_name)


def cmd_rollback(args: argparse.Namespace) -> None:
    """Rolls back 100% traffic to a target revision ID (or 'previous')."""
    engine = find_reasoning_engine(args.project, args.location, args.agent_name)
    engine_name = engine["name"]
    revisions = list_runtime_revisions(args.project, args.location, engine_name)
    if not revisions:
        raise RuntimeError(f"No runtimeRevisions found under {engine_name}")

    target_arg = args.revision_id.strip()
    if target_arg.lower() == "previous":
        if len(revisions) < 2:
            raise RuntimeError(
                f"Cannot roll back to 'previous': only {len(revisions)} revision exists."
            )
        target_rev_name = revisions[1]["name"]
    else:
        target_rev_name = (
            target_arg
            if target_arg.startswith("projects/")
            else f"{engine_name}/runtimeRevisions/{target_arg}"
        )
        known_names = {r["name"].rsplit("/", 1)[-1]: r["name"] for r in revisions}
        short_id = target_rev_name.rsplit("/", 1)[-1]
        if short_id not in known_names:
            raise RuntimeError(
                f"Revision '{short_id}' not found. Available revisions: {list(known_names.keys())}"
            )
        target_rev_name = known_names[short_id]

    smoke_test_revision(args.project, args.location, target_rev_name)
    set_traffic_to_revision(args.project, args.location, engine_name, target_rev_name)


def cmd_cleanup_legacy(args: argparse.Namespace) -> None:
    """Removes a legacy agent from Gemini Enterprise and deletes its ReasoningEngine."""
    project = args.project
    location = args.location
    legacy_name = args.legacy_agent_name
    ge_app_id = args.gemini_enterprise_app_id

    # 1. Remove matching agent registration(s) from Gemini Enterprise
    if ge_app_id:
        agents_url = (
            f"https://discoveryengine.googleapis.com/v1alpha/{ge_app_id}"
            "/assistants/default_assistant/agents"
        )
        print(f"🔍 Checking Gemini Enterprise agents in {ge_app_id} ...")
        resp = requests.get(agents_url, headers=api_headers(project), timeout=30)
        if resp.status_code == 200:
            for ag in resp.json().get("agents", []):
                ag_name = ag.get("name", "")
                disp = ag.get("displayName", "")
                re_ref = (
                    ag.get("adkAgentDefinition", {})
                    .get("provisionedReasoningEngine", {})
                    .get("reasoningEngine", "")
                )
                if (
                    legacy_name.lower() in disp.lower()
                    or "3002256082060967936" in re_ref
                    or (args.legacy_engine_id and args.legacy_engine_id in re_ref)
                ):
                    print(
                        f"🗑️  Deleting Gemini Enterprise agent: {ag_name} (displayName='{disp}')"
                    )
                    del_resp = requests.delete(
                        f"https://discoveryengine.googleapis.com/v1alpha/{ag_name}",
                        headers=api_headers(project),
                        timeout=30,
                    )
                    del_resp.raise_for_status()
                    print("  ✅ Deleted from Gemini Enterprise.")
        else:
            print(
                f"⚠️  Could not list Gemini Enterprise agents (HTTP {resp.status_code}): {resp.text}"
            )

    # 2. Delete matching ReasoningEngine(s) in Agent Runtime
    base_url = f"https://{location}-aiplatform.googleapis.com/v1beta1"
    re_list_url = f"{base_url}/projects/{project}/locations/{location}/reasoningEngines"
    print(f"🔍 Checking Agent Runtime reasoning engines in {project}/{location} ...")
    re_resp = requests.get(re_list_url, headers=api_headers(project), timeout=30)
    re_resp.raise_for_status()
    for eng in re_resp.json().get("reasoningEngines", []):
        eng_name = eng.get("name", "")
        disp = eng.get("displayName", "")
        if disp == legacy_name or (
            args.legacy_engine_id and eng_name.endswith(f"/{args.legacy_engine_id}")
        ):
            print(f"🗑️  Deleting ReasoningEngine: {eng_name} (displayName='{disp}') ...")
            del_re = requests.delete(
                f"{base_url}/{eng_name}",
                headers=api_headers(project),
                params={"force": "true"},
                timeout=60,
            )
            del_re.raise_for_status()
            op = del_re.json()
            if op.get("name") and not op.get("done", False):
                wait_for_lro(f"{base_url}/{op['name']}", project)
            print(f"  ✅ Deleted ReasoningEngine {eng_name}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage Agent Runtime revisions, traffic routing, and bindings."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # prepare-identity
    p_prep = sub.add_parser(
        "prepare-identity",
        help="Ensure ReasoningEngine shell, Agent Identity IAM roles, and Agent Registry Binding exist before deploy.",
    )
    p_prep.add_argument("--project", required=True)
    p_prep.add_argument("--location", default="europe-west3")
    p_prep.add_argument("--agent-name", default="ag-adk-asana-ticket-inspector")
    p_prep.add_argument("--mcp-service-name", default="asana-mcp")
    p_prep.add_argument("--auth-provider-id", default="asana-oauth-provider")
    p_prep.add_argument("--binding-id", default="asana-mcp-binding")
    p_prep.set_defaults(func=cmd_prepare_identity)

    # list
    p_list = sub.add_parser("list", help="List runtime revisions and traffic config.")
    p_list.add_argument("--project", required=True)
    p_list.add_argument("--location", default="europe-west3")
    p_list.add_argument("--agent-name", default="ag-adk-asana-ticket-inspector")
    p_list.set_defaults(func=cmd_list)

    # verify-and-promote
    p_vp = sub.add_parser(
        "verify-and-promote",
        help="Smoke-test newest revision, shift 100%% traffic to it, and sync bindings.",
    )
    p_vp.add_argument("--project", required=True)
    p_vp.add_argument("--location", default="europe-west3")
    p_vp.add_argument("--agent-name", default="ag-adk-asana-ticket-inspector")
    p_vp.add_argument("--mcp-service-name", default="asana-mcp")
    p_vp.add_argument("--auth-provider-id", default="asana-oauth-provider")
    p_vp.add_argument("--binding-id", default="asana-mcp-binding")
    p_vp.set_defaults(func=cmd_verify_and_promote)

    # rollback
    p_rb = sub.add_parser(
        "rollback",
        help="Roll back 100%% traffic to a specific revision ID or 'previous'.",
    )
    p_rb.add_argument("--project", required=True)
    p_rb.add_argument("--location", default="europe-west3")
    p_rb.add_argument("--agent-name", default="ag-adk-asana-ticket-inspector")
    p_rb.add_argument(
        "--revision-id",
        required=True,
        help="Target runtimeRevision ID (or 'previous' for the prior revision).",
    )
    p_rb.set_defaults(func=cmd_rollback)

    # cleanup-legacy
    p_cl = sub.add_parser(
        "cleanup-legacy",
        help="Remove legacy agent from Gemini Enterprise and Agent Runtime.",
    )
    p_cl.add_argument("--project", required=True)
    p_cl.add_argument("--location", default="europe-west3")
    p_cl.add_argument("--legacy-agent-name", default="asana-mcp")
    p_cl.add_argument("--legacy-engine-id", default="3002256082060967936")
    p_cl.add_argument("--gemini-enterprise-app-id", default="")
    p_cl.set_defaults(func=cmd_cleanup_legacy)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        sys.exit(1)
