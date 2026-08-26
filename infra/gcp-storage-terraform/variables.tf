variable "project_id" {
  description = "The GCP project ID where resources are created."
  type        = string
}

variable "region" {
  description = "The default GCP region for resources."
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

variable "bucket_name" {
  description = "Base name for the Cloud Storage bucket. A random suffix is appended for global uniqueness."
  type        = string
}

variable "location" {
  description = "Location of the Cloud Storage bucket (region or multi-region)."
  type        = string
  default     = "US"
}

variable "storage_class" {
  description = "Storage class for the bucket."
  type        = string
  default     = "STANDARD"

  validation {
    condition     = contains(["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"], var.storage_class)
    error_message = "storage_class must be one of: STANDARD, NEARLINE, COLDLINE, ARCHIVE."
  }
}

variable "force_destroy" {
  description = "When true, allows Terraform to destroy the bucket even if it contains objects."
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "Enable object versioning on the bucket."
  type        = bool
  default     = true
}

variable "uniform_bucket_level_access" {
  description = "Enable uniform bucket-level access (disables object ACLs)."
  type        = bool
  default     = true
}

variable "lifecycle_age_days" {
  description = "Age in days after which objects are deleted. Set to 0 to disable the lifecycle rule."
  type        = number
  default     = 0
}

variable "labels" {
  description = "Additional labels to apply to the bucket."
  type        = map(string)
  default     = {}
}
