# APIs are disabled by default in a new GCP project and every call fails with a
# 403 until enabled. There is no AWS equivalent of this step — the single most
# common thing that trips up people coming from AWS.
locals {
  services = [
    "aiplatform.googleapis.com",       # Agent Platform / Gemini / RAG Engine
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "documentai.googleapis.com",
    "pubsub.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ]
}

resource "google_project_service" "enabled" {
  for_each                   = toset(local.services)
  service                    = each.value
  disable_dependent_services = false
  disable_on_destroy         = false
}
