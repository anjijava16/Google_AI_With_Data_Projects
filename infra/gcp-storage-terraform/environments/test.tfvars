project_id  = "my-gcp-project-test"
region      = "us-central1"
environment = "test"

bucket_name   = "app-data"
location      = "US"
storage_class = "STANDARD"

force_destroy               = true
versioning_enabled          = true
uniform_bucket_level_access = true
lifecycle_age_days          = 60

labels = {
  team = "data"
}
