resource "google_cloud_run_v2_service" "api" {
  name     = "${var.name_prefix}-api"
  location = var.region
  deletion_protection = false
  # Private by default. Put a load balancer or IAP in front rather than
  # allowing unauthenticated access.
  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.agent.email

    scaling {
      min_instance_count = 0 # scale to zero; raise to 1 if cold start hurts
      max_instance_count = 10
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.containers.repository_id}/dia-api:latest"

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi" # docling is memory-hungry; do not start at 512Mi
        }
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }
      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "TRUE"
      }
      env {
        name  = "BQ_DATASET"
        value = var.bq_dataset
      }
      env {
        name  = "USE_MANAGED_SESSIONS"
        value = "true"
      }
      env {
        name  = "RAW_BUCKET"
        value = google_storage_bucket.raw.name
      }

      startup_probe {
        http_get { path = "/healthz" }
        initial_delay_seconds = 10
        timeout_seconds       = 5
        failure_threshold     = 6
      }
    }

    # Agent turns are long. The default 5 minutes will cut streaming responses.
    timeout = "900s"
  }

  lifecycle {
    # CI pushes new image tags; do not let terraform revert them
    ignore_changes = [template[0].containers[0].image]
  }
}
