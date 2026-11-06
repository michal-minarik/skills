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

variable "project_id" {
  type        = string
  description = "Google Cloud Project ID (single environment)."
}

variable "region" {
  type        = string
  description = "Google Cloud region for Agent Runtime and Agent Registry."
  default     = "europe-west3"
}

variable "github_org" {
  type        = string
  description = "GitHub organization or owner."
  default     = "cloud-gtm"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository name."
  default     = "ag-adk-asana-ticket-inspector"
}

variable "wif_pool_id" {
  type        = string
  description = "Workload Identity Pool ID (shared across the project)."
  default     = "github-actions-pool"
}

variable "wif_provider_id" {
  type        = string
  description = "Workload Identity Pool OIDC Provider ID."
  default     = "github-oidc"
}

variable "cicd_sa_account_id" {
  type        = string
  description = "Account ID (prefix) for the CI/CD deployer service account."
  default     = "ag-adk-asana-inspector-cicd"
}

variable "agent_name" {
  type        = string
  description = "Agent Runtime service name."
  default     = "ag-adk-asana-ticket-inspector"
}

variable "agent_display_name" {
  type        = string
  description = "Display name when registered in Gemini Enterprise."
  default     = "Asana Ticket Inspector"
}

variable "gemini_enterprise_app_id" {
  type        = string
  description = "Full resource name of the Gemini Enterprise app (engine)."
}

variable "asana_mcp_service_name" {
  type        = string
  description = "Agent Registry service name for the Asana MCP server."
  default     = "asana-mcp"
}

variable "asana_auth_provider_id" {
  type        = string
  description = "Agent Identity AuthProvider ID for Asana 3LO."
  default     = "asana-oauth-provider"
}

variable "asana_binding_id" {
  type        = string
  description = "Agent Registry AuthProvider Binding ID."
  default     = "asana-mcp-binding"
}

variable "default_workspace_gid" {
  type        = string
  description = "Default Asana Workspace GID."
  default     = "1218490684103740"
}

variable "default_project_gid" {
  type        = string
  description = "Default Asana Project GID (ACME - Tasks)."
  default     = "1218498290315548"
}
