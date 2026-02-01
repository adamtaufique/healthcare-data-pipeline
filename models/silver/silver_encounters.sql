{{ config(
    materialized='table',
    database='workspace',
    schema='silver',
    pre_hook="USE CATALOG workspace"
) }}

SELECT
    encounter_id,
    patient_id,
    encounter_type,
    admit_datetime,
    discharge_datetime,
    department,
    primary_dx_code,
    discharge_disposition,
    
    -- Calculated fields
    ROUND(DATEDIFF(HOUR, admit_datetime, discharge_datetime) / 24.0, 2) as length_of_stay_days,
    DATE(admit_datetime) as admit_date,
    YEAR(admit_datetime) as admit_year,
    MONTH(admit_datetime) as admit_month,
    
    CASE WHEN encounter_type = 'Inpatient' THEN 1 ELSE 0 END as is_inpatient,
    CASE WHEN encounter_type = 'Emergency' THEN 1 ELSE 0 END as is_emergency,
    CASE WHEN encounter_type = 'Outpatient' THEN 1 ELSE 0 END as is_outpatient,
    
    _ingested_at,
    _source_file,
    CURRENT_TIMESTAMP() as _transformed_at
    
FROM workspace.bronze.encounters
WHERE encounter_id IS NOT NULL
    AND patient_id IS NOT NULL