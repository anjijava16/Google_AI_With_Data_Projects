# Google_AI_With_Data_Projects
Google Cloud GenAI With AI and Data Projects

# Create the New Python 3.12 Environment
1. python3.12 -m venv .venv


# Activate and Verify

source .venv/bin/activate

python --version



# Install Google Cloud CLI

```

((.venv) ) (base) welcome@jaisairams-Laptop Google_AI_With_Data_Projects % gcloud --version
Google Cloud SDK 581.0.0
beta 2026.08.14
bq 2.1.37
bundled-python3-unix 3.14.5
core 2026.08.14
gcloud-crc32c 1.0.0
gsutil 5.37
((.venv) ) (base) welcome@jaisairams-Laptop Google_AI_With_Data_Projects % 


Creating virtualenv...
Installing modules...
Virtual env enabled.
==> Purging files for version 560.0.0 of Cask gcloud-cli
🍺  gcloud-cli was successfully upgraded!
==> `brew cleanup` has not been run in the last 30 days, running now...
Disable this behaviour by setting `HOMEBREW_NO_INSTALL_CLEANUP=1`.
Hide these hints with `HOMEBREW_NO_ENV_HINTS=1` (see `man brew`).
Removing: /Users/welcome/Library/Caches/Homebrew/portable-ruby-4.0.5_1.arm64_big_sur.bottle.tar.gz... (12.7MB)
Removing: /Users/welcome/Library/Caches/Homebrew/Cask/copilot-darwin-arm64.tar.gz--1.0.34.tar.gz... (55.1MB)
Removing: /Users/welcome/Library/Caches/Homebrew/bootsnap/16e4b77f396cb05f9c9d7cc3db325ed737f1a41f52ffbca011c77ad70f50850b... (1,036 files, 9.2MB)
Removing: /Users/welcome/Library/Caches/Homebrew/bootsnap/14e9983d8f21ebd1759b5d12e5a0f648a2e5b645d0e27f72867e9cb6262257d9... (1,045 files, 9.3MB)
Removing: /Users/welcome/Library/Caches/Homebrew/bootsnap/148d3a0082c45793313d4cfa2955969a9805ea8fb6e34e5cf51ee0d39c52a728... (1,045 files, 9.4MB)
Removing: /Users/welcome/Library/Logs/Homebrew/databricks... (121B)
Removing: /Users/welcome/Library/Logs/Homebrew/eksctl... (117B)
Removing: /Users/welcome/Library/Logs/Homebrew/ca-certificates... (64B)
Pruned 0 symbolic links and 1 directories from /opt/homebrew
==> Caveats
==> gcloud-cli
To use additional binary components installed via gcloud, add the "/opt/homebrew/share/google-cloud-sdk/bin"
directory to your PATH environment variable, e.g., (for Bash shell):
   export PATH=/opt/homebrew/share/google-cloud-sdk/bin:"$PATH"
((.venv) ) (base) welcome@jaisairams-Laptop Google_AI_With_Data_Projects % 



```

# Initialize Google Cloud CLI


```

((.venv) ) (base) welcome@jaisairams-Laptop Google_AI_With_Data_Projects % gcloud init
Welcome! This command will take you through the configuration of gcloud.

Settings from your current configuration [default] are:
core:
  account: mamathaanjireddy@gmail.com
  disable_usage_reporting: 'False'
  project: project-52e8c95d-822f-4563-a7e

Pick configuration to use:
 [1] Re-initialize this configuration [default] with new settings 
 [2] Create a new configuration
Please enter your numeric choice:  

```

## Setup & Verify

```
gcloud config set account mamathaanjireddy@gmail.com

gcloud config set project project-52e8c95d-822f-4563-a7e


gcloud auth list

gcloud config get-value account

gcloud config get-value project

```

## Configure ADC for Python / GenAI / ADK

1. gcloud auth application-default revoke
2. gcloud auth application-default login 


## Enable the APIS you need & Check

```

gcloud services enable \
  aiplatform.googleapis.com \
  storage.googleapis.com \
  bigquery.googleapis.com \
  bigqueryconnection.googleapis.com \
  bigquerydatatransfer.googleapis.com

 Check

 gcloud services list --enabled

```

## End to end Commands

```

 3. Verify
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
mkdir -p ~/google-genai-repo
cd ~/google-genai-repo

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

```