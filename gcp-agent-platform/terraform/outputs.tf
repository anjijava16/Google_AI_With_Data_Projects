output "raw_bucket" { value = "gs://${google_storage_bucket.raw.name}" }
output "staging_bucket" { value = "gs://${google_storage_bucket.staging.name}" }
output "agent_service_account" { value = google_service_account.agent.email }
output "artifact_repo" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.containers.repository_id}"
}
output "approvals_topic" { value = google_pubsub_topic.approvals.name }

output "env_exports" {
  description = "Paste into your shell after apply"
  value       = <<-EOT
    export GOOGLE_CLOUD_PROJECT=${var.project_id}
    export GOOGLE_CLOUD_LOCATION=${var.region}
    export RAW_BUCKET=${google_storage_bucket.raw.name}
    export STAGING_BUCKET=gs://${google_storage_bucket.staging.name}
    export BQ_DATASET=${var.bq_dataset}
    export HITL_TOPIC=${google_pubsub_topic.approvals.name}
  EOT
}
