{{ config(
    materialized='table',
    database='workspace',
    schema='silver',
    pre_hook="USE CATALOG workspace"
) }}

SELECT
    procedure_id,
    encounter_id,
    procedure_code,
    UPPER(TRIM(procedure_description)) as procedure_description,
    procedure_datetime,
    performing_provider,
    
    DATE(procedure_datetime) as procedure_date,
    
    CASE
        WHEN procedure_code BETWEEN '70000' AND '79999' THEN 'Radiology'
        WHEN procedure_code BETWEEN '80000' AND '89999' THEN 'Laboratory'
        WHEN procedure_code BETWEEN '90000' AND '99999' THEN 'Medicine'
        ELSE 'Other'
    END as procedure_category,
    
    _ingested_at,
    _source_file,
    CURRENT_TIMESTAMP() as _transformed_at
    
FROM workspace.bronze.procedures
WHERE procedure_id IS NOT NULL