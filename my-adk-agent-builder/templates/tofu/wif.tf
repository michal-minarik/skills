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

# ------------------------------------------------------------------------------
# 1. Shared Workload Identity Pool & GitHub OIDC Provider (org-scoped)
# ------------------------------------------------------------------------------

resource "google_iam_workload_identity_pool" "github_pool" {
  project                   = var.project_id
  workload_identity_pool_id = var.wif_pool_id
  display_name              = "GitHub Actions Pool"
  description               = "Shared Workload Identity Pool for GitHub Actions (${var.github_org})"
  depends_on                = [google_project_service.apis]
}

resource "google_iam_workload_identity_pool_provider" "github_provider" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = var.wif_provider_id
  display_name                       = "GitHub Actions OIDC"
  description                        = "OIDC provider for GitHub Actions in organization ${var.github_org}"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.actor"            = "assertion.actor"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
    "attribute.ref"              = "assertion.ref"
  }

  # Restrict pool provider trust to repositories owned by the GitHub org.
  attribute_condition = "attribute.repository_owner == '${var.github_org}'"
}

# ------------------------------------------------------------------------------
# 2. Dedicated CI/CD Service Account & IAM Permissions
# ------------------------------------------------------------------------------

resource "google_service_account" "cicd_sa" {
  project      = var.project_id
  account_id   = var.cicd_sa_account_id
  display_name = "CI/CD Deployer for ${var.agent_name}"
  description  = "Service account impersonated by GitHub Actions (${var.github_org}/${var.github_repo}) via WIF"
  depends_on   = [google_project_service.apis]
}

locals {
  cicd_sa_roles = [
    # Deploy & manage Agent Runtime reasoning engines, revisions, and traffic splits
    "roles/aiplatform.admin",
    # Grant IAM bindings to the agent's dynamic Agent Identity principal
    "roles/resourcemanager.projectIamAdmin",
    # Discover MCP servers and manage Agent Registry bindings
    "roles/agentregistry.admin",
    # Register and update the agent in Gemini Enterprise
    "roles/discoveryengine.admin",
    # Stage source archives and build containers during Agent Runtime deployment
    "roles/storage.admin",
    "roles/cloudbuild.builds.editor",
    "roles/artifactregistry.writer",
    # Reference Secret Manager secrets during deployment
    "roles/secretmanager.viewer",
    "roles/secretmanager.secretAccessor",
    # General service usage & logging
    "roles/serviceusage.serviceUsageConsumer",
    "roles/logging.viewer",
    "roles/iam.serviceAccountUser",
  ]

  repo_principal_set = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_org}/${var.github_repo}"
}

resource "google_project_iam_member" "cicd_sa_roles" {
  for_each = toset(local.cicd_sa_roles)
  project  = var.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.cicd_sa.email}"
}

# Allow the GitHub repository (and only this repository) to impersonate cicd_sa
resource "google_service_account_iam_member" "github_wif_user" {
  service_account_id = google_service_account.cicd_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = local.repo_principal_set
}

resource "google_service_account_iam_member" "github_wif_token_creator" {
  service_account_id = google_service_account.cicd_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = local.repo_principal_set
}

# Allow the Agent Runtime platform service agent to mount Secret Manager secrets
resource "google_project_iam_member" "agent_runtime_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-aiplatform-re.iam.gserviceaccount.com"
}

