# Architecture Documentation

## Medallion Architecture Implementation

### Overview
This project implements the medallion architecture pattern (Bronze → Silver → Gold) for healthcare analytics data processing.

### Layer Definitions

#### Bronze Layer (Raw/Landing)
**Purpose**: Store data exactly as received from source systems

**Characteristics**:
- No transformations applied
- Complete historical record
- Append-only pattern
- Source of truth for reprocessing

**Implementation**:
- Format: Delta Lake tables
- Schema: Source schema + metadata columns
- Location: `bronze` database in Databricks

#### Silver Layer (Cleaned/Conformed)
**Purpose**: Cleaned, validated, and enriched data ready for consumption

**Characteristics**:
- Standardized formats
- Data quality validation
- Calculated fields added
- Deduplication applied
- Still row-level detail (not aggregated)

**Transformations Applied**:
- Name standardization (UPPER, TRIM)
- Date parsing and component extraction
- Code categorization (ICD-10, CPT)
- Calculated fields (age, length of stay)
- Data quality flags

**Implementation**:
- Format: Delta Lake tables
- Schema: Enhanced with calculated columns
- Location: `silver` database in Databricks

#### Gold Layer (Aggregated/Analytics)
**Purpose**: Business-ready aggregations and metrics

**Characteristics** (Planned):
- Aggregated by business entities
- Pre-calculated KPIs
- Optimized for BI tools
- Denormalized for query performance

**Planned Gold Tables**:
- `gold.patient_encounter_summary`
- `gold.readmission_analysis`
- `gold.department_metrics`
- `gold.diagnosis_trends`

## Data Flow
```
Source (CSV) 
    ↓
Bronze (Raw)
    ↓ [Cleaning, Validation]
Silver (Conformed)
    ↓ [Aggregation, KPIs]
Gold (Analytics)
    ↓
Dashboards/Reports
```

## Technology Stack

- **Storage**: Delta Lake (ACID transactions, time travel)
- **Compute**: Databricks (Apache Spark)
- **Transformation**: SQL, PySpark (migrating to DBT)
- **Orchestration**: Manual (migrating to Airflow)
- **Version Control**: Git/GitHub

## Future Enhancements

1. **DBT Integration**: Refactor SQL transformations to DBT models
2. **Incremental Loads**: Implement merge logic for updates
3. **Data Quality Tests**: Automated testing in DBT
4. **Orchestration**: Airflow DAGs for scheduling
5. **CI/CD**: GitHub Actions for deployment
6. **Monitoring**: Data observability platform
```

**Save this** (Cmd+S).

---

## **Step 5: Update .gitignore**

Make sure your `.gitignore` includes:
```
# Virtual environment
venv/
__pycache__/
*.pyc

# Mac
.DS_Store

# IDE
.vscode/
.idea/

# Databricks
.databricks/

# Data files (optional - you may want to keep CSVs in repo)
# data/raw/*.csv

# Jupyter/Databricks checkpoints
.ipynb_checkpoints/
```

---

## **Step 6: Commit Everything to Git**

### **Using GitHub Desktop:**

1. **Open GitHub Desktop**
2. You should see all your new files in the left panel:
   - `databricks/notebooks/` (new folder with notebooks)
   - `docs/architecture.md` (new file)
   - `README.md` (modified)

3. **Review the changes** - click on files to see what changed

4. **Commit**:
   - Summary: `Add Silver layer implementation and documentation`
   - Description:
```
     - Implemented Silver layer with cleaned and enriched tables
     - Added calculated fields: age, LOS, diagnosis categories
     - Created data quality validation flags
     - Exported Databricks notebooks to repository
     - Updated README with complete project status
     - Added architecture documentation