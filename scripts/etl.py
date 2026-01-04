import pandas as pd
import numpy as np
from typing import List, Dict, Any
from src.models import Invoice
from pydantic import ValidationError

class DataLoader:
    """
    Robust Data Loader & Cleaner pipeline.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.raw_data = None
        self.clean_data = None

    def load_raw_data(self) -> pd.DataFrame:
        """
        Loads raw CSV data.
        """
        try:
            # Optimize memory by specifying dtypes if dataset was huge, 
            # but for 17k rows, standard load is fine.
            self.raw_data = pd.read_csv(self.filepath)
            print(f"✅ Loaded {len(self.raw_data)} rows from {self.filepath}")
            return self.raw_data
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ File not found at {self.filepath}")

    def clean_and_validate(self) -> pd.DataFrame:
        """
        Cleans data and validates against Pydantic model.
        Returns a DataFrame of valid records.
        """
        if self.raw_data is None:
            self.load_raw_data()

        df = self.raw_data.copy()

        # 0. Ensure ID is string 
        # Pydantic expects str, but pandas infers int for numeric IDs
        df['id'] = df['id'].astype(str)

        # 1. Standardize Dates
        # The data contains " UTC" suffix which might confuse standard parsers.
        date_cols = ['issue_date', 'due_date', 'paid_on_date']
        for col in date_cols:
            # Ensure it's string first
            df[col] = df[col].astype(str).str.replace(' UTC', '', regex=False)
            # Replace 'nan' string back to real NaN/None before parsing if needed, 
            # but to_datetime handles nat-like strings.
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # 2. Logic Corrections
        df['amount_due'] = df['amount_due'].fillna(0)
        
        # 3. Pydantic Validation Loop
        valid_records = []
        errors = []

        records = df.to_dict(orient='records')
        
        for record in records:
            # Handle NaT for Pydantic (convert to None)
            for col in date_cols:
                if pd.isna(record[col]):
                    record[col] = None
            
            try:
                # Validate
                invoice = Invoice(**record)
                valid_records.append(invoice.model_dump())
            except ValidationError as e:
                errors.append({'id': record.get('id', 'unknown'), 'error': str(e)})

        if errors:
            print(f"⚠️ warning: {len(errors)} records failed validation and were excluded.")
            if len(errors) > 0:
                print(f"Sample error: {errors[0]}")
        
        if not valid_records:
            raise ValueError(f"❌ CRITICAL: No valid records found! All {len(df)} rows failed validation. Check date formats.")

        # Reconstruct DataFrame from validated objects
        self.clean_data = pd.DataFrame(valid_records)
        
        # Post-Validation Feature Engineering
        self._add_derived_features()
        
        print(f"✅ Data Cleaned & Validated. {len(self.clean_data)} valid rows ready.")
        return self.clean_data

    def _add_derived_features(self):
        """
        Adds useful columns for analysis.
        """
        df = self.clean_data
        
        # Payment Status
        # If paid_on_date exists, it's paid. 
        # If not, checks if today > due_date (Overdue) or not (Open).
        # Note: In a real scenario, "today" might be relative to the dataset snapshot.
        # We will assume a reference date of the max(issue_date) + small buffer or today.
        
        reference_date = df['issue_date'].max()
        
        conditions = [
            (df['paid_on_date'].notna()),
            (df['paid_on_date'].isna()) & (df['due_date'] < reference_date),
            (df['paid_on_date'].isna()) & (df['due_date'] >= reference_date)
        ]
        choices = ['Paid', 'Overdue', 'Open']
        
        df['status'] = np.select(conditions, choices, default='Unknown')
        
        # Days Late calculation
        # If paid: paid_date - due_date
        # If unpaid: reference_date - due_date
        
        df['effective_date'] = df['paid_on_date'].fillna(reference_date)
        df['days_late'] = (df['effective_date'] - df['due_date']).dt.days
        
        # Late Category
        df['late_bucket'] = pd.cut(
            df['days_late'], 
            bins=[-9999, 0, 15, 30, 60, 90, 9999],
            labels=['On Time', '1-15 Days', '16-30 Days', '31-60 Days', '61-90 Days', '90+ Days']
        )

if __name__ == "__main__":
    # Test run
    loader = DataLoader("data/data.csv")
    cleaned_df = loader.clean_and_validate()
    print(cleaned_df.head())
    print(cleaned_df['status'].value_counts())
