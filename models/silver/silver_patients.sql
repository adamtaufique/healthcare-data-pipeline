{{ config(
    materialized='table',
    database='workspace',
    schema='silver',
    pre_hook="USE CATALOG workspace"
) }}

SELECT
    patient_id,
    mrn,
    UPPER(TRIM(first_name)) as first_name,
    UPPER(TRIM(last_name)) as last_name,
    date_of_birth,
    gender,
    zip_code,
    phone,
    email,
    
    -- Calculate age_years (not in Bronze)
    YEAR(CURRENT_DATE()) - YEAR(date_of_birth) as age_years,
    
    -- Calculate age_group (not in Bronze)
    CASE 
        WHEN YEAR(CURRENT_DATE()) - YEAR(date_of_birth) < 18 THEN 'Pediatric'
        WHEN YEAR(CURRENT_DATE()) - YEAR(date_of_birth) < 65 THEN 'Adult'
        ELSE 'Senior'
    END as age_group,
    
    -- Metadata
    _ingested_at,
    _source_file,
    CURRENT_TIMESTAMP() as _transformed_at
    
FROM workspace.bronze.patients
WHERE patient_id IS NOT NULL