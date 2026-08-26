output "dataset_id" {
  description = "The ID of the created BigQuery dataset."
  value       = google_bigquery_dataset.this.dataset_id
}

output "dataset_self_link" {
  description = "The URI of the created dataset."
  value       = google_bigquery_dataset.this.self_link
}

output "table_id" {
  description = "The ID of the created BigQuery table."
  value       = google_bigquery_table.this.table_id
}

output "table_reference" {
  description = "Fully qualified table reference (project.dataset.table)."
  value       = "${var.project_id}.${google_bigquery_dataset.this.dataset_id}.${google_bigquery_table.this.table_id}"
}
