PROJECT ?= $(GOOGLE_CLOUD_PROJECT)
REGION  ?= $(or $(GOOGLE_CLOUD_LOCATION),us-central1)
REPO    ?= $(REGION)-docker.pkg.dev/$(PROJECT)/dia-repo
IMAGE   ?= $(REPO)/dia-api:latest

.PHONY: help install infra corpus dev deploy-run deploy-runtime eval mcp a2a

help:
	@grep -E '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

install:  ## install deps locally
	pip install -r requirements.txt

infra:  ## terraform apply
	cd terraform && terraform init && terraform apply -var project_id=$(PROJECT) -var region=$(REGION)

corpus:  ## build the RAG corpus from gs://$(RAW_BUCKET)/contracts/
	PYTHONPATH=src python -m dia.ingestion.build_corpus \
	  --display-name contracts --gcs-path 'gs://$(RAW_BUCKET)/contracts/*'

dev:  ## run the ADK dev UI against the agent
	PYTHONPATH=src adk web src/dia/agents

api:  ## run FastAPI locally
	PYTHONPATH=src uvicorn dia.api.main:app --reload --port 8080

mcp:  ## run the MCP server over stdio
	PYTHONPATH=src python -m dia.mcp_server.server

a2a:  ## run the A2A server
	PYTHONPATH=src python -m dia.a2a.server

deploy-run:  ## build and deploy to Cloud Run
	gcloud builds submit --tag $(IMAGE) .
	gcloud run deploy dia-api --image $(IMAGE) --region $(REGION) \
	  --service-account dia-agent@$(PROJECT).iam.gserviceaccount.com \
	  --timeout 900 --cpu 2 --memory 2Gi --no-allow-unauthenticated

deploy-runtime:  ## deploy to Agent Runtime
	PYTHONPATH=src python -m dia.deploy.deploy_agent_runtime --display-name "DIA Orchestrator"

eval:  ## run RAG evaluation
	PYTHONPATH=src python evals/rag_eval.py --dataset evals/datasets/rag_eval.jsonl

eval-fast:  ## retrieval metrics only, no judge cost
	PYTHONPATH=src python evals/rag_eval.py --skip-judge
