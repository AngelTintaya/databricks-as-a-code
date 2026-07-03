# Setup Guide

Step-by-step instructions to configure and deploy this project to your Databricks workspace.

---

## Prerequisites

### 1. Databricks CLI (via Homebrew)

The bundle and job features require the **new** Databricks CLI (v1.0+). The legacy pip version (v0.18) does not support bundles.

```bash
brew tap databricks/tap
brew install databricks

# Verify — should show 1.x.x
databricks --version
```

### 2. Python dependencies

```bash
pip3 install -r requirements.txt
```

The only runtime dependency is `python-dotenv`, used by `validate_databricks.py` to load `.env`.

---

## Configuration

### 1. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` with your workspace credentials:

```bash
DATABRICKS_HOST=https://your-workspace.azuredatabricks.net

# Service Principal OAuth M2M (recommended for pipelines)
DATABRICKS_CLIENT_ID=your_service_principal_client_id
DATABRICKS_CLIENT_SECRET=your_service_principal_client_secret

# Alternative: Personal Access Token (for interactive use)
# DATABRICKS_TOKEN=your_personal_access_token
```

### 2. Get your credentials

#### Service Principal (recommended for all automation)

A **Service Principal (SP)** is a non-human identity used by applications and scripts to authenticate to Databricks. It is preferred over a Personal Access Token because it does not expire on a schedule, can have scoped permissions, and works in CI/CD without being tied to a person's account.

This project uses the SP for two things:
- **CLI authentication** — the Databricks CLI (`~/.databrickscfg`) uses the SP to deploy bundles and manage secrets
- **Notebook authentication** — the `data_platform` notebooks call the Databricks account-level SCIM API to create groups and manage users; this requires an account-level OAuth token fetched using the SP credentials at runtime via `dbutils.secrets`

**Creating a Service Principal (Azure Databricks):**

1. Go to **Azure Portal → Microsoft Entra ID → App registrations → New registration**
2. Give it a name (e.g. `databricks-sp-de`) and click **Register**
3. Copy the **Application (client) ID** — this is your `DATABRICKS_CLIENT_ID`
4. Go to **Certificates & secrets → New client secret**, set an expiry, click **Add**
5. Copy the **Value** immediately (it is only shown once) — this is your `DATABRICKS_CLIENT_SECRET`
6. Now register the SP in Databricks: go to your workspace → **Settings → Identity & Access → Service Principals → Add service principal**, search for the app name you just created

> **Secret expiry**: The client secret has an expiry date you choose (max 24 months on Azure). When it expires, repeat steps 4–5 and update `.env`, `~/.databrickscfg`, and the Databricks secret scope.

**Granting Account Admin role** (required for `data_platform` notebooks):

The SCIM API calls in `data_platform/common/utils.py` create and manage groups at the **account level** (not workspace level), which requires the SP to have the Account Admin role.

1. Go to `https://accounts.azuredatabricks.net`
2. Navigate to **User Management → Service Principals**
3. Find your SP and assign it the **Account Admin** role

**Configuring the CLI to use the SP:**

Edit `~/.databrickscfg` (your home directory, e.g. `/Users/yourname/.databrickscfg`):

```ini
[DEFAULT]
host = https://your-workspace.azuredatabricks.net/
client_id = your_service_principal_client_id
client_secret = your_service_principal_client_secret
```

Verify it works:
```bash
databricks auth describe
# Should show: Authenticated with: oauth-m2m
```

> Do not put `token =` and `client_secret =` in the same profile — the CLI will fail with "more than one authorization method configured".

**Storing SP credentials as Databricks secrets** (required for `data_platform` notebooks):

The `data_platform/common/_params.py` notebook reads the SP credentials from a secret scope at runtime to fetch an account-level OAuth token. Store them once using the CLI:

```bash
databricks secrets put-secret de-scope sp-client-id --string-value "your_client_id"
databricks secrets put-secret de-scope sp-client-secret --string-value "your_client_secret"
```

Verify:
```bash
databricks secrets list-secrets de-scope
# Should list: sp-client-id, sp-client-secret (values are always redacted)
```

---

#### Personal Access Token (for quick interactive use only)

A **PAT** is a token tied to your personal Databricks user account. It is simpler to create but not recommended for automation because it expires, is tied to a person, and has no granular scoping.

1. Go to your Databricks workspace → **Settings → Developer → Access Tokens**
2. Click **Generate new token**, give it a name and expiry
3. Copy the token — it is only shown once
4. Add it to `.env` as `DATABRICKS_TOKEN`, or to `~/.databrickscfg` as `token =`

> The `data_platform` notebooks **cannot use a PAT** for group management because account-level SCIM API requires an OAuth token from a service principal with Account Admin role — a workspace PAT does not have that scope.

### 3. Validate your setup

```bash
python3 validate_databricks.py
```

This checks that your `.env` exists, credentials are set, the CLI is installed, and `databricks.yml` is present.

---

## Deploy

### Load credentials for CLI commands

```bash
export $(grep -v '^#' .env | grep -v '^$' | xargs)
```

> The `grep` filters out comment lines and blank lines, which would cause `export` to fail.

### Validate the bundle

```bash
databricks bundle validate
```

This parses `databricks.yml`, resolves all paths, and checks connectivity to your workspace. Fix any errors here before deploying.

### Deploy

```bash
databricks bundle deploy
```

This uploads all notebooks to:
```
/Workspace/Projects/databricks-notebooks/dev/files/
```

And creates the Databricks Job **"DE Class — E-Commerce Pipeline"** in your workspace.

---

## Running the pipeline

After deploying, you can trigger the job from the Databricks UI or via CLI:

```bash
databricks bundle run ecommerce_pipeline
```

To run for a specific date (useful for backfilling):
```bash
databricks bundle run ecommerce_pipeline \
  --python-named-params "run_date=2024-01-15"
```

To run only a specific task:
```bash
databricks bundle run ecommerce_pipeline --task bronze_ingest
```

---

## Workspace permissions

The service principal needs **Can Manage** access on the deploy path.

To grant access:
1. In Databricks, browse to **Workspace → Projects**
2. Right-click the target folder → **Permissions**
3. Add the service principal with **Can Manage** permission

---

## Adding new notebooks

1. Create a `.py` file in `notebooks/` using the Databricks notebook format:

```python
# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # My Notebook

# COMMAND ----------

print("Hello, Databricks!")
```

2. Add a task for it in `databricks.yml` under `resources.jobs.ecommerce_pipeline.tasks`
3. Re-deploy: `databricks bundle deploy`

---

## Destroying the deployment

```bash
databricks bundle destroy
```

This removes the uploaded files and deletes the job from Databricks. It does **not** drop the Delta tables — run `99_cleanup.py` interactively for that.

---

## Troubleshooting

**`export` fails with "not valid in this context"**  
Your `.env` has comment lines. Use the filtered export:
```bash
export $(grep -v '^#' .env | grep -v '^$' | xargs)
```

**401 Unauthorized**  
- Check that `DATABRICKS_HOST` is correct (full URL including `https://`)
- Ensure only one auth method is set (`CLIENT_SECRET` or `TOKEN`, not both)
- Verify the secret/token has not expired

**403 Permission Denied on deploy**  
The service principal lacks write access to the deploy path. See [Workspace permissions](#workspace-permissions) above.

**`bundle` command not found**  
You have the legacy CLI (v0.18). Reinstall via Homebrew:
```bash
brew tap databricks/tap && brew install databricks
```

**Validation OK but job not visible in UI**  
Run `databricks bundle deploy` — `validate` only checks the config, it does not deploy.

---

## Security notes

- `.env` is in `.gitignore` — credentials are never committed
- Rotate service principal secrets before their expiry date
- In CI/CD, inject credentials as environment variables or GitHub Secrets — never hardcode them
