# Databricks Asset Bundle Setup Guide

This project uses Databricks Asset Bundles (DAB) to manage and deploy notebooks to your Databricks workspace from VS Code.

## Prerequisites

1. **Install Databricks CLI (v0.200+ with bundle support)**
   ```bash
   # Using Homebrew (macOS/Linux)
   brew tap databricks/tap
   brew install databricks
   
   # Verify installation
   databricks --version
   ```
   Note: The pip version (0.18.0) doesn't support bundles. Use Homebrew for the newer CLI.

2. **Install Python dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```
   This includes:
   - Databricks SDK
   - python-dotenv (auto-loads .env credentials)

3. **VS Code Extension**: Install the official Databricks extension
   - Search for "Databricks" in VS Code extensions
   - Install the official Databricks extension by Databricks, Inc.

## Configuration

### 1. Set up your credentials in `.env`

Edit the `.env` file with your workspace credentials:

```bash
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your_personal_access_token_here
```

**How to get your credentials:**

1. **Host URL**: Your Databricks workspace URL (e.g., `https://adb-1234567890.cloud.databricks.com`)
2. **Personal Access Token**:
   - In Databricks, go to Settings → User Settings → Developer → Access tokens
   - Click "Generate new token"
   - Copy the token and paste in `.env`

### 2. Environment variables

The `.env` file will be automatically loaded by Python scripts (via `python-dotenv`). If you need to use CLI commands directly, you can load them manually:

```bash
# Optional: Load the .env file for CLI commands
export $(cat .env | xargs)
```

## Using Databricks Asset Bundle

### Deploy the bundle

```bash
# Validate bundle configuration
databricks bundle validate

# Deploy notebooks to your workspace
databricks bundle deploy

# View deployed resources
databricks bundle show
```

### Create new notebooks

1. Create a new `.py` file in the `notebooks/` directory
2. Use the comment format below to structure your notebook:

```python
# Databricks notebook source

# COMMAND ----------

# Your code here
print("Hello, Databricks!")

# COMMAND ----------

# More cells
spark.sql("SELECT 1 as number").display()
```

3. Update `databricks.yml` to include your new notebook:

```yaml
resources:
  notebooks:
    my_new_notebook:
      path: ./notebooks/my_new_notebook
      language: PYTHON
      object_type: DIRECTORY
      format: SOURCE
```

### Sync notebooks with VS Code

1. Open the Databricks extension in VS Code
2. Click "Connect to Workspace"
3. Enter your workspace URL and personal access token
4. Browse and edit notebooks directly in VS Code
5. Changes sync automatically to your workspace

## Updating your notebook in Databricks

After making changes locally:

```bash
# Re-deploy the bundle
databricks bundle deploy --force
```

## Troubleshooting

### Databricks CLI not found or wrong version
```bash
# Install via Homebrew (required for bundle support)
brew tap databricks/tap
brew install databricks

# Check version (should be 0.200+)
databricks --version
```

### Python dependencies not installed
```bash
pip3 install -r requirements.txt
python3 validate_databricks.py
```

### "Authentication failed" error
- Verify your `DATABRICKS_HOST` and `DATABRICKS_TOKEN` in `.env`
- For CLI commands, export variables: `export $(cat .env | xargs)`
- Python scripts auto-load from `.env`

### Notebooks not appearing in workspace
- Run `databricks bundle deploy` again
- Check the workspace path defined in `databricks.yml`
- Verify the bundle is deployed: `databricks bundle show`

### VS Code extension not connecting
- Ensure the official Databricks extension is installed
- Reload VS Code after installing
- Check your workspace URL format (should start with `https://`)

## Environment Variables

The `databricks.yml` reads credentials from environment variables:
- `DATABRICKS_HOST` - Your workspace URL
- `DATABRICKS_TOKEN` - Your personal access token

Python scripts automatically load from `.env` via `python-dotenv`. For CLI commands, load with:
```bash
export $(cat .env | xargs)
```

## Security Notes

- ✅ `.env` is in `.gitignore` - credentials won't be committed
- ✅ Keep your personal access token confidential
- ✅ Rotate tokens regularly for security
- ⚠️ Never commit credentials to version control
