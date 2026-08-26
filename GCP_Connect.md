Yes. If you want this README to be **truly end-to-end from a completely new Mac**, it should start with installing the Google Cloud CLI, then authentication, project setup, billing/API setup, Gemini, Storage, BigQuery, and ADK.

Here is the recommended sequence.

# Google Cloud + Gemini + ADK — Complete Mac Setup

## 0. What we will install

```text
macOS
  ↓
Homebrew
  ↓
Google Cloud CLI
  ↓
gcloud authentication
  ↓
Google Cloud Project
  ↓
Billing / $300 Free Trial
  ↓
Vertex AI
  ↓
Gemini
  ↓
Cloud Storage
  ↓
BigQuery
  ↓
Python + Virtual Environment
  ↓
Google Gen AI SDK
  ↓
Google ADK
```

---

# 1. Install Homebrew

Check whether Homebrew is already installed:

```bash
brew --version
```

If you get `command not found`, install it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

After installation, verify:

```bash
brew --version
```

On Apple Silicon Macs, make sure Homebrew is available:

```bash
which brew
```

Typically:

```text
/opt/homebrew/bin/brew
```

---

# 2. Install Google Cloud CLI

Install:

```bash
brew install --cask google-cloud-sdk
```

Verify:

```bash
gcloud --version
```

You should see something similar to:

```text
Google Cloud SDK ...
gcloud ...
gsutil ...
bq ...
```

---

# 3. Initialize Google Cloud CLI

Run:

```bash
gcloud init
```

A browser will open.

Select your Google account:

```text
mamathaanjireddy@gmail.com
```

Then select your Google Cloud project if prompted:

```text
project-52e8c95d-822f-4563-a7e
```

If you prefer to configure manually, you can skip project selection during `gcloud init` and do:

```bash
gcloud auth login mamathaanjireddy@gmail.com
```

Then:

```bash
gcloud config set account mamathaanjireddy@gmail.com
```

And:

```bash
gcloud config set project project-52e8c95d-822f-4563-a7e
```

---

# 4. Verify Google Cloud CLI

```bash
gcloud auth list
```

Expected:

```text
Credentialed Accounts

ACTIVE  ACCOUNT
*       mamathaanjireddy@gmail.com
```

Check project:

```bash
gcloud config get-value project
```

Expected:

```text
project-52e8c95d-822f-4563-a7e
```

Check complete configuration:

```bash
gcloud config list
```

---

# 5. Verify Project Access

Run:

```bash
gcloud projects describe project-52e8c95d-822f-4563-a7e
```

If successful, your account can access the project.

You can also list accessible projects:

```bash
gcloud projects list
```

---

# 6. Check Billing

If you have the Google Cloud $300 Free Trial, check which billing account is available:

```bash
gcloud billing accounts list
```

Then:

```bash
gcloud billing projects describe \
  project-52e8c95d-822f-4563-a7e
```

You want the project to have an active billing account.

> The $300 Google Cloud Free Trial is generally valid for 90 days. Eligible Google Cloud services can consume the credit.

---

# 7. Configure Application Default Credentials

This is important for Python, Gemini SDK, ADK, BigQuery SDK, Storage SDK, etc.

Run:

```bash
gcloud auth application-default login
```

Select:

```text
mamathaanjireddy@gmail.com
```

Then:

```bash
gcloud auth application-default set-quota-project \
  project-52e8c95d-822f-4563-a7e
```

Test:

```bash
gcloud auth application-default print-access-token
```

You should receive an access token.

**Never share this token.**

---

# 8. Enable Required APIs

Enable Vertex AI:

```bash
gcloud services enable aiplatform.googleapis.com
```

Storage:

```bash
gcloud services enable storage.googleapis.com
```

BigQuery:

```bash
gcloud services enable bigquery.googleapis.com
```

Optional BigQuery APIs:

```bash
gcloud services enable \
  bigqueryconnection.googleapis.com \
  bigquerydatatransfer.googleapis.com
```

Or everything together:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  bigqueryconnection.googleapis.com \
  bigquerydatatransfer.googleapis.com
```

Verify:

```bash
gcloud services list --enabled | grep -E \
'aiplatform|storage|bigquery'
```

---

# 9. Install Python

Check:

```bash
python3 --version
```

If Python isn't installed, use Homebrew:

```bash
brew install python
```

Verify:

```bash
python3 --version
pip3 --version
```

---

# 10. Create Your AI Project

For example:

```bash
mkdir -p ~/google-genai-project
cd ~/google-genai-project
```

Create virtual environment:

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

Verify:

```bash
which python
```

You should see:

```text
.../google-genai-project/.venv/bin/python
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

---

# 11. Set Google Cloud Environment Variables

```bash
export GOOGLE_CLOUD_PROJECT="project-52e8c95d-822f-4563-a7e"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
```

Verify:

```bash
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_LOCATION
echo $GOOGLE_GENAI_USE_VERTEXAI
```

Expected:

```text
project-52e8c95d-822f-4563-a7e
us-central1
true
```

---

# 12. Install Google Gen AI SDK

```bash
pip install -U google-genai
```

Verify:

```bash
pip show google-genai
```

---

# 13. First Gemini Test

Create:

```bash
touch test_gemini.py
```

Put this inside:

```python
from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain agentic AI in three sentences.",
)

print(response.text)
```

Run:

```bash
python test_gemini.py
```

If you get a Gemini response:

```text
Gemini is working.
```

Your first major milestone is complete.

---

# 14. Test Gemini Streaming

Create:

```bash
touch test_gemini_stream.py
```

```python
from google import genai

client = genai.Client()

response = client.models.generate_content_stream(
    model="gemini-2.5-flash",
    contents="Explain Google ADK in detail.",
)

for chunk in response:
    if chunk.text:
        print(chunk.text, end="", flush=True)

print()
```

Run:

```bash
python test_gemini_stream.py
```

---

# 15. Install Google ADK

```bash
pip install -U google-adk
```

Verify:

```bash
adk --version
```

And:

```bash
pip show google-adk
```

---

# 16. Install Cloud Storage SDK

```bash
pip install -U google-cloud-storage
```

Test:

```python
from google.cloud import storage

client = storage.Client()

for bucket in client.list_buckets():
    print(bucket.name)
```

---

# 17. Cloud Storage CLI

List buckets:

```bash
gcloud storage ls
```

Create a test bucket:

```bash
export GCS_BUCKET="project-52e8c95d-822f-4563-a7e-test"
```

```bash
gcloud storage buckets create \
  gs://$GCS_BUCKET \
  --location=us-central1
```

List:

```bash
gcloud storage ls
```

Create a file:

```bash
echo "Hello Google Cloud" > test.txt
```

Upload:

```bash
gcloud storage cp \
  test.txt \
  gs://$GCS_BUCKET/
```

List objects:

```bash
gcloud storage ls gs://$GCS_BUCKET/
```

Download:

```bash
gcloud storage cp \
  gs://$GCS_BUCKET/test.txt \
  ./downloaded.txt
```

Delete test object:

```bash
gcloud storage rm \
  gs://$GCS_BUCKET/test.txt
```

Delete test bucket:

```bash
gcloud storage buckets delete \
  gs://$GCS_BUCKET
```

---

# 18. BigQuery CLI

Check:

```bash
bq version
```

List datasets:

```bash
bq ls \
  --project_id=project-52e8c95d-822f-4563-a7e
```

---

# 19. Test BigQuery

```bash
bq query \
  --use_legacy_sql=false \
  'SELECT 1 AS test'
```

Expected:

```text
+------+
| test |
+------+
|    1 |
+------+
```

Test timestamp:

```bash
bq query \
  --use_legacy_sql=false \
  'SELECT CURRENT_TIMESTAMP() AS current_time'
```

---

# 20. Create a BigQuery Dataset

```bash
bq --location=us-central1 mk \
  --dataset \
  project-52e8c95d-822f-4563-a7e:genai_demo
```

List:

```bash
bq ls \
  --project_id=project-52e8c95d-822f-4563-a7e
```

---

# 21. Install BigQuery Python SDK

```bash
pip install -U google-cloud-bigquery
```

Test:

```python
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT
    1 AS id,
    "Google Cloud" AS platform
"""

for row in client.query(query):
    print(row.id, row.platform)
```

Run:

```bash
python test_bigquery.py
```

---

# 22. Install Everything Together

Once the individual tests work:

```bash
pip install -U \
  google-genai \
  google-adk \
  google-cloud-storage \
  google-cloud-bigquery
```

Save dependencies:

```bash
pip freeze > requirements.txt
```

---

# 23. Complete Architecture

```text
                    macOS
                      |
                      v
                  Homebrew
                      |
                      v
              Google Cloud CLI
                      |
                      v
               gcloud auth
                      |
                      v
        mamathaanjireddy@gmail.com
                      |
                      v
      project-52e8c95d-822f-4563-a7e
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
    Vertex AI     Storage       BigQuery
        |
        v
     Gemini
        |
        v
 Google Gen AI SDK
        |
        v
    Google ADK
        |
        +---- Agents
        +---- Tools
        +---- MCP
        +---- A2A
        +---- Workflows
        +---- Streaming
```

---

# 24. Final Health Check

Run everything:

```bash
echo "=============================="
echo "Google Cloud Health Check"
echo "=============================="

echo ""
echo "Account:"
gcloud config get-value account

echo ""
echo "Project:"
gcloud config get-value project

echo ""
echo "Google Cloud CLI:"
gcloud --version | head -1

echo ""
echo "Enabled APIs:"
gcloud services list --enabled | \
grep -E 'aiplatform|storage|bigquery'

echo ""
echo "Cloud Storage:"
gcloud storage ls

echo ""
echo "BigQuery:"
bq --project_id="$GOOGLE_CLOUD_PROJECT" ls

echo ""
echo "Environment:"
echo "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT"
echo "GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION"
echo "GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"

echo ""
echo "Python:"
python --version

echo ""
echo "Google Gen AI:"
pip show google-genai | grep Version

echo ""
echo "Google ADK:"
adk --version

echo ""
echo "=============================="
echo "Health Check Complete"
echo "=============================="
```

---

# 25. The Complete Fresh-Mac Command Sequence

If you're starting from essentially nothing, the sequence is:

```bash
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Google Cloud CLI
brew install --cask google-cloud-sdk

# 3. Verify
gcloud --version

# 4. Login
gcloud auth login mamathaanjireddy@gmail.com

# 5. Set account
gcloud config set account mamathaanjireddy@gmail.com

# 6. Set project
gcloud config set project project-52e8c95d-822f-4563-a7e

# 7. Configure ADC
gcloud auth application-default login

# 8. Set ADC quota project
gcloud auth application-default set-quota-project \
  project-52e8c95d-822f-4563-a7e

# 9. Enable APIs
gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  bigqueryconnection.googleapis.com \
  bigquerydatatransfer.googleapis.com

# 10. Install Python
brew install python

# 11. Create project
mkdir -p ~/google-genai-project
cd ~/google-genai-project

# 12. Create virtual environment
python3 -m venv .venv

# 13. Activate
source .venv/bin/activate

# 14. Upgrade pip
python -m pip install --upgrade pip

# 15. Configure environment
export GOOGLE_CLOUD_PROJECT="project-52e8c95d-822f-4563-a7e"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"

# 16. Install Google AI packages
pip install -U \
  google-genai \
  google-adk \
  google-cloud-storage \
  google-cloud-bigquery

# 17. Verify Storage
gcloud storage ls

# 18. Verify BigQuery
bq ls

# 19. Verify Gemini
python test_gemini.py

# 20. Verify ADK
adk --version
```

### Your final stack

```text
Google Cloud CLI
        +
Google Cloud Authentication
        +
ADC
        +
Vertex AI
        +
Gemini
        +
Google Gen AI SDK
        +
Google ADK
        +
Cloud Storage
        +
BigQuery
```

This is the setup I would use for your **Google ADK workflow-patterns project**, especially if you're going to experiment with Gemini agents, MCP, A2A, streaming, RAG, BigQuery, and Cloud Storage.
