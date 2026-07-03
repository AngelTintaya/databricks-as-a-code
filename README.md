# Databricks as Code

Deploy and orchestrate Databricks notebooks using **Databricks Asset Bundles (DABs)** and the Databricks CLI — no manual workspace clicking required.

This project includes a production-inspired pipeline built for a **Master's-level Data Engineering class**, demonstrating real-world patterns for idempotency, retries, structured logging, data quality, and observability using Delta tables.

---

## What's in this project

### Pipeline — E-Commerce Order Processing

A Bronze → Silver → Gold pipeline that processes synthetic e-commerce orders daily.

```
notebooks/jobs/ecommerce_pipeline/
  00_setup.py          Create Unity Catalog schema and Delta tables (idempotent)
  01_bronze_ingest.py  Generate orders, write to Bronze with MERGE
  02_silver_clean.py   Validate, clean, and enrich Bronze → Silver
  03_gold_aggregate.py Aggregate daily revenue by category → Gold
  04_data_quality.py   End-to-end DQ gate; raises exception to trigger alerts
  99_cleanup.py        Drop schema for demo reset (not part of the job)
```

**Job DAG** (each task depends on the previous):
```
setup → bronze_ingest → silver_clean → gold_aggregate → data_quality
```

### Engineering patterns demonstrated

| Pattern | Where |
|---|---|
| Idempotent writes | Delta `MERGE ON order_id` in every task |
| Notebook parameters | `dbutils.widgets` — job passes `catalog`, `run_date` at runtime |
| Deterministic data | Seeded RNG: same `run_date` → same records on retry |
| Audit columns | `_ingested_at`, `_batch_id`, `_processed_at`, `_source_batch_id` |
| Automatic retries | `max_retries: 2` per task in `databricks.yml` |
| Structured logging | JSON metrics via `log.info()` + `dbutils.notebook.exit()` |
| DQ gate | Task 04 raises `Exception` → triggers retries → then email alert |
| Email alerts | `email_notifications.on_failure` in `databricks.yml` |
| Delta versioning | Every run creates a new Delta version; query with `VERSION AS OF` |
| Health monitoring | `health.rules` fires if total run exceeds 30 minutes |

---

## Project structure

```
databricks-as-a-code/
├── notebooks/
│   ├── sample_notebook.py               Starter notebook
│   └── jobs/
│       └── ecommerce_pipeline/          Pipeline notebooks (tasks)
├── databricks.yml                       Bundle + job definition
├── .env                                 Credentials (git-ignored)
├── .env.example                         Credentials template
├── validate_databricks.py               Pre-flight environment check
├── requirements.txt                     Python dependencies
└── SETUP.md                             Step-by-step setup guide
```

---

## Quick start

```bash
# 1. Copy and fill in credentials
cp .env.example .env

# 2. Validate your setup
python3 validate_databricks.py

# 3. Load credentials for CLI commands
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# 4. Validate the bundle
databricks bundle validate

# 5. Deploy
databricks bundle deploy
```

See [SETUP.md](SETUP.md) for full installation and configuration instructions.

---

## Authentication

This project uses **Service Principal (SP) OAuth M2M** authentication throughout — for the CLI, for bundle deployment, and for the `data_platform` notebooks.

| Credential | Where it's used |
|---|---|
| `DATABRICKS_HOST` | Workspace URL — used by CLI and `.env` |
| `DATABRICKS_CLIENT_ID` | SP application ID — CLI auth + notebook secret |
| `DATABRICKS_CLIENT_SECRET` | SP secret — CLI auth + notebook secret |

The SP needs two levels of access:
- **Workspace** — to deploy bundles and manage secrets via the CLI
- **Account Admin** — to create and manage Unity Catalog groups via the SCIM API (used by `data_platform` notebooks)

Personal Access Tokens (PATs) are supported for interactive CLI use but cannot be used for the `data_platform` notebooks — those require an account-level OAuth token that only a service principal can obtain.

See [SETUP.md](SETUP.md#2-get-your-credentials) for full step-by-step instructions on creating the SP, granting roles, configuring `~/.databrickscfg`, and storing secrets.

---

## Deploy path

Notebooks and the job are deployed to:
```
/Workspace/Projects/databricks-notebooks/dev/
```

Configured via `root_path` in `databricks.yml`. Change `dev` to `staging` or `prod` by adding a new target.
