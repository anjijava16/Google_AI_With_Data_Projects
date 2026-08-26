# 8-week path, mapped to this repo

Your existing guide has a 47-item ordered list. That's the right content but
too flat to execute against — everything looks equally weighted. This is the
same material sequenced by **what unblocks what**, with each week ending in
something that runs.

The bias throughout: build the thin end-to-end slice early, then deepen. A
working system with a bad retriever teaches you more than a perfect retriever
with nothing around it.

---

## Week 1 — Foundations (the boring week that prevents three later ones)

`scripts/bootstrap.sh`, `terraform/apis.tf`, `terraform/iam.tf`

Projects, IAM, service accounts, gcloud, Cloud Storage, Artifact Registry.

Do not skim IAM because you know AWS IAM. The additive-only model, the missing
resource-policy side, and the split between `dataViewer` and `jobUser` are
where your instincts actively mislead you. Read §2 of the deep dive properly.

**Done when:** `terraform apply` stands up the whole project from nothing, and
you can explain why the agent service account has exactly the five roles it
has and not one more.

---

## Week 2 — Cloud Run and the serving layer

`Dockerfile`, `src/dia/api/main.py`, `terraform/cloud_run.tf`

FastAPI in a container, deployed, streaming over SSE.

This is your fastest win — the architecture is one you already run on
ECS/Fargate. Spend the time on the three differences that bite: CPU throttling
outside requests, concurrency of 80 rather than 1, and the timeout that
truncates streams.

**Done when:** an SSE endpoint streams a Gemini response through Cloud Run
without truncating, and you've deliberately triggered the CPU-throttling
behaviour once so you recognise it later.

---

## Week 3 — Gemini and the GenAI SDK

`src/dia/config.py`, `src/dia/tools/`

Gemini API, function calling, structured output, streaming, embeddings.

Map every call to its Bedrock equivalent as you go. The mechanics are close
enough that the differences are what's worth writing down.

**Done when:** you have a tool-calling loop working end to end and can state
plainly what Model Garden gives you that the Bedrock catalog doesn't, and
vice versa.

---

## Week 4 — Data layer

`terraform/bigquery.tf`, `src/dia/tools/bigquery_tools.py`

BigQuery, partitioning, clustering, cost controls. Pub/Sub. Skim Dataflow and
Dataproc.

Your prior Google DE experience makes this the fastest week. The genuinely new
thing is the cost model — internalise that partitioning is a *billing* control,
not a performance one, because it changes how you design tables.

Give BigQuery ML an afternoon. It has no real AWS equivalent and it's the most
underrated thing on the platform for your background.

**Done when:** you've made a query cost more than you expected, then fixed it
with partitioning, and you know what the fix saved.

---

## Week 5 — RAG

`src/dia/ingestion/`, `src/dia/tools/rag_tools.py`

RAG Engine, Vector Search, chunking, grounding.

You've built this on OpenSearch, so the value here is comparative. Build the
managed path first (RAG Engine), get it working, then look hard at what you
gave up: custom chunking, your own reranker, and hybrid BM25 + vector — Vector
Search is ANN-only, which is a real gap versus OpenSearch.

**Done when:** you can answer "when would you not use RAG Engine?" with a
specific quality reason from your own eval numbers rather than a general one.

---

## Week 6 — ADK and multi-agent

`src/dia/agents/`

Agents, tools, Sequential/Parallel/Loop, sub-agents, sessions, memory.

Your deepest area and where your LangGraph experience both helps and misleads.
The trap is state: LangGraph reduces over typed state, ADK session state is a
shared mutable dict any agent can write. A naive port produces cross-agent
clobbering that's hard to trace.

Build the deterministic workflow agents even if the model-driven path works —
you need to know which to reach for when reliability matters more than
flexibility.

**Done when:** you can articulate the ADK ↔ LangGraph translation table from
§7 of the deep dive without looking, including where it breaks down.

---

## Week 7 — Protocols and production

`src/dia/mcp_server/`, `src/dia/a2a/`, `src/dia/deploy/`, `src/dia/obs/`

MCP, A2A, Agent Runtime, Cloud Trace.

Your MCP and A2A experience transfers directly — this is protocol knowledge,
not GCP knowledge, and A2A is a Linux Foundation project now rather than a
Google one. The new material is Agent Runtime: how cloudpickle deployment
works, why lazy client construction matters, and what managed sessions and
Memory Bank give you over rolling your own.

**Done when:** the same agent is reachable three ways — HTTP via Cloud Run, MCP
from a local client, and A2A from another agent — and traces land in Cloud
Trace with token counts and tool outcomes attached.

---

## Week 8 — Evaluation and the write-up

`evals/`

Retrieval metrics, faithfulness, negative cases, CI gating.

This is the week that makes the project credible rather than impressive. Anyone
can demo an agent. Far fewer can show a retrieval recall number, a faithfulness
score, and a CI gate that fails the build when they regress.

Then write it up — the comparative architecture piece is the artifact that
demonstrates the AWS→GCP transfer better than the code does.

**Done when:** `--fail-under` is wired into CI against a real baseline, and
you've written the "how I'd migrate an AWS agent platform to GCP" post.

---

## What to cut if you have less time

Four weeks: 1, 2, 6, 8. Foundations, serving, agents, evaluation. Skip the data
layer — your prior DE experience covers enough — and use RAG Engine's defaults
without going deep.

Two weeks: 1 and 6, and deploy to Agent Runtime rather than building the Cloud
Run path. You'll have an agent running with proper IAM, which is the minimum
that proves anything.

## What not to spend time on

Compute Engine. You know EC2 and the concepts transfer directly; there's
nothing here that repays study time.

GKE, unless you specifically need it. You know Kubernetes. Workload Identity is
the one genuinely new piece and it's an afternoon.

Chasing the rename. Vertex AI and Agent Platform are the same services. Learn
the current architecture, recognise the old names in tutorials, move on.
