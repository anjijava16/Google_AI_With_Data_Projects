variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region"
  type        = string
  default     = "us-east1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "fastapi-hello"
}

variable "repo_id" {
  description = "Artifact Registry repository ID"
  type        = string
  default     = "fastapi-repo"
}

variable "image" {
  description = "Docker image URI to deploy (e.g. REGION-docker.pkg.dev/PROJECT/REPO/hello-api:v1)"
  type        = string
}