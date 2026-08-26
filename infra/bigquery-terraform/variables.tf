variable "project_id" {
  description = "The GCP project ID where BigQuery resources are created."
  type        = string
}

variable "region" {
  description = "The default GCP region for the provider."
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Deployment environment (e.g. dev, test, prod)."
  type        = string

  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "environment must be one of: dev, test, prod."
  }
}

variable "dataset_id" {
  description = "The BigQuery dataset ID (letters, numbers, and underscores only)."
  type        = string
}

variable "dataset_location" {
  description = "Location of the BigQuery dataset (e.g. US, EU, us-central1)."
  type        = string
  default     = "US"
}

variable "table_id" {
  description = "The BigQuery table ID."
  type        = string
}

variable "table_deletion_protection" {
  description = "Protect the table from being destroyed by Terraform."
  type        = bool
  default     = true
}

variable "labels" {
  description = "Additional labels to apply to the dataset and table."
  type        = map(string)
  default     = {}
}
