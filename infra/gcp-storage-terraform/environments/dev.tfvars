project_id  = "project-52e8c95d-822f-4563-a7e"
region      = "us-central1"
environment = "dev"

bucket_name   = "iwinner-gcpadk-data-ai"
location      = "US"
storage_class = "STANDARD"

force_destroy               = true
versioning_enabled          = false
uniform_bucket_level_access = true
lifecycle_age_days          = 300

labels = {
  team = "data"
}
