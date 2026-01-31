-- models/silver/silver_patients.sql

{{ config(
    materialized='table'
) }}

SELECT
    patient_id,
    mrn,
    UPPER(TRIM(first_name)) as first_name,
    UPPER(TRIM(last_name)) as last_name,
    date_of_birth,
    age_years,
    age_group,
    gender,
    zip_code,
    _ingested_at,
    CURRENT_TIMESTAMP() as _transformed_at
FROM {{ source('bronze', 'patients') }}
WHERE patient_id IS NOT NULL