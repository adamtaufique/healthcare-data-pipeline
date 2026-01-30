# Databricks notebook source
# MAGIC %sql
# MAGIC -- Create cleaned and standardized patient table
# MAGIC CREATE OR REPLACE TABLE silver.patients AS
# MAGIC SELECT
# MAGIC     -- Original fields, cleaned
# MAGIC     patient_id,
# MAGIC     mrn,
# MAGIC     UPPER(TRIM(first_name)) as first_name,
# MAGIC     UPPER(TRIM(last_name)) as last_name,
# MAGIC     date_of_birth,
# MAGIC     CASE 
# MAGIC         WHEN UPPER(gender) IN ('M', 'MALE') THEN 'Male'
# MAGIC         WHEN UPPER(gender) IN ('F', 'FEMALE') THEN 'Female'
# MAGIC         ELSE 'Unknown'
# MAGIC     END as gender,
# MAGIC     zip_code,
# MAGIC     phone,
# MAGIC     
# MAGIC     -- Calculated fields
# MAGIC     YEAR(CURRENT_DATE()) - YEAR(date_of_birth) as age_years,
# MAGIC     CASE 
# MAGIC         WHEN YEAR(CURRENT_DATE()) - YEAR(date_of_birth) < 18 THEN 'Pediatric'
# MAGIC         WHEN YEAR(CURRENT_DATE()) - YEAR(date_of_birth) < 65 THEN 'Adult'
# MAGIC         ELSE 'Senior'
# MAGIC     END as age_group,
# MAGIC     
# MAGIC     -- Data quality flags
# MAGIC     CASE 
# MAGIC         WHEN date_of_birth IS NULL THEN 'Missing DOB'
# MAGIC         WHEN date_of_birth > CURRENT_DATE() THEN 'Future DOB'
# MAGIC         WHEN YEAR(CURRENT_DATE()) - YEAR(date_of_birth) > 120 THEN 'Unlikely Age'
# MAGIC         ELSE 'Valid'
# MAGIC     END as data_quality_flag,
# MAGIC     
# MAGIC     -- Metadata
# MAGIC     _ingested_at,
# MAGIC     _source_file,
# MAGIC     CURRENT_TIMESTAMP() as _transformed_at
# MAGIC     
# MAGIC FROM bronze.patients
# MAGIC WHERE patient_id IS NOT NULL;  -- Exclude any records without IDs
# MAGIC
# MAGIC -- Show results
# MAGIC SELECT 
# MAGIC     'Total Patients' as metric,
# MAGIC     COUNT(*) as value
# MAGIC FROM silver.patients
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC     'Age Groups',
# MAGIC     NULL
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC     CONCAT('  ', age_group),
# MAGIC     COUNT(*)
# MAGIC FROM silver.patients
# MAGIC GROUP BY age_group
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Data Quality Issues',
# MAGIC     COUNT(*)
# MAGIC FROM silver.patients
# MAGIC WHERE data_quality_flag != 'Valid';

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create cleaned encounters table with calculated fields
# MAGIC CREATE OR REPLACE TABLE silver.encounters AS
# MAGIC SELECT
# MAGIC     -- Original fields
# MAGIC     encounter_id,
# MAGIC     patient_id,
# MAGIC     encounter_type,
# MAGIC     admit_datetime,
# MAGIC     discharge_datetime,
# MAGIC     department,
# MAGIC     primary_dx_code,
# MAGIC     discharge_disposition,
# MAGIC     
# MAGIC     -- Calculated fields
# MAGIC     ROUND(
# MAGIC         DATEDIFF(HOUR, admit_datetime, discharge_datetime) / 24.0,
# MAGIC         2
# MAGIC     ) as length_of_stay_days,
# MAGIC     
# MAGIC     DATEDIFF(HOUR, admit_datetime, discharge_datetime) as length_of_stay_hours,
# MAGIC     
# MAGIC     -- Date components for analytics
# MAGIC     DATE(admit_datetime) as admit_date,
# MAGIC     YEAR(admit_datetime) as admit_year,
# MAGIC     MONTH(admit_datetime) as admit_month,
# MAGIC     DAYOFWEEK(admit_datetime) as admit_day_of_week,
# MAGIC     
# MAGIC     -- Flags for common analyses
# MAGIC     CASE WHEN encounter_type = 'Inpatient' THEN 1 ELSE 0 END as is_inpatient,
# MAGIC     CASE WHEN encounter_type = 'Emergency' THEN 1 ELSE 0 END as is_emergency,
# MAGIC     CASE WHEN encounter_type = 'Outpatient' THEN 1 ELSE 0 END as is_outpatient,
# MAGIC     CASE WHEN encounter_type = 'Observation' THEN 1 ELSE 0 END as is_observation,
# MAGIC     
# MAGIC     -- Weekend admission flag
# MAGIC     CASE 
# MAGIC         WHEN DAYOFWEEK(admit_datetime) IN (1, 7) THEN 1  -- Sunday=1, Saturday=7
# MAGIC         ELSE 0 
# MAGIC     END as is_weekend_admission,
# MAGIC     
# MAGIC     -- Length of stay category
# MAGIC     CASE
# MAGIC         WHEN DATEDIFF(HOUR, admit_datetime, discharge_datetime) < 24 THEN 'Same Day'
# MAGIC         WHEN DATEDIFF(HOUR, admit_datetime, discharge_datetime) < 72 THEN '1-3 Days'
# MAGIC         WHEN DATEDIFF(HOUR, admit_datetime, discharge_datetime) < 168 THEN '4-7 Days'
# MAGIC         ELSE '> 7 Days'
# MAGIC     END as los_category,
# MAGIC     
# MAGIC     -- Data quality flags
# MAGIC     CASE
# MAGIC         WHEN admit_datetime IS NULL THEN 'Missing Admit Date'
# MAGIC         WHEN discharge_datetime IS NULL THEN 'Missing Discharge Date'
# MAGIC         WHEN discharge_datetime < admit_datetime THEN 'Discharge Before Admit'
# MAGIC         WHEN DATEDIFF(DAY, admit_datetime, discharge_datetime) > 365 THEN 'Unusually Long Stay'
# MAGIC         ELSE 'Valid'
# MAGIC     END as data_quality_flag,
# MAGIC     
# MAGIC     -- Metadata
# MAGIC     _ingested_at,
# MAGIC     _source_file,
# MAGIC     CURRENT_TIMESTAMP() as _transformed_at
# MAGIC     
# MAGIC FROM bronze.encounters
# MAGIC WHERE encounter_id IS NOT NULL
# MAGIC     AND patient_id IS NOT NULL
# MAGIC     AND discharge_datetime >= admit_datetime;  -- Basic data quality filter
# MAGIC
# MAGIC -- Summary statistics
# MAGIC SELECT 
# MAGIC     'Total Encounters' as metric,
# MAGIC     CAST(COUNT(*) AS STRING) as value
# MAGIC FROM silver.encounters
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC     'Encounter Types',
# MAGIC     NULL
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC     CONCAT('  ', encounter_type),
# MAGIC     CAST(COUNT(*) AS STRING)
# MAGIC FROM silver.encounters
# MAGIC GROUP BY encounter_type
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Average LOS (days)',
# MAGIC     CAST(ROUND(AVG(length_of_stay_days), 1) AS STRING)
# MAGIC FROM silver.encounters
# MAGIC WHERE is_inpatient = 1
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Weekend Admissions',
# MAGIC     CONCAT(CAST(SUM(is_weekend_admission) AS STRING), ' (', 
# MAGIC            CAST(ROUND(SUM(is_weekend_admission) * 100.0 / COUNT(*), 1) AS STRING), '%)')
# MAGIC FROM silver.encounters;

# COMMAND ----------

# DBTITLE 1,Cell 3
# MAGIC %sql
# MAGIC     -- Create cleaned diagnoses table
# MAGIC CREATE OR REPLACE TABLE silver.diagnoses AS
# MAGIC SELECT
# MAGIC     -- Original fields
# MAGIC     diagnosis_id,
# MAGIC     encounter_id,
# MAGIC     icd10_code,
# MAGIC     UPPER(TRIM(diagnosis_description)) as diagnosis_description,
# MAGIC     diagnosis_type,
# MAGIC     diagnosis_sequence,
# MAGIC     
# MAGIC     -- ICD-10 code breakdown (first 3 chars = category)
# MAGIC     SUBSTRING(icd10_code, 1, 3) as icd10_category,
# MAGIC     
# MAGIC     -- Flag primary vs secondary
# MAGIC     CASE WHEN diagnosis_type = 'Primary' THEN 1 ELSE 0 END as is_primary_diagnosis,
# MAGIC     
# MAGIC     -- Common diagnosis categories (for analytics)
# MAGIC     CASE
# MAGIC         WHEN icd10_code LIKE 'I%' THEN 'Circulatory'
# MAGIC         WHEN icd10_code LIKE 'J%' THEN 'Respiratory'
# MAGIC         WHEN icd10_code LIKE 'E%' THEN 'Endocrine/Metabolic'
# MAGIC         WHEN icd10_code LIKE 'N%' THEN 'Genitourinary'
# MAGIC         WHEN icd10_code LIKE 'M%' THEN 'Musculoskeletal'
# MAGIC         WHEN icd10_code LIKE 'R%' THEN 'Symptoms/Signs'
# MAGIC         WHEN icd10_code LIKE 'K%' THEN 'Digestive'
# MAGIC         WHEN icd10_code LIKE 'F%' THEN 'Mental/Behavioral'
# MAGIC         ELSE 'Other'
# MAGIC     END as diagnosis_category,
# MAGIC     
# MAGIC     -- Data quality
# MAGIC     CASE
# MAGIC         WHEN icd10_code IS NULL THEN 'Missing Code'
# MAGIC         WHEN diagnosis_description IS NULL THEN 'Missing Description'
# MAGIC         ELSE 'Valid'
# MAGIC     END as data_quality_flag,
# MAGIC     
# MAGIC     -- Metadata
# MAGIC     _ingested_at,
# MAGIC     _source_file,
# MAGIC     CURRENT_TIMESTAMP() as _transformed_at
# MAGIC     
# MAGIC FROM bronze.diagnoses
# MAGIC WHERE diagnosis_id IS NOT NULL
# MAGIC     AND encounter_id IS NOT NULL;
# MAGIC
# MAGIC -- Summary
# MAGIC SELECT 
# MAGIC     'Total Diagnoses' as metric,
# MAGIC     CAST(COUNT(*) AS STRING) as value
# MAGIC FROM silver.diagnoses
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Primary Diagnoses',
# MAGIC     CAST(SUM(is_primary_diagnosis) AS STRING)
# MAGIC FROM silver.diagnoses
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Diagnosis Categories',
# MAGIC     NULL
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     CONCAT('  ', diagnosis_category),
# MAGIC     CAST(COUNT(*) AS STRING)
# MAGIC FROM silver.diagnoses
# MAGIC GROUP BY diagnosis_category;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Create cleaned procedures table
# MAGIC CREATE OR REPLACE TABLE silver.procedures AS
# MAGIC SELECT
# MAGIC     -- Original fields
# MAGIC     procedure_id,
# MAGIC     encounter_id,
# MAGIC     procedure_code,
# MAGIC     UPPER(TRIM(procedure_description)) as procedure_description,
# MAGIC     procedure_datetime,
# MAGIC     UPPER(TRIM(performing_provider)) as performing_provider,
# MAGIC     
# MAGIC     -- Calculated fields
# MAGIC     DATE(procedure_datetime) as procedure_date,
# MAGIC     YEAR(procedure_datetime) as procedure_year,
# MAGIC     MONTH(procedure_datetime) as procedure_month,
# MAGIC     
# MAGIC     -- Procedure type classification (based on CPT code ranges)
# MAGIC     CASE
# MAGIC         WHEN procedure_code BETWEEN '70000' AND '79999' THEN 'Radiology'
# MAGIC         WHEN procedure_code BETWEEN '80000' AND '89999' THEN 'Laboratory'
# MAGIC         WHEN procedure_code BETWEEN '90000' AND '99999' THEN 'Medicine/E&M'
# MAGIC         WHEN procedure_code BETWEEN '00100' AND '01999' THEN 'Anesthesia'
# MAGIC         WHEN procedure_code BETWEEN '10000' AND '69990' THEN 'Surgery'
# MAGIC         ELSE 'Other'
# MAGIC     END as procedure_category,
# MAGIC     
# MAGIC     -- Data quality
# MAGIC     CASE
# MAGIC         WHEN procedure_code IS NULL THEN 'Missing Code'
# MAGIC         WHEN procedure_datetime IS NULL THEN 'Missing DateTime'
# MAGIC         WHEN performing_provider IS NULL THEN 'Missing Provider'
# MAGIC         ELSE 'Valid'
# MAGIC     END as data_quality_flag,
# MAGIC     
# MAGIC     -- Metadata
# MAGIC     _ingested_at,
# MAGIC     _source_file,
# MAGIC     CURRENT_TIMESTAMP() as _transformed_at
# MAGIC     
# MAGIC FROM bronze.procedures
# MAGIC WHERE procedure_id IS NOT NULL
# MAGIC     AND encounter_id IS NOT NULL;
# MAGIC
# MAGIC -- Summary
# MAGIC SELECT 
# MAGIC     'Total Procedures' as metric,
# MAGIC     CAST(COUNT(*) AS STRING) as value
# MAGIC FROM silver.procedures
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Procedure Categories',
# MAGIC     NULL
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     CONCAT('  ', procedure_category),
# MAGIC     CAST(COUNT(*) AS STRING)
# MAGIC FROM silver.procedures
# MAGIC GROUP BY procedure_category;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Comprehensive data quality check across Silver layer
# MAGIC
# MAGIC -- 1. Check for orphaned encounters (encounters without patients)
# MAGIC SELECT 
# MAGIC     'Orphaned Encounters' as check_name,
# MAGIC     CAST(COUNT(*) AS STRING) as result,
# MAGIC     CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '✗ FAIL' END as status
# MAGIC FROM silver.encounters e
# MAGIC LEFT JOIN silver.patients p ON e.patient_id = p.patient_id
# MAGIC WHERE p.patient_id IS NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC -- 2. Check for orphaned diagnoses (diagnoses without encounters)
# MAGIC SELECT 
# MAGIC     'Orphaned Diagnoses',
# MAGIC     CAST(COUNT(*) AS STRING),
# MAGIC     CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '✗ FAIL' END
# MAGIC FROM silver.diagnoses d
# MAGIC LEFT JOIN silver.encounters e ON d.encounter_id = e.encounter_id
# MAGIC WHERE e.encounter_id IS NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC -- 3. Check for orphaned procedures
# MAGIC SELECT 
# MAGIC     'Orphaned Procedures',
# MAGIC     CAST(COUNT(*) AS STRING),
# MAGIC     CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '✗ FAIL' END
# MAGIC FROM silver.procedures p
# MAGIC LEFT JOIN silver.encounters e ON p.encounter_id = e.encounter_id
# MAGIC WHERE e.encounter_id IS NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC -- 4. Check for encounters with no diagnoses
# MAGIC SELECT 
# MAGIC     'Encounters Without Diagnoses',
# MAGIC     CAST(COUNT(DISTINCT e.encounter_id) AS STRING),
# MAGIC     CASE 
# MAGIC         WHEN COUNT(DISTINCT e.encounter_id) = 0 THEN '✓ PASS' 
# MAGIC         WHEN COUNT(DISTINCT e.encounter_id) < 10 THEN '⚠ WARNING'
# MAGIC         ELSE '✗ FAIL' 
# MAGIC     END
# MAGIC FROM silver.encounters e
# MAGIC LEFT JOIN silver.diagnoses d ON e.encounter_id = d.encounter_id
# MAGIC WHERE d.encounter_id IS NULL
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC -- 5. Check date validity in encounters
# MAGIC SELECT 
# MAGIC     'Invalid Encounter Dates',
# MAGIC     CAST(COUNT(*) AS STRING),
# MAGIC     CASE WHEN COUNT(*) = 0 THEN '✓ PASS' ELSE '✗ FAIL' END
# MAGIC FROM silver.encounters
# MAGIC WHERE data_quality_flag != 'Valid'
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC -- 6. Row count reconciliation
# MAGIC SELECT
# MAGIC     'Bronze → Silver Row Loss',
# MAGIC     CONCAT(
# MAGIC         CAST((SELECT COUNT(*) FROM bronze.encounters) - (SELECT COUNT(*) FROM silver.encounters) AS STRING),
# MAGIC         ' rows'
# MAGIC     ),
# MAGIC     CASE 
# MAGIC         WHEN (SELECT COUNT(*) FROM bronze.encounters) = (SELECT COUNT(*) FROM silver.encounters) 
# MAGIC         THEN '✓ PASS' 
# MAGIC         ELSE '⚠ CHECK'
# MAGIC     END;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Silver Layer Summary Dashboard
# MAGIC SELECT 
# MAGIC     'SILVER LAYER SUMMARY' as section,
# MAGIC     '===================' as details
# MAGIC UNION ALL
# MAGIC SELECT 
# MAGIC     'Patients',
# MAGIC     CONCAT(CAST(COUNT(*) AS STRING), ' records')
# MAGIC FROM silver.patients
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Encounters',
# MAGIC     CONCAT(CAST(COUNT(*) AS STRING), ' records')
# MAGIC FROM silver.encounters
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Diagnoses',
# MAGIC     CONCAT(CAST(COUNT(*) AS STRING), ' records')
# MAGIC FROM silver.diagnoses
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Procedures',
# MAGIC     CONCAT(CAST(COUNT(*) AS STRING), ' records')
# MAGIC FROM silver.procedures
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     '',
# MAGIC     ''
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'DATA QUALITY',
# MAGIC     '==================='
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Avg Age',
# MAGIC     CONCAT(CAST(ROUND(AVG(age_years), 1) AS STRING), ' years')
# MAGIC FROM silver.patients
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Avg LOS (Inpatient)',
# MAGIC     CONCAT(CAST(ROUND(AVG(length_of_stay_days), 1) AS STRING), ' days')
# MAGIC FROM silver.encounters
# MAGIC WHERE is_inpatient = 1
# MAGIC UNION ALL
# MAGIC SELECT
# MAGIC     'Records with Quality Issues',
# MAGIC     CONCAT(
# MAGIC         CAST((
# MAGIC             SELECT COUNT(*) FROM silver.patients WHERE data_quality_flag != 'Valid'
# MAGIC         ) + (
# MAGIC             SELECT COUNT(*) FROM silver.encounters WHERE data_quality_flag != 'Valid'
# MAGIC         ) AS STRING),
# MAGIC         ' total'
# MAGIC     );

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Patient encounter summary with diagnoses
# MAGIC SELECT 
# MAGIC     p.patient_id,
# MAGIC     p.mrn,
# MAGIC     p.first_name,
# MAGIC     p.last_name,
# MAGIC     p.age_years,
# MAGIC     p.age_group,
# MAGIC     e.encounter_id,
# MAGIC     e.encounter_type,
# MAGIC     e.admit_date,
# MAGIC     e.length_of_stay_days,
# MAGIC     e.department,
# MAGIC     d.icd10_code,
# MAGIC     d.diagnosis_description,
# MAGIC     d.diagnosis_category
# MAGIC FROM silver.patients p
# MAGIC JOIN silver.encounters e ON p.patient_id = e.patient_id
# MAGIC JOIN silver.diagnoses d ON e.encounter_id = d.encounter_id
# MAGIC WHERE d.is_primary_diagnosis = 1  -- Only primary diagnoses
# MAGIC     AND e.is_inpatient = 1         -- Only inpatient stays
# MAGIC ORDER BY p.patient_id, e.admit_date
# MAGIC LIMIT 20;