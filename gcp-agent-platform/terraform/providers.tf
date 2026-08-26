terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
  # Remote state. GCS needs no DynamoDB equivalent — object generation numbers
  # give you locking for free, which is one fewer resource than the S3 setup.
  # backend "gcs" {
  #   bucket = "REPLACE-tfstate"
  #   prefix = "dia"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}
