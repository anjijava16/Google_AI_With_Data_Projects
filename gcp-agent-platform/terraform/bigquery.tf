resource "google_bigquery_dataset" "analytics" {
  dataset_id                 = var.bq_dataset
  location                   = var.region
  delete_contents_on_destroy = false
  depends_on                 = [google_project_service.enabled]
}

# Partitioning is the single biggest cost lever in BigQuery, and the reason the
# SQL agent's guardrail tells the model to filter on partition columns.
resource "google_bigquery_table" "contract_events" {
  dataset_id          = google_bigquery_dataset.analytics.dataset_id
  table_id            = "contract_events"
  deletion_protection = true

  time_partitioning {
    type  = "DAY"
    field = "event_date"
  }
  clustering = ["counterparty", "event_type"]

  schema = jsonencode([
    { name = "event_date", type = "DATE", mode = "REQUIRED", description = "Partition column. Always filter on this." },
    { name = "contract_uri", type = "STRING", mode = "REQUIRED", description = "GCS URI of the source contract" },
    { name = "counterparty", type = "STRING", mode = "NULLABLE" },
    { name = "event_type", type = "STRING", mode = "NULLABLE", description = "signed | renewed | terminated | amended" },
    { name = "amount_usd", type = "NUMERIC", mode = "NULLABLE" },
  ])
}
