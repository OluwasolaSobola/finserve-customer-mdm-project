# MDM and Data Quality Rules

| Rule | Control | Steward response |
|---|---|---|
| Completeness | DOB is mandatory for the customer master. | Investigate missing values with the authorised source. |
| Validity | Email must meet the required structural format. | Reject invalid input or coordinate correction. |
| Consistency | Email and phone values are normalised before comparison. | Standardise values before matching. |
| Uniqueness | Potential duplicates use multiple identifiers. | Review match evidence; do not rely on one attribute. |
| Exception | Conflicting critical identifiers must not auto-merge. | Route to Data Steward for manual review. |
| Survivorship | Select values using authority, verification, recency and quality. | Document the reason for each surviving value. |
| Synchronisation | Verified master changes should propagate downstream. | Monitor failed updates and reconcile exceptions. |
