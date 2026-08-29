# SQL Walkthrough — Customer MDM Data Quality & Matching

This walkthrough connects the SQL in the FinServe Customer MDM Portfolio Project to Data Quality, MDM and Data Stewardship decisions.

> **Portfolio note:** All records are synthetic. The SQL is PostgreSQL-style. Validation results were reproduced against the synthetic dataset.

## 1. Profile the source data

```sql
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN dob IS NULL OR dob = '' THEN 1 ELSE 0 END) AS missing_dob,
    SUM(CASE WHEN email IS NULL OR email NOT LIKE '%@%.%' THEN 1 ELSE 0 END) AS invalid_email
FROM customer_source_records;
```

**Purpose:** test Completeness (DOB) and Validity (email).

| total_records | missing_dob | invalid_email |
|---:|---:|---:|
| 7 | 1 | 1 |

## 2. Standardise fields before matching

```sql
SELECT
    source_system,
    source_customer_id,
    LOWER(TRIM(email)) AS email_normalised,
    REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_normalised,
    dob
FROM customer_source_records;
```

**Purpose:** make equivalent values comparable across systems. For example, `JOHN@EMAIL.COM` and `john@email.com` become comparable, while `07123-456789` and `07123456789` resolve to the same normalised phone value.

This supports the **Consistency** dimension of Data Quality.

## 3. Identify potential duplicate records

```sql
WITH normalised AS (
    SELECT *,
           LOWER(TRIM(email)) AS email_n,
           REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_n
    FROM customer_source_records
)
SELECT
    a.source_customer_id AS record_a,
    b.source_customer_id AS record_b,
    a.dob = b.dob AS dob_match,
    a.email_n = b.email_n AS email_match,
    a.phone_n = b.phone_n AS phone_match
FROM normalised a
JOIN normalised b
  ON a.source_customer_id < b.source_customer_id
WHERE
    (CASE WHEN a.dob = b.dob THEN 1 ELSE 0 END +
     CASE WHEN a.email_n = b.email_n THEN 1 ELSE 0 END +
     CASE WHEN a.phone_n = b.phone_n THEN 1 ELSE 0 END) >= 2;
```

**Matching rule:** at least two of DOB, normalised email and normalised phone must agree for a pair to become a potential match.

**Tested result:** **4 potential record pairs**.

This is candidate-generation logic for this portfolio exercise, not a claim that two matching attributes should always cause an automatic production merge.

## 4. Route critical conflicts to a Data Steward

```sql
WITH normalised AS (
    SELECT *,
           LOWER(TRIM(email)) AS email_n,
           REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_n
    FROM customer_source_records
)
SELECT
    a.source_customer_id AS record_a,
    b.source_customer_id AS record_b,
    'MANUAL_STEWARD_REVIEW' AS decision
FROM normalised a
JOIN normalised b
  ON a.source_customer_id < b.source_customer_id
WHERE a.email_n = b.email_n
  AND a.phone_n = b.phone_n
  AND a.dob <> b.dob;
```

**Tested result:** **1 ambiguous pair** where email and phone agree but DOB conflicts.

The records are deliberately **not auto-merged**. The result is `MANUAL_STEWARD_REVIEW`, connecting technical matching logic to Data Stewardship and governance decision rights.

## 5. Retrieve failed Data Quality records

```sql
SELECT *
FROM customer_source_records
WHERE dob IS NULL OR dob = ''
   OR email IS NULL
   OR email NOT LIKE '%@%.%';
```

**Tested result:** **2 records** fail at least one mandatory/validity check: one missing DOB and one invalid email.

## 6. Apply survivorship and create the Golden Record

Matching identifies candidate relationships. The trusted Golden Record additionally requires attribute-level survivorship using:

1. source authority;
2. verification status;
3. recency; and
4. data quality.

For the worked example, Core Banking supplies the more complete verified customer name while CRM supplies the most recent verified address.

## End-to-end control flow

```text
Synthetic source records
        ↓
Data Quality profiling
        ↓
Standardisation
        ↓
Multi-attribute matching
        ↓
Potential duplicate candidates
        ↓
Critical-attribute conflict?
     ↙                 ↘
   Yes                  No
    ↓                     ↓
Data Steward review   Survivorship assessment
     ↘                 ↙
       Trusted decision
              ↓
         Golden Record
              ↓
   Synchronisation / reconciliation
```

## Measured results

| Control / output | Result |
|---|---:|
| Synthetic source records profiled | 7 |
| Missing DOB issues | 1 |
| Invalid email issues | 1 |
| Records failing mandatory/validity checks | 2 |
| Potential matching record pairs | 4 |
| Manual Data Steward exceptions | 1 |

The repository's raw SQL remains in `sql/mdm_data_quality_and_matching.sql`, with generated outputs in `results/`.
