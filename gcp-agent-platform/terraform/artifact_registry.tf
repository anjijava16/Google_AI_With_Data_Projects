resource "google_artifact_registry_repository" "containers" {
  location      = var.region
  repository_id = "${var.name_prefix}-repo"
  format        = "DOCKER"
  description   = "Container images for DIA services"
  depends_on    = [google_project_service.enabled]
}
