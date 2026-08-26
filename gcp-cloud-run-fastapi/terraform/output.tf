output "cloud_run_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.fastapi.uri
}

output "cloud_run_service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.fastapi.name
}

output "cloud_run_region" {
  description = "Cloud Run deployment region"
  value       = google_cloud_run_v2_service.fastapi.location
}