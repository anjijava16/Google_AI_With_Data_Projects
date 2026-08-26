#!/usr/bin/env bash
# One-time project setup. Run before terraform.
set -euo pipefail

PROJECT_ID="${1:?usage: bootstrap.sh PROJECT_ID [REGION]}"
REGION="${2:-us-central1}"

echo "==> Setting project"
gcloud config set project "$PROJECT_ID"
gcloud config set compute/region "$REGION"

echo "==> Application Default Credentials"
# The gcloud equivalent of `aws configure`. Note there are TWO logins in GCP:
#   gcloud auth login                      -> for the gcloud CLI itself
#   gcloud auth application-default login  -> for client libraries in your code
# Doing only the first and wondering why Python can't authenticate is a rite
# of passage. Do both.
gcloud auth login
gcloud auth application-default login

echo "==> Enabling the APIs terraform itself needs"
gcloud services enable \
  cloudresourcemanager.googleapis.com \
  serviceusage.googleapis.com \
  iam.googleapis.com

echo "==> Terraform state bucket"
BUCKET="${PROJECT_ID}-tfstate"
if ! gcloud storage buckets describe "gs://${BUCKET}" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://${BUCKET}" --location="$REGION"
  gcloud storage buckets update "gs://${BUCKET}" --versioning
fi

echo
echo "Done. Next:"
echo "  cd terraform && terraform init && terraform apply -var project_id=${PROJECT_ID}"
