# One service account per role, least privilege each. The GCP model differs from
# AWS in a way that matters: there is no resource-policy side. You grant a
# principal a role ON a resource. No bucket policy vs IAM policy split, no
# "which one wins" puzzle — but also no way to let another account in from the
# resource side alone.

resource "google_service_account" "agent" {
  account_id   = "${var.name_prefix}-agent"
  display_name = "DIA agent runtime identity"
}

resource "google_service_account" "ingest" {
  account_id   = "${var.name_prefix}-ingest"
  display_name = "DIA ingestion pipeline identity"
}

# --- agent: read data, call models, never write ------------------------------
resource "google_project_iam_member" "agent_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_bigquery_dataset_iam_member" "agent_bq_read" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.agent.email}"
}

# dataViewer alone cannot run a query — you also need job-creation at project
# level. Splitting read from execute like this is a GCP-ism with no clean AWS
# parallel, and a frequent source of confusing 403s.
resource "google_project_iam_member" "agent_bq_jobs" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_storage_bucket_iam_member" "agent_raw_read" {
  bucket = google_storage_bucket.raw.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_project_iam_member" "agent_trace" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.agent.email}"
}

resource "google_pubsub_topic" "approvals" {
  name       = "${var.name_prefix}-approvals"
  depends_on = [google_project_service.enabled]
}

resource "google_pubsub_topic_iam_member" "agent_publish" {
  topic  = google_pubsub_topic.approvals.name
  role   = "roles/pubsub.publisher"
  member = "serviceAccount:${google_service_account.agent.email}"
}

# --- ingestion: write to raw, load BigQuery, no model access -----------------
resource "google_storage_bucket_iam_member" "ingest_raw_write" {
  bucket = google_storage_bucket.raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.ingest.email}"
}

resource "google_bigquery_dataset_iam_member" "ingest_bq_write" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.ingest.email}"
}
