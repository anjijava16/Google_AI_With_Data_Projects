# GCP Cloud Storage – Terraform

Terraform configuration to provision a Google Cloud Storage (GCS) bucket with
per-environment settings (`dev`, `test`, `prod`). The bucket name is made
globally unique by appending a random suffix.

## Contents

```
gcp-storage-terraform/
├── versions.tf      # Terraform + provider version constraints
├── provider.tf      # google provider configuration
├── main.tf          # google_storage_bucket resource
├── variables.tf     # input variables (with validation)
├── outputs.tf       # bucket name, url, self_link, location
├── locals.tf        # computed bucket name + common labels
├── random.tf        # random_id suffix for bucket uniqueness
└── environments/
    ├── dev.tfvars
    ├── test.tfvars
    └── prod.tfvars
```

## What gets created

- A `google_storage_bucket` named `<bucket_name>-<environment>-<random_hex>`.
- Optional object versioning.
- Uniform bucket-level access (recommended, enabled by default).
- An optional lifecycle rule that deletes objects after `lifecycle_age_days`
  (set to `0` to disable).
- Labels: `environment`, `managed_by = terraform`, plus any custom `labels`.

## Input variables

| Variable                      | Type          | Default         | Description                                                        |
| ----------------------------- | ------------- | --------------- | ------------------------------------------------------------------ |
| `project_id`                  | `string`      | —               | GCP project ID (required).                                         |
| `region`                      | `string`      | `us-central1`   | Default region for the provider.                                   |
| `environment`                 | `string`      | —               | One of `dev`, `test`, `prod` (required).                           |
| `bucket_name`                 | `string`      | —               | Base name; random suffix is appended (required).                   |
| `location`                    | `string`      | `US`            | Bucket location (region or multi-region).                          |
| `storage_class`               | `string`      | `STANDARD`      | `STANDARD`, `NEARLINE`, `COLDLINE`, or `ARCHIVE`.                   |
| `force_destroy`               | `bool`        | `false`         | Allow destroying a non-empty bucket.                               |
| `versioning_enabled`          | `bool`        | `true`          | Enable object versioning.                                          |
| `uniform_bucket_level_access` | `bool`        | `true`          | Enable uniform bucket-level access (disables object ACLs).         |
| `lifecycle_age_days`          | `number`      | `0`             | Delete objects after N days. `0` disables the rule.                |
| `labels`                      | `map(string)` | `{}`            | Additional labels to merge onto the bucket.                        |

## Outputs

| Output             | Description                          |
| ------------------ | ------------------------------------ |
| `bucket_name`      | Name of the created bucket.          |
| `bucket_url`       | `gs://` URL of the bucket.           |
| `bucket_self_link` | URI of the bucket.                   |
| `bucket_location`  | Location of the bucket.              |

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.5.0
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- A GCP project with billing enabled and the Cloud Storage API enabled.

## 1. Authenticate to Google Cloud

```bash
# Sign in and select the account
gcloud auth login
gcloud config set account mamathaanjireddy@gmail.com

# Set the target project
gcloud config set project project-52e8c95d-822f-4563-a7e

# Application Default Credentials used by Terraform
gcloud auth application-default login

# (Optional) environment used by the app / Vertex AI clients
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

Enable the Cloud Storage API if it is not already enabled:

```bash
gcloud services enable storage.googleapis.com
```

## 2. Configure your environment values

Edit the relevant file in `environments/`. Example — `environments/dev.tfvars`:

```hcl
project_id  = "project-52e8c95d-822f-4563-a7e"
region      = "us-central1"
environment = "dev"

bucket_name   = "iwinner-google-data-ai"
location      = "US"
storage_class = "STANDARD"

force_destroy               = true
versioning_enabled          = false
uniform_bucket_level_access = true
lifecycle_age_days          = 300

labels = {
  team = "data"
}
```

## 3. Run Terraform (end-to-end)

From this directory (`infra/gcp-storage-terraform`):

```bash
# Initialize providers and modules
terraform init

# Format and validate
terraform fmt
terraform validate

# Preview changes for an environment
terraform plan -var-file=environments/dev.tfvars

# Apply the changes
terraform apply -var-file=environments/dev.tfvars

# View outputs (e.g. the generated bucket name)
terraform output
```

Switch environments by changing the `-var-file`:

```bash
terraform plan  -var-file=environments/test.tfvars
terraform apply -var-file=environments/prod.tfvars
```

## 4. Verify the bucket

```bash
# List buckets in the project
gcloud storage buckets list --project project-52e8c95d-822f-4563-a7e

# Describe the created bucket (name comes from `terraform output bucket_name`)
gcloud storage buckets describe gs://$(terraform output -raw bucket_name)
```

## 5. Destroy (tear down)

```bash
terraform destroy -var-file=environments/dev.tfvars
```

> If the bucket contains objects, destroy only succeeds when
> `force_destroy = true` for that environment.

## Managing multiple environments safely

Each environment should use its own state. The simplest option is Terraform
workspaces:

```bash
terraform workspace new dev
terraform workspace select dev
terraform apply -var-file=environments/dev.tfvars
```

For team use, configure a remote backend (GCS) so state is shared and locked.
Create `backend.tf`:

```hcl
terraform {
  backend "gcs" {
    bucket = "my-terraform-state-bucket"   # must already exist
    prefix = "gcp-storage-terraform"
  }
}
```

Then re-run `terraform init` to migrate state.

## Notes

- Bucket names are globally unique across all of GCP; the random suffix in
  `locals.tf` helps avoid collisions.
- `force_destroy = true` is convenient for `dev`/`test` but should stay `false`
  for `prod` to avoid accidental data loss.
