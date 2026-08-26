resource "google_storage_bucket" "this" {
  name          = local.bucket_full_name
  project       = var.project_id
  location      = var.location
  storage_class = var.storage_class
  force_destroy = var.force_destroy

  uniform_bucket_level_access = var.uniform_bucket_level_access

  versioning {
    enabled = var.versioning_enabled
  }

  dynamic "lifecycle_rule" {
    for_each = var.lifecycle_age_days > 0 ? [1] : []

    content {
      action {
        type = "Delete"
      }
      condition {
        age = var.lifecycle_age_days
      }
    }
  }

  labels = local.common_labels
}
