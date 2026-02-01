{{ config(
    materialized='table',
    database='workspace',
    schema='silver',
    pre_hook="USE CATALOG workspace"
) }}

SELECT
    diagnosis_id,
    encounter_id,
    icd10_code,
    UPPER(TRIM(diagnosis_description)) as diagnosis_description,
    diagnosis_type,
    diagnosis_sequence,
    
    SUBSTRING(icd10_code, 1, 3) as icd10_category,
    CASE WHEN diagnosis_type = 'Primary' THEN 1 ELSE 0 END as is_primary_diagnosis,
    
    CASE
        WHEN icd10_code LIKE 'I%' THEN 'Circulatory'
        WHEN icd10_code LIKE 'J%' THEN 'Respiratory'
        WHEN icd10_code LIKE 'E%' THEN 'Endocrine/Metabolic'
        WHEN icd10_code LIKE 'N%' THEN 'Genitourinary'
        WHEN icd10_code LIKE 'M%' THEN 'Musculoskeletal'
        ELSE 'Other'
    END as diagnosis_category,
    
    _ingested_at,
    _source_file,
    CURRENT_TIMESTAMP() as _transformed_at
    
FROM workspace.bronze.diagnoses
WHERE diagnosis_id IS NOT NULL