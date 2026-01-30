# Healthcare Analytics Pipeline

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