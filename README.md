# Healthcare Analytics Pipeline

## Overview
End-to-end healthcare data pipeline demonstrating modern ELT (Extract, Load, Transform) patterns using Databricks, DBT, and medallion architecture.

## Project Status

### ✅ Completed
- [x] Sample data generation (1,000 patients, ~12,000 total records)
- [x] Git repository setup with documentation
- [x] Databricks workspace configuration
- [x] Bronze layer implementation (raw data ingestion)
- [x] Silver layer implementation (data cleaning and enrichment)

### 🚧 In Progress
- [ ] Gold layer (analytics-ready aggregations)
- [ ] DBT transformation pipeline
- [ ] Airflow orchestration
- [ ] Data quality testing framework
- [ ] Dashboard/visualization

## Architecture

### Medallion Architecture Implementation
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────┐
│   CSV Files │──────▶│    Bronze    │──────▶│   Silver    │──────▶│   Gold   │
│  (Raw Data) │      │  (Raw Tables)│      │  (Cleaned)  │      │(Analytics)│
└─────────────┘      └──────────────┘      └─────────────┘      └──────────┘
                           4 tables           4 tables           TBD
                          ~12K rows          ~12K rows
```

## Technologies
- **Data Generation**: Python (pandas, numpy)
- **Cloud Platform**: Databricks Community Edition
- **Storage**: Delta Lake format
- **Transformation**: SQL, PySpark
- **Version Control**: Git/GitHub
- **Planned**: DBT, Apache Airflow

## Data Model

### Bronze Layer (Raw Data)
All data loaded as-is from CSV files with added metadata columns.

| Table | Records | Description |
|-------|---------|-------------|
| `bronze.patients` | 1,000 | Patient demographics |
| `bronze.encounters` | ~3,200 | Inpatient, ED, Outpatient, Observation encounters |
| `bronze.diagnoses` | ~9,700 | ICD-10 diagnosis codes |
| `bronze.procedures` | ~8,200 | CPT procedure codes |

**Metadata columns**: `_ingested_at`, `_source_file`

### Silver Layer (Cleaned & Enriched)

#### `silver.patients`
**Enhancements**:
- Standardized name formatting (uppercase, trimmed)
- Calculated `age_years` and `age_group` (Pediatric/Adult/Senior)
- Gender standardization (Male/Female/Unknown)
- Data quality flags for validation

#### `silver.encounters`
**Enhancements**:
- Calculated `length_of_stay_days` and `length_of_stay_hours`
- Date components (year, month, day of week)
- Binary flags: `is_inpatient`, `is_emergency`, `is_outpatient`, `is_observation`
- Weekend admission indicator
- LOS categories (Same Day, 1-3 Days, 4-7 Days, >7 Days)
- Data quality validation

#### `silver.diagnoses`
**Enhancements**:
- ICD-10 category extraction (first 3 characters)
- Diagnosis category mapping (Circulatory, Respiratory, etc.)
- Primary diagnosis flag
- Standardized descriptions

#### `silver.procedures`
**Enhancements**:
- Procedure category classification (Radiology, Laboratory, Medicine, etc.)
- Date components for temporal analysis
- Provider name standardization

### Gold Layer (Analytics - Planned)
- Patient encounter summaries
- 30-day readmission analysis
- Department performance metrics
- Length of stay analytics by service line
- Diagnosis trend analysis

## Key Features
- ✅ **Realistic Healthcare Data**: Actual ICD-10 and CPT codes
- ✅ **30-Day Readmissions**: Built-in 15% readmission rate
- ✅ **Northern Virginia Focus**: ZIP codes relevant to Inova Health System
- ✅ **Data Quality**: Validation flags and referential integrity
- ✅ **Medallion Architecture**: Bronze → Silver → Gold pattern
- ✅ **Delta Lake**: ACID transactions, time travel, schema evolution

## Project Structure
```
healthcare-data-pipeline/
├── data/
│   └── raw/                      # Source CSV files
├── databricks/
│   └── notebooks/                # Databricks SQL/Python notebooks
├── docs/                         # Documentation
├── generate_sample_data.py       # Data generation script
├── README.md                     # This file
└── .gitignore
```

## Sample Data Statistics
- **Total Patients**: 1,000
- **Total Encounters**: ~3,200
- **Average Encounters per Patient**: 3.2
- **30-Day Readmission Rate**: 15%
- **Encounter Types**: 35% Outpatient, 30% Inpatient, 25% ED, 10% Observation
- **Average Length of Stay** (Inpatient): 4.5 days
- **Date Range**: 2 years of historical data

## Getting Started

### Prerequisites
- Python 3.8+
- pandas, numpy
- Databricks account (Community Edition or trial)

### Generate Sample Data
```bash
python3 generate_sample_data.py
```

Output files created in `data/raw/`:
- `patients.csv`
- `encounters.csv`
- `diagnoses.csv`
- `procedures.csv`

### Load to Databricks
1. Import notebooks from `databricks/notebooks/`
2. Upload CSV files via Databricks Data UI
3. Run Bronze layer notebook to create raw tables
4. Run Silver layer notebook for cleaned tables

## Data Quality Checks

### Implemented Validations
- ✅ No null primary keys
- ✅ Referential integrity maintained (no orphaned records)
- ✅ Date logic validation (discharge > admit)
- ✅ Age range validation (0-120 years)
- ✅ Length of stay reasonableness checks

### Quality Metrics
- **Bronze → Silver Row Loss**: 0 records
- **Data Quality Issues**: 0 flagged records
- **Orphaned Records**: 0 across all tables

## Sample Queries

### Find Patients with Multiple Encounters
```sql
SELECT 
    patient_id,
    COUNT(*) as encounter_count
FROM silver.encounters
GROUP BY patient_id
HAVING COUNT(*) > 3
ORDER BY encounter_count DESC;
```

### 30-Day Readmission Rate
```sql
WITH readmissions AS (
    SELECT 
        patient_id,
        LEAD(admit_datetime) OVER (
            PARTITION BY patient_id 
            ORDER BY admit_datetime
        ) as next_admit,
        discharge_datetime
    FROM silver.encounters
    WHERE is_inpatient = 1
)
SELECT 
    COUNT(*) as total_discharges,
    SUM(CASE 
        WHEN DATEDIFF(day, discharge_datetime, next_admit) <= 30 
        THEN 1 ELSE 0 
    END) as readmissions_30day,
    ROUND(
        SUM(CASE 
            WHEN DATEDIFF(day, discharge_datetime, next_admit) <= 30 
            THEN 1 ELSE 0 
        END) * 100.0 / COUNT(*), 
        1
    ) as readmission_rate
FROM readmissions
WHERE next_admit IS NOT NULL;
```

## Next Steps
1. ✅ Build Gold layer aggregations
2. ✅ Connect DBT Cloud to Databricks
3. ✅ Refactor Silver/Gold layers as DBT models
4. ✅ Implement automated testing in DBT
5. ✅ Set up Airflow for orchestration
6. ✅ Create visualization dashboard

## Target Use Case
This project demonstrates modern data engineering skills for healthcare analytics roles, specifically targeting:
- **Inova Health System** - Senior Data Engineer position
- Healthcare organizations implementing cloud data platforms
- Roles requiring Epic/Clarity data pipeline experience

## Learning Objectives
- ✅ Modern ELT patterns (vs traditional ETL)
- ✅ Medallion architecture implementation
- ✅ Cloud data warehouse concepts (Databricks)
- ✅ Delta Lake features (ACID, time travel)
- 🚧 DBT for transformation layer
- 🚧 Airflow for orchestration
- 🚧 Data quality testing frameworks

## Author
**Adam Taufique**  
Healthcare IT Professional | 7 Years Management Experience  
Transitioning to Modern Data Engineering

[GitHub](https://github.com/YOUR_USERNAME/healthcare-data-pipeline) | [LinkedIn](#)

## License
MIT License - Free to use for learning and portfolio purposes

---

**Last Updated**: [2026-01-30]

## Overview
End-to-end healthcare data pipeline demonstrating modern ELT (Extract, Load, Transform) patterns using Databricks, DBT, and medallion architecture.

## Project Goals
- Build a production-like healthcare analytics platform
- Demonstrate proficiency with modern data engineering tools
- Create portfolio project for data engineering roles

## Architecture
```
CSV Files → Databricks (Bronze) → DBT (Silver/Gold) → Analytics
```

## Technologies
- **Data Generation**: Python (pandas, numpy)
- **Storage**: Databricks Delta Lake
- **Transformation**: DBT (Data Build Tool)
- **Orchestration**: Apache Airflow (planned)
- **Version Control**: Git/GitHub

## Data Model

### Bronze Layer (Raw Data)
- **patients**: 1,000 synthetic patients with demographics
- **encounters**: ~3,200 encounters (Inpatient, ED, Outpatient, Observation)
- **diagnoses**: ~9,700 diagnosis records (ICD-10 codes)
- **procedures**: ~8,200 procedure records (CPT codes)

### Silver Layer (Cleaned)
- Standardized patient demographics
- Cleaned encounter data with calculated fields
- Quality-checked diagnoses and procedures

### Gold Layer (Analytics)
- Patient encounter summaries
- 30-day readmission analysis
- Department-level metrics
- Length of stay analytics

## Key Features
- **Realistic Healthcare Data**: Uses actual ICD-10 and CPT codes
- **30-Day Readmissions**: Built-in 15% readmission rate for analytics
- **Northern Virginia Focus**: ZIP codes relevant to Inova Health System
- **Proper Relationships**: Foreign keys maintain data integrity

## Sample Data Statistics
- Total Patients: 1,000
- Total Encounters: ~3,200
- Average Encounters per Patient: 3.2
- 30-Day Readmission Rate: 15%

## Getting Started

### Prerequisites
- Python 3.8+
- pandas, numpy

### Generate Sample Data
```bash
python3 generate_sample_data.py
```

Output files will be created in `data/raw/`

## Project Status
- [x] Sample data generation
- [x] Git repository setup
- [ ] Databricks Bronze layer
- [ ] DBT Silver transformations
- [ ] DBT Gold analytics models
- [ ] Airflow orchestration
- [ ] Dashboard/visualization

## Next Steps
1. Upload data to Databricks
2. Create Bronze layer tables
3. Build DBT transformation pipeline
4. Implement data quality tests
5. Create analytics dashboard

## Author
Adam - Healthcare IT Professional transitioning to modern data engineering

## License
MIT License - Feel free to use this for learning purposes