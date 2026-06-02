#!/usr/bin/env python3
"""
Validate Databricks connection and credentials
"""

import os
import sys
from pathlib import Path

# Load .env file automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv not installed. Run: pip install -r requirements.txt")
    print("   Or load manually: export $(cat .env | xargs)\n")


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        return False
    print("✅ .env file found")
    return True


def check_credentials():
    """Check if environment variables are set"""
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")

    if not host:
        print("❌ DATABRICKS_HOST not set in .env")
        return False
    print(f"✅ DATABRICKS_HOST: {host}")

    if not token:
        print("❌ DATABRICKS_TOKEN not set in .env")
        return False

    # Don't print the full token, just confirm it exists
    print(f"✅ DATABRICKS_TOKEN: {'*' * len(token)}")
    return True


def check_databricks_cli():
    """Check if Databricks CLI is installed"""
    import subprocess
    try:
        result = subprocess.run(
            ["databricks", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Databricks CLI: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ Databricks CLI not installed")
    print("   Install with: pip install databricks-cli")
    return False


def check_bundle_config():
    """Check if databricks.yml exists"""
    config_path = Path("databricks.yml")
    if not config_path.exists():
        print("❌ databricks.yml not found")
        return False
    print("✅ databricks.yml found")
    return True


def check_notebooks_directory():
    """Check if notebooks directory exists"""
    notebooks_path = Path("notebooks")
    if not notebooks_path.exists():
        print("❌ notebooks/ directory not found")
        return False

    py_files = list(notebooks_path.glob("*.py"))
    print(f"✅ notebooks/ directory found ({len(py_files)} notebook files)")
    return True


def main():
    print("\n🔍 Validating Databricks Asset Bundle Setup\n")

    checks = [
        ("Config Files", check_env_file),
        ("Credentials", check_credentials),
        ("Databricks CLI", check_databricks_cli),
        ("Bundle Configuration", check_bundle_config),
        ("Notebooks Directory", check_notebooks_directory),
    ]

    results = []
    for name, check in checks:
        print(f"\n📋 Checking {name}...")
        results.append(check())

    print("\n" + "=" * 50)
    if all(results):
        print("✅ All checks passed!")
        print("\nNext steps:")
        print("1. export $(cat .env | xargs)")
        print("2. databricks bundle validate")
        print("3. databricks bundle deploy")
    else:
        print("❌ Some checks failed - see above for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
