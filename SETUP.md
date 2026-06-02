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

**Service Principal (recommended)**:
1. In Databricks, go to **Settings → Identity & Access → Service Principals**
2. Create a service principal (or use an existing one)
3. Under the service principal, go to **Secrets → Generate Secret**
4. Copy the **Client ID** and the generated **Secret** into `.env`
5. Grant the service principal **Can Manage** access on the workspace path it will deploy to

**Personal Access Token** (for manual/interactive use):
1. Go to **Settings → Developer → Access Tokens**
2. Click **Generate new token**, set an expiry
3. Copy the token into `.env` as `DATABRICKS_TOKEN`

> **Note**: Do not set both `DATABRICKS_TOKEN` and `DATABRICKS_CLIENT_SECRET` at the same time.  
> The CLI will fail with "more than one authorization method configured".

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
