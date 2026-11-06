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
# GitHub Actions Secrets & Variables (populated automatically on the repository)
# ------------------------------------------------------------------------------

data "github_repository" "repo" {
  full_name = "${var.github_org}/${var.github_repo}"
}

resource "github_actions_secret" "wif_provider" {
  repository      = data.github_repository.repo.name
  secret_name     = "WIF_PROVIDER"
  plaintext_value = google_iam_workload_identity_pool_provider.github_provider.name
}

resource "github_actions_secret" "gcp_service_account" {
  repository      = data.github_repository.repo.name
  secret_name     = "GCP_SERVICE_ACCOUNT"
  plaintext_value = google_service_account.cicd_sa.email
}

locals {
  github_variables = {
    GCP_PROJECT_ID           = var.project_id
    GCP_PROJECT_NUMBER       = tostring(data.google_project.current.number)
    GCP_REGION               = var.region
    AGENT_NAME               = var.agent_name
    AGENT_DISPLAY_NAME       = var.agent_display_name
    GEMINI_ENTERPRISE_APP_ID = var.gemini_enterprise_app_id
    ASANA_MCP_SERVICE_NAME   = var.asana_mcp_service_name
    ASANA_AUTH_PROVIDER_ID   = var.asana_auth_provider_id
    ASANA_BINDING_ID         = var.asana_binding_id
    DEFAULT_WORKSPACE_GID    = var.default_workspace_gid
    DEFAULT_PROJECT_GID      = var.default_project_gid
  }
}

resource "github_actions_variable" "vars" {
  for_each      = local.github_variables
  repository    = data.github_repository.repo.name
  variable_name = each.key
  value         = each.value
}
