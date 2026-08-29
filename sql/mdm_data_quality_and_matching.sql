-- FinServe Customer MDM Portfolio Project
-- SQL is written in PostgreSQL-style syntax and is intended for the synthetic dataset.

-- 1. Basic data-quality profiling
SELECT
    COUNT(*) AS total_records,
    SUM(CASE WHEN dob IS NULL OR dob = '' THEN 1 ELSE 0 END) AS missing_dob,
    SUM(CASE WHEN email IS NULL OR email NOT LIKE '%@%.%' THEN 1 ELSE 0 END) AS invalid_email
FROM customer_source_records;

-- 2. Standardise fields before matching
SELECT
    source_system,
    source_customer_id,
    LOWER(TRIM(email)) AS email_normalised,
    REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS phone_normalised,
    dob
FROM customer_source_records;

-- 3. Identify potential duplicate groups using multiple identifiers.
-- A single matching attribute should not automatically trigger a merge.
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

-- 4. Steward exception: strong potential match but conflicting critical DOB.
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

-- 5. Example quality rule: records failing mandatory/validity checks
SELECT *
FROM customer_source_records
WHERE dob IS NULL OR dob = ''
   OR email IS NULL
   OR email NOT LIKE '%@%.%';
