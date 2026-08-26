# AWS → Google Cloud: where the mapping table stops helping

Your existing guide has the lookup tables. This document covers the part the
tables can't: the places where "X maps to Y" is true on a slide and false in
production. These are the things that cost a day each when you hit them cold.

Written against the platform as it stands in August 2026, after the Cloud Next
rename. Where a name changed recently I give both, because every tutorial,
Stack Overflow answer and GitHub repo you find will still use the old one.

---

## 0. The rename, and what actually changed

At Cloud Next in April 2026, Vertex AI was folded into the **Gemini Enterprise
Agent Platform**. By late May the Vertex AI entry was gone from the Console —
searching for it redirects you. This is not a thin rebrand; the information
architecture inverted. Vertex AI was a model platform that grew some agent
features. Agent Platform is an agent platform with model training, AutoML, Model
Registry and Endpoints as sub-features underneath it.

What this means for you practically:

| Old name | Name now |
|---|---|
| Vertex AI | Gemini Enterprise Agent Platform ("Agent Platform") |
| Vertex AI Agent Engine | Agent Runtime |
| Agent Builder Sessions | Agent Platform Sessions |
| Memory Bank | Agent Platform Memory Bank |
| Vertex AI Search | Search (also "Agent Search") |
| Agentspace | absorbed into Gemini Enterprise |

**The API endpoints did not change.** Existing `aiplatform.googleapis.com` calls
keep working, existing code keeps running, there is no forced migration. Two
things did change that you will notice: some IAM role display names shifted in
the Console, and billing line items rolled from Vertex AI to Gemini Enterprise
during May–June 2026. If you inherit a project with cost dashboards, they may
have broken silently.

The SDK is mid-transition and you will see three import styles in the wild:

```python
import vertexai                     # deployment, agent_engines — current
import agentplatform                # RAG Engine, newer surfaces — current
from vertexai.preview import rag    # older tutorials — same service
```

Don't try to normalise these. Use whichever the current doc for that specific
feature uses, and pin your SDK version.

---

## 1. The mappings that mislead

Five rows in the standard table are actively misleading. These are the ones
worth unlearning deliberately.

### "Lambda → Cloud Functions"

Directionally fine, operationally wrong for anything you'd build. Cloud
Functions (2nd gen) *is* Cloud Run underneath. For an AI workload you almost
never want Functions — you want Cloud Run directly, because you need a
container, a long timeout, and more than a trivial memory ceiling.

The bigger difference: **Lambda's 15-minute hard ceiling has no equivalent
here.** Cloud Run request timeout goes to 60 minutes, and Cloud Run jobs run
for hours. If you have architecture on AWS that exists purely to work around
the 15-minute wall — Step Functions chaining, chunked processing, SQS
re-invocation — much of that scaffolding can be deleted on GCP. That's a real
simplification, and it's easy to miss because the table says the services
correspond.

### "Glue → Dataflow"

This one causes the most wasted effort. Glue is three products in a trench
coat: a Spark runtime, a metadata catalog, and a visual ETL builder. Dataflow
is an Apache Beam runner and nothing else.

Split it properly:

- Glue's **Spark jobs** → Dataproc Serverless (same engine, same PySpark)
- Glue's **Data Catalog** → Dataplex Universal Catalog, or just BigQuery's own
  metadata if everything lands in BigQuery
- Glue's **crawlers** → no direct equivalent; you define schemas or use
  BigQuery autodetect
- Glue's **visual ETL** → Data Fusion

If you lift a Glue PySpark job to Dataflow you will rewrite it in Beam for no
reason. Take it to Dataproc Serverless and it usually runs close to unchanged.

**When Beam is actually worth it:** unified batch/streaming with the same code,
and event-time windowing with watermarks. Spark Structured Streaming's
watermark handling is genuinely weaker. If you don't need event-time semantics,
Beam's learning curve buys you nothing.

### "SageMaker → Vertex AI / Agent Platform"

Too coarse to be useful. SageMaker is one platform covering the whole ML
lifecycle. On GCP that lifecycle is split across BigQuery ML (SQL-native
models), Agent Platform Training and Endpoints (custom models), and Colab
Enterprise or Workbench (notebooks).

The genuinely important difference for a data engineer: **BigQuery ML has no
AWS equivalent worth naming.** You can train and serve a model with SQL, inside
the warehouse, with no data movement. Redshift ML exists but is thin by
comparison. For a large class of tabular problems this deletes an entire
pipeline. It's the single most underrated thing on GCP for someone with your
background.

### "Bedrock → Gemini"

Bedrock is a model-access API plus agents plus guardrails plus knowledge bases.
The Gemini API is only the model-access part. The rest lives elsewhere in Agent
Platform: ADK for agents, RAG Engine for knowledge bases, and governance
features for guardrails.

Model Garden ≈ the Bedrock model catalog, and yes, Claude models are
first-class in it alongside Gemini — so "we're on GCP therefore we use Gemini"
is a choice, not a constraint.

### "IAM Role → Service Account"

The closest single-cell answer, and still wrong enough to hurt. See below.

---

## 2. IAM: the difference that actually bites

This is the deepest conceptual gap, and it is worth slowing down on because
almost every confusing 403 you get in your first month traces back to it.

**AWS**: policies attach to identities *and* to resources. A bucket policy and
an IAM policy both grant access, and you reason about their intersection. Roles
are assumed — you swap identity temporarily via STS.

**GCP**: there is one direction only. You bind a *principal* to a *role* **on a
resource**. There is no resource-policy side that can independently grant
access. A "role" is just a named bundle of permissions — you don't assume it,
you *have* it.

Three consequences:

**Roles are additive and there is no deny by default.** IAM Deny policies exist
but are a separate, newer, rarely-used mechanism. In AWS you routinely reason
about explicit deny overriding allow. That reflex will mislead you here. If a
principal has a permission through *any* binding at *any* level of the
hierarchy, they have it.

**Permissions inherit down the hierarchy and cannot be revoked lower.** Grant
someone Editor at the organization level and you cannot take it away at a
single project. This is the opposite of the AWS mental model where a resource
policy can constrain. Design the hierarchy accordingly: grant low, never high.

**Read and execute are split in ways AWS doesn't split them.** The one that
will get you within a week:

```
roles/bigquery.dataViewer   # can read table contents
roles/bigquery.jobUser      # can run a query job
```

You need both to run a `SELECT`. dataViewer alone gets a 403 that doesn't
mention job permissions at all. There's no AWS parallel — `s3:GetObject`
doesn't require a separate "you may make a request" permission. You'll see this
handled explicitly in `terraform/iam.tf` in this repo, with a comment, because
it comes up every single time.

**Workload Identity Federation** is the equivalent of IRSA / OIDC role
assumption, and it's the right answer for CI and for cross-cloud. Do not create
service account key files. A downloaded JSON key is a permanent credential with
no rotation story — the same mistake as a long-lived IAM access key, and easier
to make here because the Console offers it cheerfully.

---

## 3. Project ≠ account (and that changes your architecture)

An AWS account is heavyweight. Creating one is a process, so teams cram
environments into fewer accounts and separate with tags and IAM conditions.

A GCP project is cheap and near-instant. The idiomatic pattern is **many small
projects** — one per environment per workload — because the project is the unit
of quota, billing, and IAM blast radius.

If you carry the AWS instinct over and build one big project with everything in
it, you get a worse result than either model would give you alone. Quotas are
per-project. So is much of the billing granularity. So is the audit story.

**The step with no AWS analogue at all**: APIs are disabled by default in a new
project. Every call to a service you haven't enabled returns 403 until you run
`gcloud services enable`. There's nothing like this in AWS — every service is
just there. This is the single most common thing that makes a first day on GCP
feel broken. `terraform/apis.tf` in this repo handles it up front.

---

## 4. BigQuery is not Redshift with a different name

You know Redshift and Athena. BigQuery is neither, and the difference is
structural rather than cosmetic.

**There is no cluster.** No node type, no resize, no maintenance window, no
WLM queue tuning, no VACUUM, no ANALYZE, no distribution key, no sort key. The
entire body of Redshift operational knowledge — which is real, hard-won
expertise — mostly does not transfer. That's disorienting rather than
pleasant at first.

**The cost model inverts your instincts.** Redshift: you pay for the cluster,
so queries are "free" and you optimise for cluster utilisation. BigQuery
on-demand: you pay per byte *scanned*, so every careless query costs money and
you optimise for scanning less.

Three habits follow directly:

- `SELECT *` on a wide table is now a billing event, not a style issue
- **Partitioning and clustering are cost controls, not just performance
  controls.** An unpartitioned filter scans everything and bills for
  everything.
- Set `maximum_bytes_billed` on every job. It's a hard stop. Without it, one
  bad generated query can cost four figures — which is exactly why the
  text-to-SQL agent in this repo dry-runs first and refuses anything over a
  configured ceiling. That guardrail is not paranoia; it's the standard answer
  to "what if the LLM writes a cross join."

**Editions / slot reservations** are the flat-rate alternative, and they're
closer to the Redshift mental model — buy capacity, then queries don't bill per
byte. Worth it above roughly a consistent 100 TB/month scanned, but run the
numbers on your actual usage.

**Federated query** covers most of what you'd use Athena for: BigQuery reads
external tables on Cloud Storage directly. You often don't need a load step at
all.

---

## 5. Dataproc vs EMR: closer than you'd expect

The cleanest mapping in the whole exercise. Same Spark, same PySpark, same
Hadoop lineage. Your EMR jobs mostly move over.

Real differences, in the order you'll notice them:

**Cluster startup is ~90 seconds, versus several minutes on EMR.** That sounds
minor and isn't — it changes ephemeral-cluster-per-job from a nuisance into the
default pattern.

**Dataproc Serverless has no EMR Serverless-equivalent warm-up story.** Submit
a PySpark batch, Google provisions and runs it, you never see a cluster. For
your EMR Serverless workloads this is a near drop-in.

**GCS is not HDFS and the connector semantics differ from S3's.** Cloud Storage
gives you strong read-after-write consistency for all operations, which S3 only
gained in 2020. More importantly, **directory rename is not atomic** — it's a
copy-and-delete under the hood. Spark's default `FileOutputCommitter` v1 relies
on rename for job commit. On large outputs this is slow and, on failure, can
leave partial results. Use the GCS connector's committer settings rather than
assuming HDFS semantics.

**Persistent History Server** is a separate deployment. On EMR the Spark UI
comes with the cluster; here, if you tear down ephemeral clusters, your job
history goes with them unless you've set one up. Do it early — debugging a job
you can no longer inspect is miserable.

---

## 6. Cloud Run vs Fargate/Lambda: the one you'll like

Cloud Run is the service most likely to change how you build, and it's
underrated in the mapping tables.

What's genuinely better than the AWS equivalents:

- **Scale to zero with fast cold starts.** Fargate doesn't scale to zero.
  Lambda does but constrains you to its packaging model.
- **`gcloud run deploy --source .`** builds and deploys from source with no
  Dockerfile. There's no comparable one-liner on AWS.
- **Request-based billing.** You pay for request-handling time, not
  instance-hours.
- **Traffic splitting is built in.** Canary and blue/green are a flag, not an
  ALB target group dance.

What to watch:

- **CPU is throttled outside a request** by default. Background threads,
  async cleanup, and buffered telemetry flushes silently stall. If you have
  background work, enable CPU-always-allocated — otherwise you'll debug a
  "hang" that's actually throttling.
- **Concurrency defaults to 80 requests per instance**, unlike Lambda's 1. Your
  code must actually be concurrency-safe. Module-level mutable state that was
  fine in Lambda is now a race condition.
- **Set the timeout explicitly for agent workloads.** The default will truncate
  long streaming turns. `--timeout=900` and disable response buffering, or SSE
  gets cut mid-stream.

---

## 7. Agents: ADK, Bedrock Agents, and LangGraph

You've built on all three of the relevant primitives, so this is about
architecture, not syntax.

**ADK vs Bedrock Agents.** Bedrock Agents is configuration-first: you define
action groups, attach an OpenAPI schema, and the service orchestrates. ADK is
code-first: agents are Python objects, you compose them, you control the loop.
Bedrock's model is faster to a demo. ADK's is easier to test, version, and
reason about — and much easier to run locally, which matters more than it
sounds.

**ADK vs LangGraph.** This is the comparison that actually matters for you, and
the honest answer is that they have different centres of gravity.

LangGraph is a graph execution engine. You define nodes and edges, state
transitions are explicit, and the graph is the program. That explicitness is
its strength — you can see and test every path — and its cost, because
expressing "just let the model decide" requires building the loop yourself.

ADK is agent-composition-first. `AgentTool` for delegation, `SequentialAgent` /
`ParallelAgent` / `LoopAgent` for deterministic control flow, sub-agents for
handoff. The model-driven path is the default and the deterministic path is
opt-in — the inverse of LangGraph's bias.

Practical translation guide:

| LangGraph | ADK |
|---|---|
| `StateGraph` with conditional edges | `Agent` with sub-agents (LLM routes) |
| explicit linear edges | `SequentialAgent` |
| parallel branches + join | `ParallelAgent` |
| cycle with an exit condition | `LoopAgent` with `max_iterations` |
| `interrupt()` for human input | long-running tool + Agent Runtime resume |
| checkpointer | Sessions / Memory Bank |

The trap: ADK's shared session state looks like LangGraph's typed state object
but isn't. LangGraph state is a schema you declare and reduce over. ADK session
state is a dict any agent in the tree can write. If you carry over a design
that depends on reducer semantics, you'll get subtle cross-agent clobbering. In
this repo the orchestrator deliberately holds no data credentials and delegates
via `AgentTool` — partly for blast radius, partly to keep state ownership
clean.

**A2A is now a Linux Foundation project**, not Google-only, with 150+
organisations behind it as of April 2026, and the protocol moved to production
status. Your existing A2A work transfers as protocol knowledge, not just GCP
knowledge — that's a durable rather than vendor-specific skill.

**Agent Runtime vs Bedrock AgentCore.** Both are managed agent hosting.
Differences worth knowing: Agent Runtime supports long-running operations up to
7 days, sub-second cold starts, and custom containers; provisioning is under a
minute. Deployment works by cloudpickling your agent and rebuilding it in a
managed container — which is why every cloud client in this repo is constructed
lazily inside a function. Module-level clients break the pickle, and the error
you get doesn't say so.

---

## 8. RAG: three paths, pick deliberately

You've built the OpenSearch path end to end, so the useful framing is what each
GCP option gives up.

| | Control | Effort | Closest AWS |
|---|---|---|---|
| **RAG Engine** | low | lowest | Bedrock Knowledge Bases |
| **Vector Search** | high | medium | OpenSearch k-NN |
| **Search / Agent Search** | medium | low | Kendra |

**RAG Engine** manages chunking, embedding, and index. One API call to create a
corpus, one to import from GCS, then attach it to Gemini as a grounding tool.
You give up custom chunking logic, your own reranker, and hybrid retrieval.

**Vector Search** (formerly Matching Engine) is the OpenSearch-equivalent path —
you own chunking, embedding, indexing, and reranking. Note it's ANN-only:
there's no built-in BM25, so true hybrid search means running lexical retrieval
separately and fusing yourself. That's a real gap versus OpenSearch, and the
main reason to keep an OpenSearch-shaped design if hybrid is load-bearing for
your quality.

**The honest recommendation** given what you've already built: start on RAG
Engine to get the system working, keep your evaluation harness pointed at the
retrieval stage, and move to Vector Search only when the metrics say managed
retrieval has plateaued. That's why `rag_tools.py` in this repo exposes both
paths behind one interface — swapping is a config change, not a rewrite.

One thing GCP does better: **grounding with Google Search** is a first-class
tool with citation metadata returned. There's no equivalent on Bedrock.

---

## 9. Observability

The mapping is clean (CloudWatch → Cloud Monitoring, X-Ray → Cloud Trace) but
two things differ in practice.

**Cloud Trace is OTel-native.** X-Ray has its own SDK and OTel support arrived
late. Cloud Trace takes standard OpenTelemetry, so instrumentation isn't
vendor-locked — you point the exporter elsewhere and nothing else changes.
Given your Monocle work this should feel familiar rather than new.

**Log-based metrics are better than CloudWatch Metric Filters** and are the
cheap way to get agent metrics without a metrics pipeline: emit structured
JSON logs, define a metric over a field, alert on it.

For agents specifically, the generic three pillars aren't enough. Trace
attributes worth having from day one, because retrofitting them is painful:
which model served the turn, token counts in and out, tool name and outcome per
call, retrieved document IDs, retry count, and any evaluation score. "The
request took 4.2s" tells you nothing; "three Gemini calls, one retried, plus an
800ms BigQuery scan" tells you what to fix.

**Sample aggressively.** Every tool call is a span. A busy agent generates
enough trace volume to matter on the bill.

---

## 10. Things with no real equivalent

Worth knowing in both directions, because these are where architecture
genuinely diverges rather than just renaming.

**On GCP, nothing to point at from AWS:**
- BigQuery ML — training and serving from SQL, in the warehouse
- Global VPC — GCP VPCs span regions natively; no peering mesh for a
  multi-region footprint
- Live migration — VMs move across hosts during maintenance without a reboot
- Grounding with Google Search as a first-class model tool

**On AWS, nothing clean on GCP:**
- Step Functions — Workflows is thinner; complex sagas need more of your own code
- The sheer breadth of the service catalog
- Spot Instances vs Preemptible/Spot VMs — GCP's are capped at 24 hours
- IAM condition keys — GCP's IAM Conditions are far more limited

---

## 11. Interview answers worth having ready

Your existing guide lists the questions. Here are the answers that separate a
real answer from a memorised table row.

**"Redshift vs BigQuery?"** — Not warehouse vs warehouse. Redshift is
provisioned compute you tune and pay for by the hour; BigQuery is serverless
with per-byte-scanned billing and no cluster to manage. The consequence is that
optimisation targets invert: on Redshift you optimise cluster utilisation, on
BigQuery you optimise bytes scanned, so partitioning and clustering become cost
controls rather than just performance tuning.

**"IAM Role vs Service Account?"** — An IAM role is assumed temporarily via
STS; a service account is a durable identity that *has* roles bound to it. GCP
has no resource-policy side, so all access flows one direction from principal
to resource, and permissions inherit down the hierarchy without a way to revoke
them lower. Practically: grant at the lowest level that works, and use Workload
Identity Federation rather than key files.

**"When Spark vs Beam?"** — Spark when you have existing Spark, or heavy
iterative/ML work, or the team knows it. Beam when you need one codebase for
batch and streaming, or event-time windowing with watermarks where Spark
Structured Streaming is weaker. Don't rewrite working Spark into Beam to be on
the "Google-native" service — take it to Dataproc Serverless.

**"LangGraph vs ADK?"** — Different defaults. LangGraph makes control flow
explicit and model autonomy something you build; ADK makes model-driven
delegation the default and explicit control flow opt-in via Sequential/Parallel/
Loop agents. LangGraph is easier to test exhaustively; ADK is faster to compose
and has a managed runtime behind it. The state models differ in a way that
doesn't survive a naive port — LangGraph reduces over typed state, ADK session
state is a shared mutable dict.

**"How do you stop a text-to-SQL agent bankrupting you?"** — Three layers, and
you want all three: read-only IAM on the service account so it *can't* write;
`maximum_bytes_billed` as a hard server-side stop; and a dry run first so the
agent sees the cost estimate and can narrow its own query before committing.
Prompt instructions alone are not a control.
