# Validation Results

The SQL logic was tested against the synthetic customer dataset using SQLite with a small compatibility function for `REGEXP_REPLACE`.

## Data-quality profile

| Metric | Result |
|---|---:|
| Total synthetic source records | 7 |
| Records with missing DOB | 1 |
| Records with invalid email structure | 1 |
| Records failing at least one mandatory/validity rule | 2 |

## Matching results

The multi-attribute matching logic identified **4 potential record pair(s)** with at least two agreeing identifiers.

## Steward exceptions

The exception logic identified **1 pair(s)** where normalised email and phone agree but Date of Birth conflicts. These are deliberately **not auto-merged** and are routed to `MANUAL_STEWARD_REVIEW`.

## Why this matters

The results demonstrate that the project does more than describe governance concepts. It applies executable rules to synthetic records and produces auditable outputs for Data Quality review, duplicate assessment and Data Steward exception handling.

Generated result files:

- `dq_summary.csv`
- `potential_matches.csv`
- `steward_exceptions.csv`
- `failed_quality_checks.csv`
