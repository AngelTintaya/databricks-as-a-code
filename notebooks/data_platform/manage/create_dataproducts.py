# Databricks notebook source
# MAGIC %run ../common/utils

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Product Creator
# MAGIC Reads all `pending` rows and creates the corresponding data products.
# MAGIC Safe to run multiple times — only processes pending rows, existing catalogs are skipped.

# COMMAND ----------

pending = spark.sql("""
    SELECT group, leader, members, domain_code, domain_name, dp_name
    FROM data_platform.admin.dataproduct_requests
    WHERE status = 'pending'
    ORDER BY submitted_at
""").collect()

print(f"Found {len(pending)} pending data product(s)")

# COMMAND ----------

for row in pending:
    group       = row['group']
    leader      = row['leader']
    members     = [m.strip() for m in row['members'].split(',') if m.strip()]
    domain_code = row['domain_code']
    domain_name = row['domain_name']
    dp_name     = row['dp_name']

    try:
        print(f"\n--- {group} / {domain_code} / {dp_name} ---")
        domain = {'code': f'{group.lower()}_{domain_code}', 'name': domain_name}
        generate_dataproduct(domain, dp_name, leader, members)
        spark.sql(f"""
            UPDATE data_platform.admin.dataproduct_requests
            SET status = 'created', processed_at = current_timestamp()
            WHERE group = '{group}' AND domain_code = '{domain_code}'
                AND dp_name = '{dp_name}' AND status = 'pending'
        """)
        print(f"Done.")
    except Exception as e:
        error_msg = str(e)[:500].replace("'", "''")   # ← escape single quotes
        spark.sql(f"""
            UPDATE data_platform.admin.dataproduct_requests
            SET status = 'failed', error = '{error_msg}', processed_at = current_timestamp()
            WHERE group = '{group}' AND domain_code = '{domain_code}'
                AND dp_name = '{dp_name}' AND status = 'pending'
        """)
        print(f"FAILED: {e}")

# COMMAND ----------

spark.sql("""
    SELECT group, domain_code, domain_name, dp_name, status, submitted_at, processed_at, error
    FROM data_platform.admin.dataproduct_requests
    ORDER BY group, submitted_at
""").display()
