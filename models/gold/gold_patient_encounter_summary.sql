{{ config(
    materialized='table',
    database='workspace',
    schema='gold',
    pre_hook="USE CATALOG workspace"
) }}

SELECT
    p.patient_id,
    p.mrn,
    p.first_name,
    p.last_name,
    p.age_years,
    p.age_group,
    p.gender,
    
    COUNT(DISTINCT e.encounter_id) as total_encounters,
    SUM(e.is_inpatient) as inpatient_encounters,
    SUM(e.is_emergency) as emergency_encounters,
    SUM(e.is_outpatient) as outpatient_encounters,
    
    ROUND(AVG(e.length_of_stay_days), 2) as avg_length_of_stay,
    
    COUNT(DISTINCT d.icd10_code) as unique_diagnoses,
    
    MAX(e.discharge_datetime) as last_encounter_date,
    
    CASE 
        WHEN COUNT(DISTINCT e.encounter_id) >= 10 THEN 'High Utilizer'
        WHEN COUNT(DISTINCT e.encounter_id) >= 5 THEN 'Moderate Utilizer'
        ELSE 'Low Utilizer'
    END as utilization_category,
    
    CURRENT_TIMESTAMP() as _created_at

FROM workspace.silver.silver_patients p
LEFT JOIN workspace.silver.silver_encounters e ON p.patient_id = e.patient_id
LEFT JOIN workspace.silver.silver_diagnoses d ON e.encounter_id = d.encounter_id
LEFT JOIN workspace.silver.silver_procedures pr ON e.encounter_id = pr.encounter_id
GROUP BY 
    p.patient_id, p.mrn, p.first_name, p.last_name, 
    p.age_years, p.age_group, p.gender