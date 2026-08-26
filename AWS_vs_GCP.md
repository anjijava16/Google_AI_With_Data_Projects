# AWS → Google Cloud 2026

# Deep-Dive Learning & Hands-On Guide

> **Target Profile:** Senior / Staff / Principal Cloud + ML + GenAI + Agentic AI Engineer
> **Starting Point:** Strong AWS experience + previous Google Cloud Data Engineering experience
> **Primary Goal:** Rebuild deep Google Cloud expertise while mapping every major concept to AWS.

---

# 1. Why This Guide Exists

I previously worked extensively with Google Cloud and Google Data Engineering.

Over the last several years, my primary cloud ecosystem has been AWS, including:

* AWS
* S3
* IAM
* VPC
* EC2
* ECS/EKS
* Glue
* EMR
* Redshift
* OpenSearch
* SageMaker
* SageMaker Pipelines
* SageMaker Endpoints
* Bedrock
* Bedrock Agents
* RAG
* LLM applications
* LangChain
* LangGraph
* MCP
* A2A
* FastAPI
* Terraform

Now I am returning to Google Cloud.

The objective is **not to relearn cloud computing from zero**.

The objective is:

```text
Existing AWS Expertise
        +
Previous Google Data Engineering Experience
        +
Recent GenAI / Agentic AI Experience
        ↓
Deep Google Cloud 2026 Expertise
```

---

# 2. Important 2026 Google Cloud Naming

Google Cloud's AI platform has evolved significantly.

Historically:

```text
Vertex AI
```

was Google's unified AI/ML platform.

In 2026, Google is positioning the platform around:

```text
Gemini Enterprise Agent Platform
```

and its agent-centric capabilities.

You will still encounter the term **Vertex AI** extensively in:

* older tutorials
* SDKs
* APIs
* GitHub repositories
* documentation
* architecture diagrams
* existing enterprise systems

Therefore:

```text
Vertex AI
     ↓
Evolution / transition
     ↓
Gemini Enterprise Agent Platform
```

Do not treat Vertex AI and Agent Platform as completely unrelated products.

The important goal is understanding the **current architecture**, while recognizing legacy terminology.

---

# 3. High-Level AWS → Google Cloud Mapping

## Core Cloud

| AWS            | Google Cloud                        |
| -------------- | ----------------------------------- |
| AWS Account    | GCP Project / Organization          |
| Organizations  | Resource hierarchy                  |
| IAM            | Cloud IAM                           |
| IAM Role       | Service Account / Workload Identity |
| CloudFormation | Terraform                           |
| S3             | Cloud Storage                       |
| EBS            | Persistent Disk                     |
| EFS            | Filestore                           |
| EC2            | Compute Engine                      |
| ECS            | Cloud Run / GKE                     |
| EKS            | GKE                                 |
| Lambda         | Cloud Functions                     |
| Fargate        | Cloud Run                           |
| ALB            | Cloud Load Balancing                |
| Route 53       | Cloud DNS                           |
| CloudFront     | Cloud CDN                           |

---

# 4. Data Engineering Mapping

| AWS            | Google Cloud                      |
| -------------- | --------------------------------- |
| S3             | Cloud Storage                     |
| Glue           | Dataflow / Dataproc / Data Fusion |
| EMR            | Dataproc                          |
| EMR Serverless | Dataproc Serverless               |
| Kinesis        | Pub/Sub / Dataflow                |
| MSK            | Managed Kafka                     |
| Redshift       | BigQuery                          |
| Athena         | BigQuery                          |
| DynamoDB       | Firestore / Bigtable              |
| RDS            | Cloud SQL                         |
| ElastiCache    | Memorystore                       |
| Lake Formation | Dataplex / governance ecosystem   |

---

# 5. ML / GenAI Mapping

| AWS                      | Google Cloud                           |
| ------------------------ | -------------------------------------- |
| SageMaker AI             | Agent Platform ML capabilities         |
| SageMaker Studio         | Agent Platform development environment |
| SageMaker Training       | Agent Platform Training                |
| SageMaker Model Registry | Model management / registry            |
| SageMaker Endpoint       | Model deployment / endpoint            |
| SageMaker Pipelines      | Agent Platform Pipelines               |
| SageMaker Model Monitor  | Model Monitoring                       |
| Bedrock                  | Gemini + Agent Platform                |
| Bedrock Model Catalog    | Model Garden                           |
| Bedrock Knowledge Bases  | Agent Search / RAG capabilities        |
| Bedrock Agents           | ADK + Agent Runtime                    |
| Bedrock AgentCore        | Agent Runtime ecosystem                |
| Bedrock Guardrails       | Agent Platform safety/governance       |
| Bedrock Evaluation       | Agent / Model Evaluation               |

---

# 6. Observability / Security Mapping

| AWS             | Google Cloud                             |
| --------------- | ---------------------------------------- |
| CloudWatch      | Cloud Monitoring                         |
| CloudWatch Logs | Cloud Logging                            |
| CloudTrail      | Cloud Audit Logs                         |
| X-Ray           | Cloud Trace                              |
| KMS             | Cloud KMS                                |
| Secrets Manager | Secret Manager                           |
| GuardDuty       | Security Command Center ecosystem        |
| Security Hub    | Security Command Center                  |
| AWS Config      | Cloud Asset Inventory / policy ecosystem |

---

# 7. The Most Important Mental Model

Do not learn Google Cloud service-by-service.

Think in platforms.

```text
                         GOOGLE CLOUD
                              |
        +---------------------+---------------------+
        |                     |                     |
        ▼                     ▼                     ▼
     DATA                  ML / AI              AGENTS
        |                     |                     |
   BigQuery             Agent Platform          ADK
   GCS                   Gemini                  Runtime
   Dataflow              Model Garden           MCP
   Dataproc              RAG                     A2A
   Pub/Sub               Search                  Memory
        |                     |                     |
        +---------------------+---------------------+
                              |
                              ▼
                         Applications
```

---

# 8. Google Cloud Resource Hierarchy

This is one of the first things to refresh.

```text
Organization
    |
    +-- Folder
    |      |
    |      +-- Project A
    |      +-- Project B
    |
    +-- Folder
           |
           +-- Project C
```

A project is a very important operational boundary.

A typical enterprise setup:

```text
Organization
|
+-- Engineering
|    |
|    +-- AI-DEV
|    +-- AI-TEST
|    +-- AI-PROD
|
+-- Data
     |
     +-- DATA-DEV
     +-- DATA-PROD
```

Compare to AWS:

```text
AWS Organization
|
+-- OU
     |
     +-- AWS Account
```

The concepts are similar, but the implementation and IAM model differ.

---

# 9. GCP CLI

Install Google Cloud CLI.

Verify:

```bash
gcloud version
```

Login:

```bash
gcloud auth login
```

Application Default Credentials:

```bash
gcloud auth application-default login
```

List projects:

```bash
gcloud projects list
```

Set project:

```bash
gcloud config set project PROJECT_ID
```

Check configuration:

```bash
gcloud config list
```

Check account:

```bash
gcloud auth list
```

---

# 10. AWS CLI vs gcloud

AWS:

```bash
aws sts get-caller-identity
aws configure
aws s3 ls
aws ec2 describe-instances
```

Google:

```bash
gcloud auth list
gcloud config list
gcloud storage ls
gcloud compute instances list
```

Important distinction:

```text
AWS CLI
   ↓
Many service-specific commands

gcloud
   ↓
Google Cloud resource hierarchy
   +
service commands
```

---

# 11. Cloud Storage vs S3

## AWS

```text
S3
 |
 +-- Bucket
      |
      +-- Object
      +-- Prefix
      +-- Lifecycle
      +-- Versioning
```

## Google

```text
Cloud Storage
 |
 +-- Bucket
      |
      +-- Object
      +-- Prefix
      +-- Lifecycle
      +-- Versioning
```

Example:

```bash
gcloud storage buckets list
```

Create bucket:

```bash
gcloud storage buckets create gs://MY_BUCKET \
  --location=US
```

Upload:

```bash
gcloud storage cp file.txt gs://MY_BUCKET/
```

List:

```bash
gcloud storage ls gs://MY_BUCKET/
```

---

# 12. Cloud Storage Architecture

A typical enterprise data lake:

```text
                   Cloud Storage
                         |
        +----------------+----------------+
        |                |                |
        ▼                ▼                ▼
      raw/           processed/        curated/
        |                |                |
        ▼                ▼                ▼
   Original data    Clean data       Analytics data
```

Example:

```text
gs://company-data/
|
+-- raw/
|    +-- documents/
|    +-- events/
|
+-- processed/
|    +-- text/
|    +-- embeddings/
|
+-- curated/
     +-- analytics/
```

---

# 13. IAM Deep Dive

AWS IAM:

```text
Principal
   ↓
Policy
   ↓
Action
   ↓
Resource
```

Google:

```text
Principal
   ↓
IAM Role
   ↓
Permission
   ↓
Resource
```

Important Google identities:

```text
User
Service Account
Group
Workload Identity
Federated Identity
```

Example service account:

```text
agent-prod@PROJECT_ID.iam.gserviceaccount.com
```

Your production agents should normally use service identities rather than personal credentials.

---

# 14. Service Accounts

Create:

```bash
gcloud iam service-accounts create agent-prod \
  --display-name="Production Agent"
```

List:

```bash
gcloud iam service-accounts list
```

Grant role:

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:agent-prod@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

The important architectural concept:

```text
Agent
  |
  ▼
Service Account
  |
  +-- BigQuery permissions
  +-- GCS permissions
  +-- Secret permissions
  +-- Vertex/Agent Platform permissions
```

---

# 15. BigQuery

BigQuery should be one of your highest-priority refresh areas.

Think:

```text
AWS Redshift
       +
Athena
       +
large-scale analytics ecosystem
```

→

```text
BigQuery
```

BigQuery architecture:

```text
Cloud Storage
      |
      ▼
   BigQuery
      |
 +----+------------------+
 |                       |
 ▼                       ▼
Analytics              ML / AI
 |                       |
SQL                    Embeddings
 |                       |
BI                     RAG
```

Create dataset:

```bash
bq mk --dataset PROJECT_ID:analytics
```

List datasets:

```bash
bq ls
```

Query:

```bash
bq query \
'SELECT * FROM `PROJECT_ID.analytics.customer` LIMIT 10'
```

---

# 16. BigQuery vs Redshift

AWS:

```text
S3
 ↓
Glue
 ↓
Redshift
```

Google:

```text
GCS
 ↓
Dataflow / Dataproc
 ↓
BigQuery
```

But BigQuery can also query external data and integrate tightly with Cloud Storage.

The major concept:

```text
Storage
+
Compute
+
Analytics
```

are highly decoupled.

---

# 17. Dataproc

## Dataproc = Managed Spark/Hadoop

This is important.

If you know AWS EMR:

```text
EMR
 ↓
Dataproc
```

Dataproc supports workloads involving technologies such as:

```text
Apache Spark
Hadoop
Hive
Spark SQL
PySpark
Scala
```

Architecture:

```text
             Dataproc
                 |
       +---------+---------+
       |         |         |
     Spark     Hadoop     Hive
       |
       ▼
Cloud Storage / BigQuery
```

---

# 18. Dataproc Serverless

Traditional Dataproc:

```text
Create cluster
      ↓
Master
Workers
      ↓
Run Spark
      ↓
Terminate cluster
```

Dataproc Serverless:

```text
PySpark Job
     |
     ▼
Dataproc Serverless
     |
     ▼
Google manages compute
```

Use this when you want Spark without managing long-lived clusters.

---

# 19. Dataproc vs Dataflow

This distinction is critical.

## Dataproc

Think:

> I have Spark/Hadoop workloads.

```text
PySpark
Spark SQL
Scala Spark
Hadoop
Hive
```

## Dataflow

Think:

> I need distributed processing using Apache Beam.

```text
Apache Beam
     |
     ▼
Dataflow
     |
 +---+---+
 |       |
Batch Streaming
```

Therefore:

```text
AWS EMR
    ↓
Dataproc

AWS Glue
    ↓
Dataflow OR Dataproc
depending on workload
```

Do not treat Dataflow as simply "Google EMR."

---

# 20. Pub/Sub

Google's event backbone.

Conceptually:

```text
Application
    |
    ▼
 Pub/Sub
    |
 +--+----------+
 |             |
 ▼             ▼
Dataflow      Agent
 |
 ▼
BigQuery
```

AWS equivalents depend on the pattern:

```text
SNS
SQS
Kinesis
EventBridge
```

Google often uses:

```text
Pub/Sub
+
Eventarc
+
Dataflow
```

depending on the architecture.

---

# 21. Dataflow

Dataflow is based on Apache Beam.

```text
Producer
   |
   ▼
Pub/Sub
   |
   ▼
Dataflow
   |
   +-- Transform
   +-- Filter
   +-- Join
   +-- Window
   +-- Aggregate
   |
   ▼
BigQuery
```

Learn:

* batch
* streaming
* windows
* watermarks
* state
* triggers
* autoscaling
* Beam SDK
* Python
* Java

---

# 22. Compute Engine

AWS:

```text
EC2
```

Google:

```text
Compute Engine
```

You already know the concepts.

Focus on:

* machine types
* images
* disks
* VPC
* firewall rules
* instance groups
* load balancing
* autoscaling
* service accounts

Do not spend too much time here.

---

# 23. Cloud Run

This should be high priority for you.

Your FastAPI architecture:

```text
FastAPI
   |
Docker
   |
Artifact Registry
   |
Cloud Run
```

Example:

```text
User
 |
 ▼
Cloud Run
 |
 +-- FastAPI
 +-- ADK Agent
 +-- MCP Server
 +-- REST API
```

This is extremely useful for modern AI applications.

---

# 24. GKE

AWS:

```text
EKS
```

Google:

```text
GKE
```

You already know Kubernetes.

Focus on:

* GKE Autopilot
* GKE Standard
* Workload Identity
* networking
* private clusters
* autoscaling
* service accounts
* Cloud Load Balancing

---

# 25. Vertex AI → Agent Platform

Historically:

```text
Vertex AI
 |
 +-- Training
 +-- Model Registry
 +-- Endpoints
 +-- Pipelines
 +-- Gemini
 +-- RAG
 +-- Search
 +-- Agents
```

Current direction:

```text
Gemini Enterprise Agent Platform
 |
 +-- Gemini
 +-- Model Garden
 +-- Agent Studio
 +-- Agent Development Kit
 +-- Agent Runtime
 +-- Agent Search
 +-- RAG
 +-- Evaluation
 +-- Memory
 +-- Sessions
 +-- Governance
```

Your goal is understanding both old and new terminology.

---

# 26. SageMaker AI → Agent Platform

AWS:

```text
SageMaker AI
 |
 +-- Studio
 +-- Training
 +-- Processing
 +-- Pipelines
 +-- Model Registry
 +-- Endpoints
 +-- Monitoring
```

Google:

```text
Agent Platform
 |
 +-- Development
 +-- Training
 +-- Model management
 +-- Deployment
 +-- Evaluation
 +-- Monitoring
```

The important difference:

Google's current platform increasingly combines:

```text
Traditional ML
+
Foundation Models
+
Generative AI
+
Agents
```

---

# 27. Gemini

Gemini is Google's foundation model family.

Learn:

```text
Gemini
 |
 +-- Text
 +-- Vision
 +-- Audio
 +-- Video
 +-- Multimodal
 +-- Tool Calling
 +-- Structured Output
 +-- Streaming
 +-- Embeddings
 +-- Grounding
```

Your Bedrock comparison:

```text
AWS Bedrock
   |
   +-- Foundation Models
   +-- Tool use
   +-- Agents
   +-- RAG
```

Google:

```text
Gemini / Model Garden
   |
   +-- Gemini
   +-- Other models
   +-- Tool use
   +-- RAG
   +-- Agents
```

---

# 28. Model Garden

Think:

```text
AWS Bedrock Model Access
        ↓
Google Model Garden
```

The architecture:

```text
                    Model Garden
                         |
       +-----------------+-----------------+
       |                 |                 |
       ▼                 ▼                 ▼
    Gemini          Open Models       Partner Models
```

Do not only learn Gemini.

As an architect, learn:

```text
Model selection
Cost
Latency
Context
Quality
Fine-tuning
Hosting
Security
Data residency
```

---

# 29. Google GenAI SDK

Learn the current Google GenAI SDK instead of relying only on older Vertex-specific examples.

Conceptually:

```python
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="GEMINI_MODEL",
    contents="Explain BigQuery architecture"
)

print(response.text)
```

Then learn:

```text
Streaming
Tool Calling
Structured Output
Multimodal
Embeddings
Async
```

---

# 30. Streaming

For an AI application:

```text
User
 |
 ▼
FastAPI
 |
 ▼
Gemini
 |
 +-- chunk
 +-- chunk
 +-- chunk
 +-- chunk
 |
 ▼
User
```

Understand:

```text
Streaming
SSE
WebSocket
async generators
backpressure
timeouts
retries
```

This connects directly to your previous LangGraph / ADK streaming questions.

---

# 31. RAG

Your existing AWS architecture:

```text
S3
 ↓
Textract
 ↓
Chunking
 ↓
Embeddings
 ↓
OpenSearch
 ↓
Bedrock
```

Google:

```text
Cloud Storage
 ↓
Document processing
 ↓
Chunking
 ↓
Gemini Embeddings
 ↓
Agent Search / Vector Search / RAG
 ↓
Gemini
```

Learn both:

```text
Managed RAG
```

and:

```text
Custom RAG
```

---

# 32. RAG Pipeline

```text
                DOCUMENT INGESTION

Cloud Storage
      |
      ▼
Document Processor
      |
      ▼
Text Extraction
      |
      ▼
Chunking
      |
      ▼
Embedding Model
      |
      ▼
Vector Index
      |
      ▼
Metadata
```

Query:

```text
User
 |
 ▼
Query
 |
 ▼
Query Embedding
 |
 ▼
Vector Search
 |
 ▼
Top-K Documents
 |
 ▼
Context Construction
 |
 ▼
Gemini
 |
 ▼
Grounded Answer
```

---

# 33. RAG Evaluation

Do not stop at "the answer looks good."

Measure:

```text
Retrieval Precision
Retrieval Recall
Context Relevance
Faithfulness
Groundedness
Answer Relevance
Latency
Token Usage
Cost
```

Build an evaluation dataset:

```text
question
expected_answer
expected_documents
actual_documents
actual_answer
score
```

This should become part of your production pipeline.

---

# 34. Agent Development Kit — ADK

ADK is Google's agent development framework.

Conceptually:

```text
Agent
 |
 +-- Instruction
 +-- Model
 +-- Tools
 +-- Callbacks
 +-- Sessions
 +-- Memory
 +-- Sub-agents
```

Your mental mapping:

```text
LangGraph
      ↕
Google ADK
```

But do not assume identical abstractions.

Learn ADK natively.

---

# 35. Basic Agent Architecture

```text
User
 |
 ▼
Root Agent
 |
 +-- Tool
 |
 +-- Tool
 |
 +-- Sub-Agent
 |
 +-- Sub-Agent
 |
 ▼
Response
```

Example:

```text
                    Root Agent
                        |
        +---------------+---------------+
        |               |               |
        ▼               ▼               ▼
    Research          SQL             RAG
     Agent           Agent           Agent
        |               |               |
      Search         BigQuery       Vector Search
```

---

# 36. Multi-Agent Architecture

Build:

```text
                Orchestrator
                     |
       +-------------+-------------+
       |             |             |
       ▼             ▼             ▼
 Research        RAG Agent      SQL Agent
 Agent
       |             |             |
       ▼             ▼             ▼
  Search         Vector DB     BigQuery
```

Then add:

```text
MCP
A2A
Memory
Sessions
Evaluation
```

---

# 37. MCP

You already know MCP.

Use it as a tool integration protocol:

```text
Agent
 |
 ▼
MCP Client
 |
 +-- S3/GCS tool
 +-- Database tool
 +-- Search tool
 +-- API tool
```

For Google:

```text
Agent
 |
 ▼
MCP
 |
 +-- BigQuery
 +-- Cloud Storage
 +-- APIs
 +-- Enterprise systems
```

Your previous MCP experience transfers directly.

---

# 38. A2A

A2A is useful for agent-to-agent communication.

```text
Agent A
   |
   | A2A
   ▼
Agent B
   |
   ▼
Agent C
```

Example:

```text
Customer Agent
      |
      ▼
Research Agent
      |
      ▼
Risk Agent
      |
      ▼
Decision Agent
```

Learn:

```text
Agent discovery
Agent identity
Agent communication
Task delegation
Authentication
Authorization
Observability
```

---

# 39. Agent Runtime

Think:

```text
ADK
 |
 | build
 ▼
Agent
 |
 | deploy
 ▼
Agent Runtime
 |
 +-- Scaling
 +-- Sessions
 +-- Memory
 +-- Security
 +-- Observability
 +-- Production execution
```

This is where your existing:

```text
FastAPI
Agent hosting
MCP servers
A2A servers
```

experience becomes useful.

---

# 40. Agent Memory

Understand the difference:

```text
Conversation history
       vs
Session
       vs
Long-term memory
       vs
Application state
```

Architecture:

```text
User
 |
 ▼
Agent
 |
 +-- Session
 |
 +-- Conversation
 |
 +-- Memory
 |
 +-- Tools
```

Never treat all four as the same thing.

---

# 41. Production Agent Architecture

Build toward:

```text
                         USER
                           |
                           ▼
                     API Gateway
                           |
                           ▼
                       Cloud Run
                           |
                           ▼
                   Agent Orchestrator
                           |
          +----------------+----------------+
          |                |                |
          ▼                ▼                ▼
       RAG Agent       SQL Agent       Research Agent
          |                |                |
          ▼                ▼                ▼
     Agent Search       BigQuery         Search/API
          |
          ▼
     Cloud Storage
```

Model:

```text
Gemini
```

Agent framework:

```text
ADK
```

Runtime:

```text
Agent Runtime
```

Infrastructure:

```text
Terraform
```

---

# 42. Enterprise Security

Production architecture:

```text
                         Identity
                            |
                            ▼
                         IAM
                            |
             +--------------+--------------+
             |              |              |
             ▼              ▼              ▼
         Agent SA       Tool SA       Data SA
             |
             ▼
        Agent Runtime
             |
     +-------+-------+
     |               |
     ▼               ▼
   BigQuery          GCS
```

Add:

```text
Secret Manager
Cloud KMS
VPC
Private connectivity
Audit Logs
Security Command Center
```

---

# 43. Observability

For traditional applications:

```text
Logs
Metrics
Traces
```

For AI agents add:

```text
Prompt
Response
Token usage
Model
Latency
Tool calls
Tool failures
Agent transitions
Retrieved documents
Evaluation scores
```

Example:

```text
Agent Request
 |
 +-- Gemini: 1.2 sec
 |
 +-- Search: 300 ms
 |
 +-- BigQuery: 800 ms
 |
 +-- Gemini: 1.5 sec
 |
 ▼
Response
```

This is essential for production agent platforms.

---

# 44. Terraform

You already know Terraform.

Use it from the beginning.

Example structure:

```text
gcp-agent-platform/
|
+-- terraform/
|    |
|    +-- providers.tf
|    +-- variables.tf
|    +-- main.tf
|    +-- iam.tf
|    +-- storage.tf
|    +-- bigquery.tf
|    +-- cloudrun.tf
|    +-- artifact_registry.tf
|    +-- outputs.tf
|
+-- agents/
|
+-- services/
|
+-- tests/
|
+-- README.md
```

Initialize:

```bash
terraform init
```

Plan:

```bash
terraform plan
```

Apply:

```bash
terraform apply
```

---

# 45. CI/CD

Production:

```text
GitHub
   |
   ▼
CI
   |
   +-- Unit Tests
   +-- RAG Evaluation
   +-- Security Scan
   +-- Build Docker
   |
   ▼
Artifact Registry
   |
   ▼
Cloud Run / Agent Runtime
```

Terraform:

```text
Terraform
   |
   ▼
Dev
   |
   ▼
Test
   |
   ▼
Prod
```

---

# 46. Recommended Repository

Create:

```text
aws-to-gcp-agent-platform/
|
+-- 01-gcp-foundations/
|
+-- 02-cloud-storage/
|
+-- 03-bigquery/
|
+-- 04-pubsub/
|
+-- 05-dataflow/
|
+-- 06-dataproc/
|
+-- 07-cloud-run/
|
+-- 08-terraform/
|
+-- 09-gemini/
|
+-- 10-rag/
|
+-- 11-agent-search/
|
+-- 12-adk/
|
+-- 13-multi-agent/
|
+-- 14-mcp/
|
+-- 15-a2a/
|
+-- 16-agent-runtime/
|
+-- 17-evaluation/
|
+-- 18-observability/
|
+-- 19-security/
|
+-- 20-capstone/
|
+-- README.md
```

---

# 47. Capstone Project

Build:

# Enterprise Multi-Agent AI Platform

Architecture:

```text
                              USER
                               |
                               ▼
                         API Gateway
                               |
                               ▼
                          Cloud Run
                               |
                               ▼
                     Agent Orchestrator
                               |
             +-----------------+------------------+
             |                 |                  |
             ▼                 ▼                  ▼
       Research Agent      RAG Agent          SQL Agent
             |                 |                  |
             ▼                 ▼                  ▼
         Search/API       Agent Search         BigQuery
                               |
                               ▼
                        Cloud Storage
```

Model:

```text
Gemini
```

Framework:

```text
ADK
```

Agent communication:

```text
A2A
```

External tools:

```text
MCP
```

Runtime:

```text
Agent Runtime
```

Infrastructure:

```text
Terraform
```

Observability:

```text
Cloud Logging
Cloud Monitoring
Cloud Trace
```

Evaluation:

```text
RAG Evaluation
Agent Evaluation
Model Evaluation
```

---

# 48. Add AWS Integration

Once the Google version works, make it multi-cloud.

```text
                    Enterprise User
                          |
                          ▼
                    Agent Platform
                          |
          +---------------+---------------+
          |                               |
          ▼                               ▼
       GCP                                AWS
          |                               |
       Gemini                         Bedrock
          |                               |
       BigQuery                       S3
          |                               |
     Cloud Storage                  OpenSearch
          |                               |
       ADK Agent                   AgentCore
          |                               |
          +---------------+---------------+
                          |
                         A2A
```

Now you have a genuine:

# Multi-Cloud Agentic AI Platform

---

# 49. What You Should Learn First

Do not try to learn all services simultaneously.

## Phase 1 — GCP Refresh

```text
1. Projects
2. IAM
3. Service Accounts
4. gcloud
5. Cloud Storage
6. VPC
7. Cloud Run
8. Artifact Registry
```

---

# 50. Phase 2 — Data Engineering Refresh

```text
1. BigQuery
2. Pub/Sub
3. Dataflow
4. Dataproc
5. Dataproc Serverless
6. Cloud Storage
7. BigQuery + GCS architecture
```

Your previous Google DE experience should make this phase fast.

---

# 51. Phase 3 — ML

```text
1. Agent Platform
2. Training
3. Model Registry
4. Model deployment
5. Endpoints
6. Pipelines
7. Evaluation
8. Monitoring
```

Map every concept back to SageMaker.

---

# 52. Phase 4 — Gemini

```text
1. Gemini API
2. Google GenAI SDK
3. Streaming
4. Function Calling
5. Structured Output
6. Multimodal
7. Embeddings
8. Grounding
```

Map this to Bedrock.

---

# 53. Phase 5 — RAG

```text
1. Embeddings
2. Chunking
3. Vector Search
4. Agent Search
5. RAG
6. Grounding
7. Metadata filtering
8. Hybrid search
9. Evaluation
```

Map this to:

```text
OpenSearch
+
Bedrock Knowledge Bases
```

---

# 54. Phase 6 — Agents

```text
1. ADK
2. Agents
3. Tools
4. Workflow agents
5. Multi-agent
6. Sessions
7. Memory
8. MCP
9. A2A
10. Agent Runtime
```

This should be your deepest area.

---

# 55. Phase 7 — Production

```text
1. Cloud Run
2. Agent Runtime
3. IAM
4. Service Accounts
5. VPC
6. Secret Manager
7. Cloud KMS
8. Logging
9. Monitoring
10. Trace
11. Evaluation
12. Terraform
13. CI/CD
```

---

# 56. AWS vs GCP Architecture Interview Questions

You should eventually be able to answer:

### Cloud

* AWS Account vs GCP Project?
* IAM Role vs Service Account?
* AWS VPC vs GCP VPC?
* S3 vs GCS?
* ECS vs Cloud Run?
* EKS vs GKE?

### Data

* Redshift vs BigQuery?
* EMR vs Dataproc?
* Glue vs Dataflow?
* Kinesis vs Pub/Sub?
* When would you use Spark versus Apache Beam?

### ML

* SageMaker AI vs Agent Platform?
* SageMaker Endpoint vs Google model deployment?
* SageMaker Pipeline vs Google pipeline?
* Model Registry differences?

### GenAI

* Bedrock vs Gemini?
* Bedrock Model Catalog vs Model Garden?
* Bedrock Knowledge Bases vs Agent Search/RAG?
* Bedrock Agents vs ADK?

### Agents

* Bedrock AgentCore vs Agent Runtime?
* LangGraph vs ADK?
* MCP architecture?
* A2A architecture?
* Agent memory?
* Session management?
* Agent observability?
* Agent evaluation?

---

# 57. The Most Important Architectural Difference

Do not memorize:

```text
SageMaker = Vertex AI
Bedrock = Gemini
```

That is too simplistic.

Instead:

```text
AWS
 |
 +-- SageMaker AI
 |       |
 |       +-- ML lifecycle
 |
 +-- Bedrock
         |
         +-- Foundation Models
         +-- GenAI
         +-- Agents
         +-- AgentCore
```

Google:

```text
Google Cloud
 |
 +-- Agent Platform
        |
        +-- ML
        +-- Gemini
        +-- Model Garden
        +-- RAG
        +-- Search
        +-- ADK
        +-- Agent Runtime
        +-- Evaluation
        +-- Memory
        +-- Sessions
```

Google's direction is increasingly toward a **unified AI + agent platform**.

---

# 58. Your Skill Transfer Matrix

Your existing skill:

```text
AWS S3
```

Learn:

```text
GCS
```

Your existing skill:

```text
AWS Glue
```

Learn:

```text
Dataflow + Dataproc
```

Your existing skill:

```text
EMR
```

Learn:

```text
Dataproc
```

Your existing skill:

```text
Redshift
```

Learn:

```text
BigQuery
```

Your existing skill:

```text
SageMaker
```

Learn:

```text
Agent Platform ML
```

Your existing skill:

```text
Bedrock
```

Learn:

```text
Gemini + Model Garden
```

Your existing skill:

```text
Bedrock Knowledge Bases
```

Learn:

```text
Agent Search + RAG
```

Your existing skill:

```text
Bedrock Agents
```

Learn:

```text
ADK + Agent Runtime
```

Your existing skill:

```text
LangGraph
```

Learn:

```text
ADK
```

Your existing skill:

```text
MCP
```

Learn:

```text
MCP on Google Cloud
```

Your existing skill:

```text
A2A
```

Learn:

```text
A2A with Google agents
```

---

# 59. What Your Final Skillset Should Look Like

At the end of this learning journey:

```text
                 CLOUD ARCHITECT
                       |
        +--------------+--------------+
        |                             |
       AWS                          GCP
        |                             |
 SageMaker AI                  Agent Platform
 Bedrock                       Gemini
 AgentCore                     ADK
 S3                            Agent Runtime
 OpenSearch                    BigQuery
 EMR                           Dataproc
 Glue                          Dataflow
 EKS                           GKE
 ECS                           Cloud Run
        |                             |
        +--------------+--------------+
                       |
                       ▼
               AGENTIC AI PLATFORM
                       |
        +--------------+--------------+
        |              |              |
       RAG            MCP            A2A
        |              |              |
     Search          Tools          Agents
        |
     Evaluation
        |
   Observability
        |
     Security
        |
    Terraform
```

---

# 60. Final Learning Strategy

Because you already have strong AWS experience, use this rule:

> **Every time you learn a Google service, compare it against the AWS service you already know.**

Example:

```text
Learn Dataproc
    ↓
Compare with EMR
    ↓
Understand architectural differences
    ↓
Build Spark job
    ↓
Deploy with Terraform
```

Then:

```text
Learn BigQuery
    ↓
Compare with Redshift
    ↓
Load GCS data
    ↓
Run SQL
    ↓
Connect Gemini
```

Then:

```text
Learn ADK
    ↓
Compare with LangGraph
    ↓
Build Agent
    ↓
Add tools
    ↓
Add MCP
    ↓
Add A2A
    ↓
Deploy to Agent Runtime
```

Finally:

```text
AWS Agent Platform
        +
Google Agent Platform
        ↓
Multi-Cloud Agentic AI Architecture
```

---

# 61. Recommended Order

The complete order is:

```text
01. GCP Projects
02. IAM
03. Service Accounts
04. gcloud CLI
05. Cloud Storage
06. VPC
07. Cloud Run
08. Artifact Registry

09. BigQuery
10. Pub/Sub
11. Dataflow
12. Dataproc
13. Dataproc Serverless

14. Agent Platform fundamentals
15. ML training
16. Model Registry
17. Model deployment
18. Evaluation
19. Monitoring

20. Gemini
21. Google GenAI SDK
22. Streaming
23. Function Calling
24. Structured Output
25. Multimodal
26. Embeddings

27. RAG
28. Agent Search
29. Vector Search
30. Grounding
31. RAG Evaluation

32. ADK
33. Tools
34. Workflow Agents
35. Multi-Agent
36. Sessions
37. Memory
38. MCP
39. A2A

40. Agent Runtime
41. Production deployment
42. Security
43. Observability
44. Terraform
45. CI/CD

46. Enterprise Multi-Agent Platform
47. AWS ↔ GCP Multi-Cloud Architecture
```

---

# 62. Final Goal

Do not aim for:

> "I know Google Cloud."

Aim for:

> **"I can take an enterprise workload currently running on AWS and architect the equivalent solution on Google Cloud, explain the service-level and architectural trade-offs, and build a production-grade GenAI/Agentic AI platform using Gemini, Agent Platform, ADK, RAG, MCP, A2A, BigQuery, Cloud Storage, Cloud Run, Terraform, IAM and observability."**

That is the level that will make your previous **Google Data Engineering experience + 4 years of AWS ML/Bedrock experience + current Agentic AI experience** work together rather than treating them as separate skillsets.
