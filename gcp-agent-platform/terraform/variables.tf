variable "project_id" {
  type        = string
  description = "GCP project ID. Closest AWS analogue is an account, but far cheaper to create."
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "name_prefix" {
  type    = string
  default = "dia"
}

variable "bq_dataset" {
  type    = string
  default = "dia_analytics"
}
