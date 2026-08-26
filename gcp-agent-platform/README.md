# Document Intelligence Agent (DIA)

An end-to-end multi-agent system on the Gemini Enterprise Agent Platform. Built
as a portfolio-grade project rather than a tutorial: real IAM boundaries, real
cost guardrails, a real evaluation harness, and Terraform for everything.

The domain is deliberately generic — contracts and analytics — so it's safe to
put on GitHub while exercising exactly the architecture you'd build at work.

## What it does

Ask it "what's the termination clause in the Acme MSA?" and it does grounded
retrieval with citations. Ask it "how many contracts renewed last quarter?" and
it writes and runs BigQuery SQL. Ask it something that needs both and it
combines them, saying which part came from where. Ask it to *do* something
consequential and it refuses to act, filing an approval request instead.

## Architecture

```
                              User
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
              Cloud Run                Agent Runtime
             (FastAPI, SSE)          (managed sessions)
                    │                       │
                    └───────────┬───────────┘
                                ▼
                      dia_orchestrator  (ADK)
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
      document_qa_agent   analytics_agent   request_human_approval
              │                 │                 │
              ▼                 ▼                 ▼
        RAG Engine          BigQuery          Pub/Sub
              │            (read-only,       (approval
        Cloud Storage       cost-capped)       queue)

  Also exposed as:   MCP server (FastMCP)  ─ tools for any MCP client
                     A2A server            ─ agent-to-agent delegation

  Observability:     OpenTelemetry → Cloud Trace
  Infrastructure:    Terraform
```

Three design decisions worth calling out, because they're the difference
between a demo and something you'd defend in a review:

**The orchestrator holds no data credentials.** Retrieval and SQL access live
with the specialist agents. A prompt injection that captures the orchestrator
gets delegation ability, not a BigQuery credential.

**The agent cannot perform consequential actions.** `request_human_approval`
publishes to Pub/Sub and returns "pending". There is no code path where the
agent acts unilaterally. If the agent holds the credential to act, you don't
have a human in the loop — you have a human being notified.

**The SQL agent has three independent cost controls.** Read-only IAM, a
server-side `maximum_bytes_billed` cap, and a dry run before every query.
Prompt instructions are not a control.

## Layout

```
├── docs/AWS_TO_GCP_DEEP_DIVE.md   ← read this first
├── docs/LEARNING_PATH.md          ← 8-week sequence, mapped to this repo
├── terraform/                     ← project, IAM, buckets, BQ, Cloud Run
├── src/dia/
│   ├── config.py                  ← env-driven, one source of truth
│   ├── ingestion/                 ← extract (docling | Document AI), chunk, corpus
│   ├── tools/                     ← rag, bigquery, human-approval tools
│   ├── agents/                    ← rag_agent, sql_agent, root_agent
│   ├── mcp_server/                ← FastMCP — tools for any MCP client
│   ├── a2a/                       ← A2A server + agent card
│   ├── api/                       ← FastAPI, SSE streaming
│   ├── obs/                       ← OTel → Cloud Trace
│   └── deploy/                    ← Agent Runtime deployment
└── evals/                         ← retrieval + faithfulness harness
```

## Getting started

```bash
# 1. Project setup (enables APIs, does BOTH gcloud logins, makes a state bucket)
./scripts/bootstrap.sh my-project-id us-central1

# 2. Infrastructure
cd terraform && terraform init
terraform apply -var project_id=my-project-id
terraform output env_exports        # paste these into your shell
cd ..

# 3. Dependencies
pip install -r requirements.txt

# 4. Load some documents and build the corpus
gcloud storage cp ./sample-contracts/*.pdf gs://$RAW_BUCKET/contracts/
make corpus                          # prints the RAG_CORPUS to export

# 5. Run it locally — the ADK dev UI shows the full trace of each turn
make dev
```

Then pick a deployment target:

```bash
make deploy-run       # Cloud Run: you own the container and the HTTP surface
make deploy-runtime   # Agent Runtime: Google owns sessions and memory
```

Use Cloud Run while you're iterating — faster loop, full control. Move to Agent
Runtime when managing sessions and memory yourself stops being interesting.

## Evaluation

```bash
make eval-fast   # retrieval metrics only — deterministic, free
make eval        # adds LLM-judged faithfulness and answer relevance
```

Retrieval metrics are computed without a model: precision@k, recall@k, MRR. No
cost, no flakiness, safe to run on every commit. Only faithfulness and answer
relevance need a judge, and the judge runs on a cheaper model than the system
under test.

The dataset includes **negative cases** — questions the corpus genuinely cannot
answer. An index that confidently retrieves something for every question is
worse than one that returns nothing, and you won't catch that without probing
for it.

The rule that saves the most time: if retrieval recall is bad, no amount of
prompt engineering will fix the answer. Measure the stages separately or you'll
spend a week tuning the wrong one.

Wire `--fail-under` into CI once you have a baseline:

```bash
python evals/rag_eval.py --skip-judge --fail-under 0.8
```

## Gotchas that cost a day each

Collected here because every one of them cost someone an afternoon.

**APIs are disabled by default.** Every call returns 403 until you enable the
service. No AWS equivalent. `terraform/apis.tf` handles it.

**There are two gcloud logins.** `gcloud auth login` authenticates the CLI.
`gcloud auth application-default login` authenticates client libraries in your
code. Doing only the first and wondering why Python can't authenticate is a
rite of passage.

**`GOOGLE_GENAI_USE_VERTEXAI=TRUE`.** Without it the SDK targets the public
Gemini API and asks for an API key. This is the most common "why doesn't it
work" on the whole platform.

**BigQuery needs two roles.** `dataViewer` reads tables, `jobUser` runs
queries. You need both. The 403 you get with only the first doesn't mention
jobs.

**Build cloud clients lazily.** Agent Runtime deploys by cloudpickling your
agent. Module-level clients and threads break the upload, and the error doesn't
say so. Every module here constructs clients inside functions.

**Cloud Run throttles CPU outside requests.** Background threads and buffered
telemetry flushes stall silently. Enable CPU-always-allocated if you have
background work.

**Cloud Run concurrency defaults to 80, not 1.** Module-level mutable state
that was safe in Lambda is a race condition here.

**Set the Cloud Run timeout.** The default truncates long agent turns. Use
`--timeout=900` and disable response buffering or SSE gets cut mid-stream.

## Naming

Vertex AI became the Gemini Enterprise Agent Platform in 2026, and Agent Engine
became Agent Runtime. The APIs didn't change, so most tutorials and repos you
find still use the old names — they still work. `docs/AWS_TO_GCP_DEEP_DIVE.md`
has the full mapping and covers what actually changed versus what was renamed.
