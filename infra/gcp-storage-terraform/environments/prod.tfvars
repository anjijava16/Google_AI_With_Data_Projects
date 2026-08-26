project_id  = "my-gcp-project-prod"
region      = "us-central1"
environment = "prod"

bucket_name   = "app-data"
location      = "US"
storage_class = "STANDARD"

force_destroy               = false
versioning_enabled          = true
uniform_bucket_level_access = true
lifecycle_age_days          = 0

labels = {
  team = "data"
}
