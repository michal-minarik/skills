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

terraform {
  required_version = ">= 1.6.0"

  # State is stored in GCS (configured via backend.hcl or -backend-config):
  #   tofu init -backend-config=backend.hcl
  backend "gcs" {}

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    github = {
      source  = "integrations/github"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project               = var.project_id
  region                = var.region
  user_project_override = true
  billing_project       = var.project_id
}

# Used strictly for enabling Service Usage & Cloud Resource Manager before
# billing_project override can be evaluated.
provider "google" {
  alias  = "bootstrap"
  region = var.region
}

provider "github" {
  owner = var.github_org
}

locals {
  bootstrap_apis = [
    "serviceusage.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ]

  project_apis = [
    "aiplatform.googleapis.com",
    "agentregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudtrace.googleapis.com",
    "discoveryengine.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "logging.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com",
    "sts.googleapis.com",
  ]
}

resource "google_project_service" "bootstrap" {
  provider           = google.bootstrap
  for_each           = toset(local.bootstrap_apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_project_service" "apis" {
  for_each           = toset(local.project_apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
  depends_on         = [google_project_service.bootstrap]
}

data "google_project" "current" {
  project_id = var.project_id
  depends_on = [google_project_service.bootstrap]
}
