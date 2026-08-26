# FastAPI on Google Cloud Run — Terraform Deploy

A minimal FastAPI service containerized with Docker, pushed to Artifact
Registry, and deployed to **Cloud Run** using **Terraform**. Terraform manages
the APIs, the Artifact Registry repository, and the Cloud Run service.

## Contents

```
gcp-cloud-run-fastapi/
├── Dockerfile
├── requirements.txt
├── app/
│   └── main.py            # FastAPI app: GET / and GET /health
└── terraform/
    ├── main.tf            # APIs + Artifact Registry + Cloud Run v2 + public IAM
    ├── variables.tf       # project_id, region, service_name, repo_id, image
    ├── terraform.tfvars   # your values
    └── output.tf          # service URL, name, region
```

## The app

| Route      | Method | Response                                             |
| ---------- | ------ | ---------------------------------------------------- |
| `/`        | GET    | `{"message": "Hello World", "service": "..."}`       |
| `/health`  | GET    | `{"status": "healthy"}`                              |

The container listens on `8080` (Cloud Run's default `PORT`).

## What Terraform creates

- `google_project_service.enabled` — enables `run`, `artifactregistry`, and
  `cloudbuild` APIs.
- `google_artifact_registry_repository.fastapi` — the Docker repo (`fastapi-repo`).
- `google_cloud_run_v2_service.fastapi` — the Cloud Run service (0–3 instances,
  1 vCPU / 512Mi).
- `google_cloud_run_v2_service_iam_member.public` — grants `roles/run.invoker`
  to `allUsers` (public endpoint).

## Prerequisites

- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Docker](https://docs.docker.com/get-docker/) (only if building locally)
- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.6.0
- A GCP project with billing enabled.

Set shell variables used throughout:

```bash
export PROJECT_ID="project-52e8c95d-822f-4563-a7e"
export REGION="us-east1"
export REPO="fastapi-repo"
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/hello-api:v1"
```

## 1. Authenticate & select the project

```bash
gcloud auth login
gcloud config set project "$PROJECT_ID"
gcloud auth application-default login
```

## The deploy order (important)

There is a chicken-and-egg dependency:

```
create APIs + repo (Terraform)  →  build & push image (you / Cloud Build)  →  deploy Cloud Run (Terraform)
```

Terraform **cannot build the Docker image** — it only references the image tag.
So the flow is a two-step apply.

## 2. Create the APIs + Artifact Registry repo (Terraform)

```bash
cd terraform
terraform init
terraform apply \
  -target=google_project_service.enabled \
  -target=google_artifact_registry_repository.fastapi
```

## 3. Build & push the image

**Option A — Cloud Build (no local Docker needed):**

```bash
# from the gcp-cloud-run-fastapi/ folder
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID"
```

**Option B — local Docker (build for linux/amd64 on Apple Silicon):**

```bash
gcloud auth configure-docker "${REGION}-docker.pkg.dev"
docker build --platform linux/amd64 -t "$IMAGE" .
docker push "$IMAGE"
```

## 4. Deploy Cloud Run (Terraform)

You can supply the image **dynamically** (recommended) or from `terraform.tfvars`.

**Dynamic (no file edits per version):**

```bash
cd terraform
terraform apply -var="image=$IMAGE"
```

**From tfvars:** ensure `image` in `terraform.tfvars` matches `$IMAGE`, then:

```bash
terraform apply
```

## 5. Test the service

```bash
URL=$(terraform output -raw cloud_run_url)

curl "$URL/"
curl "$URL/health"
```

Expected:

```json
{"message":"Hello World","service":"FastAPI on Cloud Run"}
{"status":"healthy"}
```

## 6. Update / redeploy a new version

```bash
export IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/hello-api:v2"
gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID"
terraform apply -var="image=$IMAGE"
```

No repo/API recreation needed — only the image tag changes.

## 7. Tear down

```bash
terraform destroy
```

---

## Terraform variables

| Variable       | Default        | Notes                                                     |
| -------------- | -------------- | --------------------------------------------------------- |
| `project_id`   | —              | Required. Your GCP project ID.                            |
| `region`       | `us-east1`     | Cloud Run + Artifact Registry region.                     |
| `service_name` | `fastapi-hello`| Cloud Run service name.                                   |
| `repo_id`      | `fastapi-repo` | Artifact Registry repository ID.                          |
| `image`        | —              | Required. Full image URI; can be passed via `-var`.       |

`terraform.tfvars`:

```hcl
project_id   = "project-52e8c95d-822f-4563-a7e"
region       = "us-east1"
service_name = "fastapi-hello"
image        = "us-east1-docker.pkg.dev/project-52e8c95d-822f-4563-a7e/fastapi-repo/hello-api:v1"
```

> If you always pass `-var="image=..."`, you can remove the `image` line from
> `terraform.tfvars` (the variable has no default, so it must come from one or
> the other).

---

## Code & Terraform review

**Correct and working:**
- `app/main.py` — valid FastAPI app with `/` and `/health`.
- `Dockerfile` — installs deps, respects Cloud Run's `PORT`, listens on `8080`.
- `terraform/main.tf` — enables APIs, creates the Artifact Registry repo, and
  deploys a Cloud Run v2 service with public access. `depends_on` ensures the
  APIs exist before the repo and service are created.
- Outputs expose the service URL, name, and region.

**Things to be aware of:**
1. **Two-step apply** — the image must be pushed between step 2 and step 4;
   Terraform can't build images.
2. **Public access** — `allUsers` makes the endpoint internet-facing. Remove the
   `public` IAM resource for an authenticated-only service.
3. **Apple Silicon** — build with `--platform linux/amd64` (step 3B) so the
   image runs on Cloud Run.
4. **Billing** — the project must have billing enabled for API enablement to
   succeed.
