terraform {
  required_version = ">= 1.6.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ---------------------------------------------------------
# Enable required APIs
# ---------------------------------------------------------

locals {
  services = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
  ]
}

resource "google_project_service" "enabled" {
  for_each = toset(local.services)
  project  = var.project_id
  service  = each.value

  disable_on_destroy = false
}

# ---------------------------------------------------------
# Artifact Registry (Docker) repository
# ---------------------------------------------------------

resource "google_artifact_registry_repository" "fastapi" {
  location      = var.region
  repository_id = var.repo_id
  format        = "DOCKER"
  description   = "FastAPI images"

  depends_on = [google_project_service.enabled]
}

# ---------------------------------------------------------
# Cloud Run Service
# ---------------------------------------------------------

resource "google_cloud_run_v2_service" "fastapi" {
  name     = var.service_name
  location = var.region

  deletion_protection = false

  template {
    containers {
      image = var.image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 3
    }
  }

  depends_on = [google_project_service.enabled]
}

# ---------------------------------------------------------
# Allow public access to Cloud Run
# ---------------------------------------------------------

resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.fastapi.name
  location = google_cloud_run_v2_service.fastapi.location
  project  = var.project_id

  role   = "roles/run.invoker"
  member = "allUsers"
}