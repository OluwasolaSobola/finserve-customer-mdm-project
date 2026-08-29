# FinServe Customer Master Data Management (MDM) Project

> **Portfolio disclaimer:** This is an independent simulated portfolio project using entirely synthetic customer data. It is not a production implementation and does not represent work commissioned by or performed for a real bank.

## Overview

This project demonstrates practical working knowledge of **Master Data Management (MDM), Data Governance, Data Quality and Data Stewardship** in a simulated financial-services environment.

Customer information is represented across three source systems — **CRM, Core Banking and Mobile Banking** — with intentional quality issues including missing values, inconsistent formatting, potential duplicates, outdated attributes and conflicting critical identifiers.

The objective is to demonstrate how governance and stewardship controls can be used to identify potential duplicate records and create a trusted **Golden Record** while avoiding unsafe automatic merges.

## Business problem

Multiple systems may hold different versions of the same customer. Without effective controls, this can create:

- duplicate customer records;
- incomplete or invalid attributes;
- inconsistent contact details;
- conflicting identity information;
- unclear source authority; and
- unreliable reporting and analytics.

## Project approach

### 1. Define the Customer Master

Customer master attributes include Customer ID, Full Name, DOB, Address, Email, Phone, Customer Status, Nationality and Account Number.

Account Balance is deliberately excluded because it is dynamic transactional/operational data rather than a stable customer master attribute.

### 2. Establish ownership and stewardship

- **Data Owner:** accountable for the Customer data domain and approval of standards.
- **Data Steward:** monitors quality, maintains definitions, investigates issues and reviews ambiguous matches.
- **IT/Data teams:** support integration, synchronisation and technical remediation.
- **Governance Council:** provides governance standards and escalation oversight.

### 3. Apply Data Quality rules

The project applies **Completeness, Validity, Consistency, Uniqueness and Timeliness** controls.

Examples in the synthetic dataset include a missing DOB, an invalid email format and inconsistent phone/email formatting.

### 4. Standardise and match records

Email and phone values are normalised before comparison. Potential duplicates are assessed using a **combination of DOB, email and phone**, rather than one matching attribute alone.

A strong potential match with a conflicting critical identifier such as DOB is routed to **manual Data Steward review** rather than automatically merged.

### 5. Apply survivorship rules

Surviving values are selected attribute-by-attribute using:

1. source authority;
2. verification status;
3. recency; and
4. data quality.

This avoids the simplistic assumption that one system should always supply every Golden Record attribute.

### 6. Create the Golden Record

The worked example consolidates three synthetic representations of the same customer into a trusted Golden Record while preserving the rationale for each surviving attribute.

## Repository structure

```text
finserve-customer-mdm-project/
├── README.md
├── data/
│   ├── raw/customer_source_records.csv
│   └── processed/golden_record_example.csv
├── sql/
│   └── mdm_data_quality_and_matching.sql
├── documentation/
│   ├── mdm_rules.md
│   ├── survivorship.md
│   ├── sql_walkthrough.md
│   └── validation_results.md
├── validation/
│   └── run_mdm_validation.py
└── results/
    ├── dq_summary.csv
    ├── potential_matches.csv
    ├── steward_exceptions.csv
    └── failed_quality_checks.csv
```

## SQL evidence

The SQL demonstrates:

- basic Data Quality profiling;
- email and phone standardisation;
- multi-attribute potential-duplicate detection;
- identification of ambiguous matches for Data Steward review; and
- retrieval of records failing mandatory/validity rules.

### SQL walkthrough

➡️ **[View the full step-by-step SQL walkthrough](documentation/sql_walkthrough.md)**

The walkthrough demonstrates how SQL was applied to:

- profile Data Quality issues;
- standardise customer attributes across source systems;
- identify potential duplicate records using multi-attribute matching;
- detect conflicting critical identifiers;
- route ambiguous matches to Data Steward review; and
- support survivorship and Golden Record decisions.

Tested results include **7 source records profiled, 4 potential matching record pairs, 2 records failing Data Quality checks and 1 ambiguous match requiring manual Data Steward review**.

## Tested results

The matching and Data Quality logic has been executed against the synthetic source dataset.

- **7** source records were profiled.
- **1** record has a missing DOB.
- **1** record has an invalid email structure.
- **4** potential record pair(s) meet the multi-attribute matching threshold.
- **1** ambiguous pair(s) are routed to manual Data Steward review because email and phone agree while DOB conflicts.

The generated outputs are stored in `/results`, and the validation can be reproduced with:

```bash
python validation/run_mdm_validation.py
```

See [`documentation/validation_results.md`](documentation/validation_results.md) for the measured results and interpretation.

## Skills demonstrated

**Master Data Management (MDM) • Data Governance • Data Quality • Data Stewardship • Data Ownership • Record Matching • Duplicate Management • Survivorship • Golden Records • Data Validation • Exception Management • SQL**

## Limitations

This is a learning and portfolio case study. It demonstrates practical MDM reasoning and SQL-based controls using synthetic data, but does **not** claim production enterprise MDM implementation or experience with an enterprise MDM platform.

## Possible future enhancements

- introduce configurable match scores and thresholds;
- add a larger synthetic dataset;
- implement automated DQ metrics and scorecards;
- add an exception-management workflow;
- model additional master-data domains;
- connect the case study to a data catalogue/governance platform.
