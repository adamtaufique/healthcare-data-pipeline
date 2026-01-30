"""
Healthcare Sample Data Generator
Generates realistic sample data mimicking Epic Clarity tables
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Configuration
NUM_PATIENTS = 1000
AVG_ENCOUNTERS_PER_PATIENT = 3
READMISSION_RATE = 0.15  # 15% of patients have readmissions

# Reference data
FIRST_NAMES = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 
               'Linda', 'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan',
               'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Charles', 'Karen']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
              'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
              'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']

# Northern Virginia ZIP codes (for Inova relevance)
ZIP_CODES = ['22202', '22203', '22204', '22205', '22206', '22207', '22042', '22043',
             '22044', '22046', '22101', '22102', '22150', '22151', '22152', '20124']

DEPARTMENTS = [
    'Cardiology', 'Emergency', 'Medicine', 'Surgery', 'Orthopedics',
    'Neurology', 'Oncology', 'Pediatrics', 'Obstetrics', 'ICU'
]

ENCOUNTER_TYPES = ['Inpatient', 'Emergency', 'Outpatient', 'Observation']

# ICD-10 codes with descriptions (common conditions)
DIAGNOSES = {
    'I50.9': 'Heart failure, unspecified',
    'I10': 'Essential (primary) hypertension',
    'E11.9': 'Type 2 diabetes mellitus without complications',
    'J44.9': 'Chronic obstructive pulmonary disease, unspecified',
    'I25.10': 'Atherosclerotic heart disease',
    'N18.3': 'Chronic kidney disease, stage 3',
    'I63.9': 'Cerebral infarction, unspecified',
    'J18.9': 'Pneumonia, unspecified organism',
    'R07.9': 'Chest pain, unspecified',
    'M54.5': 'Low back pain',
    'K21.9': 'Gastro-esophageal reflux disease',
    'F41.9': 'Anxiety disorder, unspecified',
    'I48.91': 'Atrial fibrillation',
    'E78.5': 'Hyperlipidemia, unspecified',
    'N39.0': 'Urinary tract infection, site not specified'
}

# CPT codes with descriptions (common procedures)
PROCEDURES = {
    '93000': 'Electrocardiogram, routine ECG',
    '93306': 'Echocardiography, transthoracic',
    '71046': 'Chest X-ray, 2 views',
    '80053': 'Comprehensive metabolic panel',
    '85025': 'Complete blood count with differential',
    '36415': 'Collection of venous blood',
    '99285': 'Emergency department visit, high complexity',
    '99223': 'Initial hospital care, high complexity',
    '36556': 'Insertion of central venous catheter',
    '94760': 'Noninvasive pulse oximetry'
}

def generate_patients(n=NUM_PATIENTS):
    """Generate patient demographic data"""
    print(f"Generating {n} patients...")
    
    patients = []
    for i in range(1, n + 1):
        # Generate date of birth (ages 18-95)
        age = random.randint(18, 95)
        dob = datetime.now() - timedelta(days=age*365 + random.randint(0, 364))
        
        patient = {
            'patient_id': i,
            'mrn': f'MRN{str(i).zfill(6)}',
            'first_name': random.choice(FIRST_NAMES),
            'last_name': random.choice(LAST_NAMES),
            'date_of_birth': dob.strftime('%Y-%m-%d'),
            'gender': random.choice(['M', 'F']),
            'zip_code': random.choice(ZIP_CODES),
            'phone': f'703{random.randint(1000000, 9999999)}',
            'email': None  # Could generate if needed
        }
        patients.append(patient)
    
    return pd.DataFrame(patients)

def generate_encounters(patients_df):
    """Generate encounter data with realistic patterns"""
    print("Generating encounters...")
    
    encounters = []
    encounter_id = 1
    
    for _, patient in patients_df.iterrows():
        patient_id = patient['patient_id']
        
        # Determine number of encounters (Poisson distribution)
        num_encounters = np.random.poisson(AVG_ENCOUNTERS_PER_PATIENT) + 1
        num_encounters = max(1, min(num_encounters, 10))  # Cap at 10
        
        # Generate encounters over past 2 years
        start_date = datetime.now() - timedelta(days=730)
        
        for enc_num in range(num_encounters):
            # Space encounters somewhat realistically
            days_offset = random.randint(0, 730)
            admit_dt = start_date + timedelta(days=days_offset)
            
            # Encounter type probabilities
            enc_type = random.choices(
                ENCOUNTER_TYPES,
                weights=[0.3, 0.25, 0.35, 0.1],  # Inpatient, ED, Outpatient, Obs
                k=1
            )[0]
            
            # Length of stay varies by type
            if enc_type == 'Inpatient':
                los_hours = random.randint(24, 240)  # 1-10 days
            elif enc_type == 'Observation':
                los_hours = random.randint(8, 48)  # 8 hours - 2 days
            elif enc_type == 'Emergency':
                los_hours = random.randint(2, 12)  # 2-12 hours
            else:  # Outpatient
                los_hours = random.randint(1, 4)  # 1-4 hours
            
            discharge_dt = admit_dt + timedelta(hours=los_hours)
            
            # Don't create encounters in the future
            if discharge_dt > datetime.now():
                continue
            
            encounter = {
                'encounter_id': f'E{str(encounter_id).zfill(6)}',
                'patient_id': patient_id,
                'encounter_type': enc_type,
                'admit_datetime': admit_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'discharge_datetime': discharge_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'department': random.choice(DEPARTMENTS),
                'primary_dx_code': random.choice(list(DIAGNOSES.keys())),
                'discharge_disposition': random.choice([
                    'Home', 'Home with Home Health', 'SNF', 'Rehab', 
                    'Expired', 'Left AMA', 'Transfer'
                ])
            }
            encounters.append(encounter)
            encounter_id += 1
    
    encounters_df = pd.DataFrame(encounters)
    
    # Add some readmissions for realism
    encounters_df = add_readmissions(encounters_df, patients_df)
    
    return encounters_df.sort_values(['patient_id', 'admit_datetime']).reset_index(drop=True)

def add_readmissions(encounters_df, patients_df):
    """Add realistic 30-day readmissions"""
    print("Adding readmissions...")
    
    # Get inpatient encounters only
    inpatient = encounters_df[encounters_df['encounter_type'] == 'Inpatient'].copy()
    
    # Select patients for readmission
    readmit_patients = random.sample(
        list(inpatient['patient_id'].unique()),
        k=int(len(inpatient['patient_id'].unique()) * READMISSION_RATE)
    )
    
    new_encounters = []
    encounter_id = encounters_df['encounter_id'].str.extract(r'(\d+)').astype(int).max()[0] + 1
    
    for patient_id in readmit_patients:
        # Get their last inpatient encounter
        patient_encounters = inpatient[inpatient['patient_id'] == patient_id]
        if len(patient_encounters) == 0:
            continue
            
        last_encounter = patient_encounters.iloc[-1]
        discharge_dt = pd.to_datetime(last_encounter['discharge_datetime'])
        
        # Create readmission within 30 days
        readmit_days = random.randint(5, 30)
        readmit_dt = discharge_dt + timedelta(days=readmit_days)
        
        # Don't create readmissions in the future
        if readmit_dt > datetime.now():
            continue
        
        los_hours = random.randint(24, 168)  # 1-7 days
        readmit_discharge = readmit_dt + timedelta(hours=los_hours)
        
        readmission = {
            'encounter_id': f'E{str(encounter_id).zfill(6)}',
            'patient_id': patient_id,
            'encounter_type': 'Inpatient',
            'admit_datetime': readmit_dt.strftime('%Y-%m-%d %H:%M:%S'),
            'discharge_datetime': readmit_discharge.strftime('%Y-%m-%d %H:%M:%S'),
            'department': random.choice(DEPARTMENTS),
            'primary_dx_code': last_encounter['primary_dx_code'],  # Often same diagnosis
            'discharge_disposition': random.choice(['Home', 'Home with Home Health', 'SNF'])
        }
        new_encounters.append(readmission)
        encounter_id += 1
    
    # Combine and return
    return pd.concat([encounters_df, pd.DataFrame(new_encounters)], ignore_index=True)

def generate_diagnoses(encounters_df):
    """Generate diagnosis records (1-4 per encounter)"""
    print("Generating diagnoses...")
    
    diagnoses = []
    diagnosis_id = 1
    
    for _, encounter in encounters_df.iterrows():
        encounter_id = encounter['encounter_id']
        primary_dx = encounter['primary_dx_code']
        
        # Primary diagnosis
        diagnoses.append({
            'diagnosis_id': f'D{str(diagnosis_id).zfill(6)}',
            'encounter_id': encounter_id,
            'icd10_code': primary_dx,
            'diagnosis_description': DIAGNOSES[primary_dx],
            'diagnosis_type': 'Primary',
            'diagnosis_sequence': 1
        })
        diagnosis_id += 1
        
        # Secondary diagnoses (1-3)
        num_secondary = random.randint(1, 3)
        other_diagnoses = [dx for dx in DIAGNOSES.keys() if dx != primary_dx]
        secondary_dx_codes = random.sample(other_diagnoses, min(num_secondary, len(other_diagnoses)))
        
        for seq, dx_code in enumerate(secondary_dx_codes, start=2):
            diagnoses.append({
                'diagnosis_id': f'D{str(diagnosis_id).zfill(6)}',
                'encounter_id': encounter_id,
                'icd10_code': dx_code,
                'diagnosis_description': DIAGNOSES[dx_code],
                'diagnosis_type': 'Secondary',
                'diagnosis_sequence': seq
            })
            diagnosis_id += 1
    
    return pd.DataFrame(diagnoses)

def generate_procedures(encounters_df):
    """Generate procedure records (0-5 per encounter)"""
    print("Generating procedures...")
    
    procedures = []
    procedure_id = 1
    
    for _, encounter in encounters_df.iterrows():
        encounter_id = encounter['encounter_id']
        admit_dt = pd.to_datetime(encounter['admit_datetime'])
        discharge_dt = pd.to_datetime(encounter['discharge_datetime'])
        
        # Number of procedures varies by encounter type
        if encounter['encounter_type'] == 'Inpatient':
            num_procedures = random.randint(2, 5)
        elif encounter['encounter_type'] == 'Emergency':
            num_procedures = random.randint(1, 3)
        elif encounter['encounter_type'] == 'Observation':
            num_procedures = random.randint(1, 4)
        else:  # Outpatient
            num_procedures = random.randint(0, 2)
        
        proc_codes = random.sample(list(PROCEDURES.keys()), 
                                   min(num_procedures, len(PROCEDURES)))
        
        for proc_code in proc_codes:
            # Procedure datetime between admit and discharge
            time_range = (discharge_dt - admit_dt).total_seconds()
            proc_offset = random.randint(0, int(time_range))
            proc_dt = admit_dt + timedelta(seconds=proc_offset)
            
            procedures.append({
                'procedure_id': f'P{str(procedure_id).zfill(6)}',
                'encounter_id': encounter_id,
                'procedure_code': proc_code,
                'procedure_description': PROCEDURES[proc_code],
                'procedure_datetime': proc_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'performing_provider': f'Dr. {random.choice(LAST_NAMES)}'
            })
            procedure_id += 1
    
    return pd.DataFrame(procedures)

def main():
    """Generate all sample data files"""
    print("=" * 60)
    print("Healthcare Sample Data Generator")
    print("=" * 60)
    
    # Generate data
    patients_df = generate_patients(NUM_PATIENTS)
    encounters_df = generate_encounters(patients_df)
    diagnoses_df = generate_diagnoses(encounters_df)
    procedures_df = generate_procedures(encounters_df)
    
    # Save to CSV
    output_dir = 'data/raw'
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print("\nSaving files...")
    patients_df.to_csv(f'{output_dir}/patients.csv', index=False)
    print(f"✓ Saved {len(patients_df)} patients to {output_dir}/patients.csv")
    
    encounters_df.to_csv(f'{output_dir}/encounters.csv', index=False)
    print(f"✓ Saved {len(encounters_df)} encounters to {output_dir}/encounters.csv")
    
    diagnoses_df.to_csv(f'{output_dir}/diagnoses.csv', index=False)
    print(f"✓ Saved {len(diagnoses_df)} diagnoses to {output_dir}/diagnoses.csv")
    
    procedures_df.to_csv(f'{output_dir}/procedures.csv', index=False)
    print(f"✓ Saved {len(procedures_df)} procedures to {output_dir}/procedures.csv")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Patients: {len(patients_df):,}")
    print(f"Total Encounters: {len(encounters_df):,}")
    print(f"Total Diagnoses: {len(diagnoses_df):,}")
    print(f"Total Procedures: {len(procedures_df):,}")
    print(f"\nAverage encounters per patient: {len(encounters_df)/len(patients_df):.2f}")
    
    # Encounter type breakdown
    print("\nEncounter Type Distribution:")
    print(encounters_df['encounter_type'].value_counts())
    
    # Calculate readmission rate
    inpatient = encounters_df[encounters_df['encounter_type'] == 'Inpatient'].copy()
    inpatient['admit_datetime'] = pd.to_datetime(inpatient['admit_datetime'])
    inpatient['discharge_datetime'] = pd.to_datetime(inpatient['discharge_datetime'])
    inpatient = inpatient.sort_values(['patient_id', 'admit_datetime'])
    
    inpatient['next_admit'] = inpatient.groupby('patient_id')['admit_datetime'].shift(-1)
    inpatient['days_to_next'] = (inpatient['next_admit'] - inpatient['discharge_datetime']).dt.days
    readmissions = len(inpatient[inpatient['days_to_next'] <= 30])
    
    print(f"\n30-day readmissions: {readmissions} ({readmissions/len(inpatient)*100:.1f}%)")
    print("\n" + "=" * 60)
    print("Data generation complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()