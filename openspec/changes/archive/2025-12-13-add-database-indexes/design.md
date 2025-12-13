# Design: Database Indexing Strategy

## Indexing Rules
-   **Foreign Keys**: Ensure all foreign key columns are indexed.
-   **Search Fields**: Index columns likely to be used in `WHERE`, `ORDER BY`, or `GROUP BY` clauses.
-   **Composite Indexes**: Use composite indexes for columns frequently queried together (e.g., `patient_id` + `visit_date`).
-   **Naming Convention**: `idx_<table_name>_<column_names>` or descriptive name.

## Proposed Indexes

### `patient_info`
-   `idx_patient_name`: `(name)`
-   `idx_patient_phone`: `(phone)`

### `medical_records`
-   `idx_mr_patient_date`: `(patient_id, visit_date)` - Optimize getting records for a patient ordered by date.
-   `idx_mr_doctor`: `(doctor_id)` - Find records by doctor.

### `lab_results`
-   `idx_lr_patient_date`: `(patient_id, test_date)`
-   `idx_lr_record`: `(record_id)`
-   `idx_lr_date_type`: `(test_date, test_type)` - Filtering by type over time.

### `medication_records`
-   `idx_med_patient_date`: `(patient_id, medication_date)`
-   `idx_med_record`: `(record_id)`
-   `idx_med_drug`: `(drug_name)`

### `diagnosis_records`
-   `idx_diag_patient_date`: `(patient_id, diagnosis_date)`
-   `idx_diag_record`: `(record_id)`
-   `idx_diag_name`: `(diagnosis_name)`
-   `idx_diag_code`: `(diagnosis_code)`

### `hypertension_risk_assessment`
-   `idx_hra_patient_date`: `(patient_id, assessment_date)`

### `diabetes_control_assessment`
-   `idx_dca_patient_date`: `(patient_id, assessment_date)`

### `guideline_recommendations`
-   `idx_gr_disease`: `(disease_type)`
-   `idx_gr_level`: `(recommendation_level)`

### `system_logs`
-   `idx_log_time`: `(operation_time)`
-   `idx_log_patient`: `(patient_id)`
-   `idx_log_status`: `(status)`
