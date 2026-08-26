# GCP BigQuery – Terraform

Terraform configuration to provision a Google BigQuery **dataset** and **table**
with per-environment settings (`dev`, `test`, `prod`).

## Contents

```
bigquery-terraform/
├── versions.tf      # Terraform + provider version constraints
├── provider.tf      # google provider configuration
├── main.tf          # bigquery_dataset + bigquery_table (with schema)
├── variables.tf     # input variables (with validation)
├── outputs.tf       # dataset_id, table_id, table_reference
├── locals.tf        # common labels
└── environments/
    ├── dev.tfvars
    ├── test.tfvars
    └── prod.tfvars
```

## What gets created

- A `google_bigquery_dataset`.
- A `google_bigquery_table` named by `table_id`, day-partitioned on
  `created_at`, with this starter schema:

  | Column       | Type      | Mode     | Description                          |
  | ------------ | --------- | -------- | ------------------------------------ |
  | `id`         | STRING    | REQUIRED | Unique identifier for the record.    |
  | `name`       | STRING    | NULLABLE | Display name.                        |
  | `amount`     | NUMERIC   | NULLABLE | Monetary amount.                     |
  | `created_at` | TIMESTAMP | REQUIRED | Creation timestamp (partition col).  |

- Labels: `environment`, `managed_by = terraform`, plus any custom `labels`.

## Input variables

| Variable                    | Type          | Default       | Description                                             |
| --------------------------- | ------------- | ------------- | ------------------------------------------------------- |
| `project_id`                | `string`      | —             | GCP project ID (required).                              |
| `region`                    | `string`      | `us-central1` | Default region for the provider.                        |
| `environment`               | `string`      | —             | One of `dev`, `test`, `prod` (required).                |
| `dataset_id`                | `string`      | —             | Dataset ID (letters, numbers, underscores only).        |
| `dataset_location`          | `string`      | `US`          | Dataset location (e.g. `US`, `EU`, `us-central1`).      |
| `table_id`                  | `string`      | —             | Table ID (required).                                    |
| `table_deletion_protection` | `bool`        | `true`        | Prevent Terraform from destroying the table.            |
| `labels`                    | `map(string)` | `{}`          | Additional labels merged onto dataset and table.        |

## Outputs

| Output              | Description                                     |
| ------------------- | ----------------------------------------------- |
| `dataset_id`        | ID of the created dataset.                      |
| `dataset_self_link` | URI of the dataset.                             |
| `table_id`          | ID of the created table.                        |
| `table_reference`   | Fully qualified `project.dataset.table` string. |

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.5.0
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud`)
- A GCP project with billing enabled.

## 1. Authenticate to Google Cloud

```bash
gcloud auth login
gcloud config set account mamathaanjireddy@gmail.com
gcloud config set project project-52e8c95d-822f-4563-a7e

# Application Default Credentials used by Terraform
gcloud auth application-default login

# Enable the BigQuery API
gcloud services enable bigquery.googleapis.com
```

## 2. Configure your environment values

Edit the relevant file in `environments/`. Example — `environments/dev.tfvars`:

```hcl
project_id  = "project-52e8c95d-822f-4563-a7e"
region      = "us-central1"
environment = "dev"

dataset_id       = "iwinner_google_data_ai_dev"
dataset_location = "US"

table_id                  = "events"
table_deletion_protection = false

labels = {
  team = "data"
}
```

> BigQuery dataset IDs allow only letters, numbers, and underscores — no hyphens.

## 3. Run Terraform (end-to-end)

From this directory (`infra/bigquery-terraform`):

```bash
# Initialize providers
terraform init

# Format and validate
terraform fmt
terraform validate

# Preview changes for an environment
terraform plan -var-file=environments/dev.tfvars

# Apply the changes
terraform apply -var-file=environments/dev.tfvars

# View outputs (e.g. fully qualified table reference)
terraform output
```

Switch environments by changing the `-var-file`:

```bash
terraform plan  -var-file=environments/test.tfvars
terraform apply -var-file=environments/prod.tfvars
```

## 4. Verify

```bash
# List datasets in the project
bq ls --project_id project-52e8c95d-822f-4563-a7e

# Show table schema
bq show --schema --format=prettyjson \
  project-52e8c95d-822f-4563-a7e:iwinner_google_data_ai_dev.events
```

## 5. Destroy (tear down)

```bash
terraform destroy -var-file=environments/dev.tfvars
```

> Destroying a table requires `table_deletion_protection = false` for that
> environment (it is `true` for `prod` by default).

## Customizing the table schema

Edit the `schema = jsonencode([...])` block in `main.tf` to match your columns.
Each field supports `name`, `type`, `mode`, and `description`. Adjust or remove
the `time_partitioning` block if you don't need day-based partitioning.

## Managing multiple environments safely

Use Terraform workspaces so each environment has isolated state:

```bash
terraform workspace new dev
terraform workspace select dev
terraform apply -var-file=environments/dev.tfvars
```

For team use, configure a remote GCS backend so state is shared and locked.

## Notes

- `table_deletion_protection = true` (prod) guards against accidental drops.
- Dataset location is immutable — choose it carefully up front.
