resource "google_storage_bucket" "raw" {
  name                        = "${var.project_id}-${var.name_prefix}-raw"
  location                    = var.region
  uniform_bucket_level_access = true # the GCS equivalent of "block public access + no object ACLs"
  force_destroy               = false

  versioning { enabled = true }

  lifecycle_rule {
    condition { age = 90 }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  depends_on = [google_project_service.enabled]
}

resource "google_storage_bucket" "staging" {
  name                        = "${var.project_id}-${var.name_prefix}-staging"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  # Agent Runtime deployment artifacts. They accumulate; clean them up.
  lifecycle_rule {
    condition { age = 30 }
    action { type = "Delete" }
  }

  depends_on = [google_project_service.enabled]
}
