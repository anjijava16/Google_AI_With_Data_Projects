resource "google_bigquery_dataset" "this" {
  project     = var.project_id
  dataset_id  = var.dataset_id
  location    = var.dataset_location
  description = "Dataset for ${var.environment} managed by Terraform."

  labels = local.common_labels
}

resource "google_bigquery_table" "this" {
  project             = var.project_id
  dataset_id          = google_bigquery_dataset.this.dataset_id
  table_id            = var.table_id
  deletion_protection = var.table_deletion_protection

  time_partitioning {
    type  = "DAY"
    field = "created_at"
  }

  schema = jsonencode([
    {
      name        = "id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique identifier for the record."
    },
    {
      name        = "name"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Display name."
    },
    {
      name        = "amount"
      type        = "NUMERIC"
      mode        = "NULLABLE"
      description = "Monetary amount."
    },
    {
      name        = "created_at"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Record creation timestamp (partition column)."
    }
  ])

  labels = local.common_labels
}
