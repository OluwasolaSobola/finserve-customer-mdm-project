"""
Reproduce the MDM portfolio validation results using Python's built-in sqlite3.
No external packages are required.

Run from the repository root:
    python validation/run_mdm_validation.py
"""
from pathlib import Path
import csv, sqlite3, re

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "customer_source_records.csv"
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

conn = sqlite3.connect(":memory:")
conn.create_function(
    "REGEXP_REPLACE", 4,
    lambda value, pattern, replacement, flags: re.sub(pattern, replacement, value or "")
)
conn.execute("""
CREATE TABLE customer_source_records (
    source_system TEXT, source_customer_id TEXT, full_name TEXT, dob TEXT,
    email TEXT, phone TEXT, address TEXT, customer_status TEXT,
    nationality TEXT, account_number TEXT, last_updated TEXT
)
""")

with RAW.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = [
        (r["source_system"], r["source_customer_id"], r["full_name"], r["dob"],
         r["email"], r["phone"], r["address"], r["customer_status"],
         r["nationality"], r["account_number"], r["last_updated"])
        for r in reader
    ]
conn.executemany("INSERT INTO customer_source_records VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)

queries = {
" dq_summary.csv": """
SELECT COUNT(*) AS total_records,
       SUM(CASE WHEN dob IS NULL OR dob = '' THEN 1 ELSE 0 END) AS missing_dob,
       SUM(CASE WHEN email IS NULL OR email NOT LIKE '%@%.%' THEN 1 ELSE 0 END) AS invalid_email
FROM customer_source_records
""",
"potential_matches.csv": """
WITH normalised AS (
  SELECT *, LOWER(TRIM(email)) AS email_n,
         REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_n
  FROM customer_source_records
)
SELECT a.source_customer_id AS record_a,
       b.source_customer_id AS record_b,
       CASE WHEN a.dob = b.dob THEN 1 ELSE 0 END AS dob_match,
       CASE WHEN a.email_n = b.email_n THEN 1 ELSE 0 END AS email_match,
       CASE WHEN a.phone_n = b.phone_n THEN 1 ELSE 0 END AS phone_match,
       (CASE WHEN a.dob = b.dob THEN 1 ELSE 0 END +
        CASE WHEN a.email_n = b.email_n THEN 1 ELSE 0 END +
        CASE WHEN a.phone_n = b.phone_n THEN 1 ELSE 0 END) AS match_count
FROM normalised a
JOIN normalised b ON a.source_customer_id < b.source_customer_id
WHERE (CASE WHEN a.dob = b.dob THEN 1 ELSE 0 END +
       CASE WHEN a.email_n = b.email_n THEN 1 ELSE 0 END +
       CASE WHEN a.phone_n = b.phone_n THEN 1 ELSE 0 END) >= 2
ORDER BY match_count DESC, record_a, record_b
""",
"steward_exceptions.csv": """
WITH normalised AS (
  SELECT *, LOWER(TRIM(email)) AS email_n,
         REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_n
  FROM customer_source_records
)
SELECT a.source_customer_id AS record_a,
       b.source_customer_id AS record_b,
       a.dob AS dob_a, b.dob AS dob_b,
       a.email_n AS email_normalised,
       a.phone_n AS phone_normalised,
       'MANUAL_STEWARD_REVIEW' AS decision,
       'Email and phone agree but critical DOB conflicts' AS reason
FROM normalised a
JOIN normalised b ON a.source_customer_id < b.source_customer_id
WHERE a.email_n = b.email_n
  AND a.phone_n = b.phone_n
  AND a.dob <> b.dob
ORDER BY record_a, record_b
""",
"failed_quality_checks.csv": """
SELECT source_system, source_customer_id, full_name, dob, email, phone,
       CASE
         WHEN dob IS NULL OR dob = '' THEN 'Missing DOB'
         WHEN email IS NULL OR email NOT LIKE '%@%.%' THEN 'Invalid email'
         ELSE 'Other'
       END AS failed_rule
FROM customer_source_records
WHERE dob IS NULL OR dob = ''
   OR email IS NULL
   OR email NOT LIKE '%@%.%'
ORDER BY source_customer_id
"""
}

for filename, sql in queries.items():
    filename = filename.strip()
    cur = conn.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with (OUT / filename).open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)

print("Validation complete. Results written to:", OUT)
